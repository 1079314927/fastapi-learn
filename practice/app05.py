from fastapi import FastAPI,Path

#参数：路径参数、查询参数、请求体

#路径参数 位置：URL路径的一部分 作用：指向唯一、特性的资源 方法：GET
app=FastAPI()

@app.get("/book/{id}")
async def get_book(id:int=Path(...,gt=0,lt=101,description="书籍编号，取值范围是1-100")):#跟路径参数同名的形参
    return {"id":id, "title":f"这是第{id}本书"}

#查询参数 位置URL？之后 作用：对资源集合进行过滤、排序、分页等操作 方法：GET
