from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import os


DATABASE_URL = f"mysql+pymysql://root:{os.getenv('DB_PASSWORD')}@localhost:3306/tutor_ai?charset=utf8mb4"
# 连库的地址，`+pymysql` 是驱动，`tutor_ai` 是建好的库。

engine=create_engine(DATABASE_URL,
                     echo=True,
                     connect_args={"connect_timeout":5},
                     pool_timeout=5
                     )
# engine：总管。`echo=True` 的意思是它发的每条 SQL 都打印到终端，学习时很有用，能看到 ORM 到底在背后干了什么。

SessionLocal=sessionmaker(bind=engine,autoflush=False)
# 会话工厂
# `autoflush` = “查询前自动把你攒着的改动先发给数据库”。

# 你的代码 → SQLAlchemy 引擎 → pymysql 驱动 → 3306 端口 → MySQL 认证 → tutor_ai 库
# & 'D:\anaconda\envs\fastapi_learn\python.exe' 
# -c "from sqlalchemy import text; 
# from database import engine;
#  print(engine.connect().execute(text('SELECT 1')).scalar())"
