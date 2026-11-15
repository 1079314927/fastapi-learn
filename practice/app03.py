from fastapi import FastAPI

#创建API实例
app=FastAPI()

@app.get("/")
async def root():
    return{"message":"Hello,world!"}
#路由指的是用这个装饰器登记出来的规则
#有人使用get（HTTP方法）请求/，就执行接下来的函数

@app.get("/hello/{name}")
async def say_hello(name:str):
    return {"message":f"Hello,{name}!"}

#路由练习：访问/hello 响应结果： msg：你好 FastAPI

@app.get("/hello")
async def get_hello1():
    return {"msg":"你好 FastAPI!"}

#路由练习
@app.get("/user/hello")
async def say_hello():
    return {"msg":"我正在学习 FastAPI……"}