from fastapi import FastAPI
from fastapi.responses import JSONResponse
from models import AskRequest
app=FastAPI()
@app.get("/health")
async def health():
    return {"status":"OK"}

@app.get("/")
async def root():
    return {"message":"tutor-quality service running"}

@app.post("/ask")
async def ask(req: AskRequest):
    if req.question.strip() == "":
        return JSONResponse(status_code=400, content={"error": "question不能为空"})
    return {"answer": "这是硬编码的答疑结果", "question": req.question}
