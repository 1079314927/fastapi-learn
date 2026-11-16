from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse
from models import AskLog, AskRequest, Question
from sqlalchemy.orm import Session
from database import SessionLocal

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
@app.get("/health")
async def health():
    return {"status":"OK"}

@app.get("/")
async def root():
    return {"message":"tutor-quality service running"}

@app.post("/ask")
async def ask(req: AskRequest,db:Session=Depends(get_db)):
    logger.info(f"收到问题：{req.question!r}")
    if req.question.strip() == "":
        logger.warning("问题为空，已拦截。")
        return JSONResponse(status_code=400, content={"error": "question不能为空"})


    keyword=req.question.strip()
    row=db.query(Question).filter(Question.question.contains(keyword)).first()
    matched = row is not None

    db.add(AskLog(question=req.question,matched=matched))
    db.commit()

    if row is None:
        logger.info("题库未匹配，返回暂未收录。")
        return {"answer":"题库暂未收录该题","matched":False}

    logger.info(f"匹配到题库 id={row.id}")
    return {
        "answer":row.steps,
        "common_mistake":row.common_mistake,
        "matched":True,
        "question":row.question,

        }



@app.get("/history")
async def history():
    logger.info("查询历史记录")
    return []
