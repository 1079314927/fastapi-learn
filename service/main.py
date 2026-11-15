from fastapi import FastAPI
app=FastAPI()
@app.get("/health")
async def health():
    return {"status":"OK"}

@app.get("/")
async def root():
    return {"message":"tutor-quality service running"}