from fastapi import FastAPI
from fastapi.responses import JSONResponse
from models import AskRequest

import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger=logging.getLogger(__name__)


app=FastAPI()
@app.get("/health")
async def health():
    return {"status":"OK"}

@app.get("/")
async def root():
    return {"message":"tutor-quality service running"}

@app.post("/ask")
async def ask(req: AskRequest):
    logger.info(f"收到问题：{req.question!r}")
    if req.question.strip() == "":
        logger.warning("问题为空，已拦截。")
        return JSONResponse(status_code=400, content={"error": "question不能为空"})
    logger.info("返回结果：这是硬编码的答疑结果。")
    return {"answer": "这是硬编码的答疑结果", "question": req.question}


@app.get("/history")
async def history():
    logger.info("查询历史记录")
    return []
