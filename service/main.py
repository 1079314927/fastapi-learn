from fastapi import Depends, FastAPI, Header
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from models import AskLog, AskRequest, Question
from database import SessionLocal
from retry import retry_call

import json
import time
import uuid
import logging



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger=logging.getLogger(__name__)


def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()

app=FastAPI()

_CACHE:dict[str,dict]={}
@app.get("/health")
async def health():
    return {"status":"OK"}

@app.get("/")
async def root():
    return {"message":"tutor-quality service running"}



@app.post("/ask")
async def ask(req: AskRequest,db:Session=Depends(get_db),
              x_request_id:str|None=Header(default=None,alias="X-Request-ID")):
    start=time.perf_counter()
    request_id = x_request_id or uuid.uuid4().hex
    logger.info(json.dumps({"msg": "收到问题", "request_id": request_id,
                            "path": "/ask", "method": "POST",
                            "question": req.question}, ensure_ascii=False))
    if req.question.strip() == "":
        logger.warning(json.dumps({"msg": "问题为空，已拦截", "request_id": request_id,
                                   "path": "/ask", "method": "POST",
                                   "duration_ms": round((time.perf_counter()-start)*1000, 1),
                                   "status": "bad_request"}, ensure_ascii=False))
        return JSONResponse(status_code=400, content={"error": "question不能为空"})

    if request_id in _CACHE:
        logger.info(json.dumps({"msg": "命中幂等，直接返回上次结果", "request_id": request_id,
                                "path": "/ask", "method": "POST",
                                "duration_ms": round((time.perf_counter()-start)*1000, 1),
                                "status": "idempotent_hit"}, ensure_ascii=False))
        return _CACHE[request_id]


    keyword=req.question.strip()
    def do_query():
        return db.query(Question).filter(Question.question.contains(keyword)).first()
    row=retry_call(do_query)
    
    matched = row is not None

    db.add(AskLog(question=req.question,matched=matched,request_id=request_id))
    db.commit()

    if row is None:
        logger.info(json.dumps({"msg": "题库未匹配，返回暂未收录", "request_id": request_id,
                                "path": "/ask", "method": "POST",
                                "duration_ms": round((time.perf_counter()-start)*1000, 1),
                                "status": "unmatched"}, ensure_ascii=False))
        resp={"answer":"题库暂未收录该题","matched":False}
        _CACHE[request_id]=resp
        return resp

    logger.info(json.dumps({"msg":"匹配到题库","request_id":request_id,
                            "path":"/ask","method":"POST",
                            "duration_ms":round((time.perf_counter()-start)*1000,1),
                            "status":"matched","question_id": row.id},ensure_ascii=False))
    resp={
        "answer":row.steps,
        "common_mistake":row.common_mistake,
        "matched":True,
        "question":row.question,

        }
    _CACHE[request_id]=resp
    return resp



@app.get("/history")
async def history(db:Session=Depends(get_db),x_request_id:str|None=Header(default=None,alias="X-Request-ID")):
    start = time.perf_counter()
    request_id=x_request_id or uuid.uuid4().hex

    try:
        rows=(
            db.query(AskLog).order_by(AskLog.created_at.desc()).limit(20).all()
        )
    except Exception as exc:
        logger.error(json.dumps({"msg": "查询历史失败，数据库不可用", "request_id": request_id,
                                 "path": "/history", "method": "GET",
                                 "duration_ms": round((time.perf_counter()-start)*1000, 1),
                                 "status": "db_error", "error": str(exc)}, ensure_ascii=False))
        return JSONResponse(status_code=500, content={"error": "数据库不可用"})

    logger.info(json.dumps({"msg": "查询历史记录：最近20条", "request_id": request_id,
                            "path": "/history", "method": "GET", "count": len(rows),
                            "duration_ms": round((time.perf_counter()-start)*1000, 1),
                            "status": "ok"}, ensure_ascii=False))

    return [
        {"id":r.id, "question":r.question, "matched":r.matched, "created_at":r.created_at}
        for r in rows
    ]
