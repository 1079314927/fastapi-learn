from datetime import datetime


from pydantic import BaseModel
from sqlalchemy import DateTime, Integer, String, Text, func,Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class AskRequest(BaseModel):
    question:str


class Base(DeclarativeBase):
    pass

class Question(Base):
    __tablename__="questions"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    question:Mapped[str]=mapped_column(Text,nullable=False)
    knowledge_point:Mapped[str|None]=mapped_column(String(100))
    steps:Mapped[str|None]=mapped_column(Text)
    common_mistake:Mapped[str|None]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime, server_default=func.now())

class AskLog(Base):
    __tablename__="ask_logs"
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True)
    question:Mapped[str]=mapped_column(Text,nullable=False)
    matched:Mapped[bool]=mapped_column(Boolean,nullable=False)
    created_at:Mapped[datetime]=mapped_column(DateTime,server_default=func.now())
    request_id:Mapped[str|None]=mapped_column(String(64),unique=True)