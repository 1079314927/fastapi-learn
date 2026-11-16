# 项目架构说明

## 一、分层图

```
调用方（浏览器 / 测试脚本）
  │  HTTP 请求
  ▼
路由层   service/main.py
  │  调用
  ▼
服务层   service/service.py        ← 待建，逻辑暂时还在 main.py
  │  读写
  ▼
数据层   MySQL 库 tutor_ai（service/database.py）
        表 questions / ask_logs（service/models.py 映射）
```

## 二、每层职责

**路由层（service/main.py）**
负责：收请求、校验参数、把结果打包回话。
不负责：算答案、存数据。

**服务层（service/service.py，待建）**
负责：算逻辑——拼答案、走判断、以后调 AI 模型。
不负责：收请求（它不知道 HTTP 长什么样）。

**数据层（MySQL + SQLAlchemy，已接入）**
负责：存和取——把 Python 对象变成表里的行，把查询结果变回对象。
现状：库 `tutor_ai`（utf8mb4），两张表：

- `questions`（题库，5 条）：`id` / `question` / `knowledge_point` / `steps` / `common_mistake` / `created_at`
- `ask_logs`（提问记录）：`id` / `question` / `matched` / `created_at`

连接配置在 `service/database.py`（`engine` + `SessionLocal`，密码读环境变量 `DB_PASSWORD`），表结构的 Python 写法在 `service/models.py`（`Base` / `Question` / `AskLog`）。

查询路径：

- `POST /ask` → `query(Question).filter(contains(keyword)).first()` 拿答案，再 `add(AskLog(...))` + `commit()` 落一条记录
- `GET /history` → `query(AskLog).order_by(created_at.desc()).limit(20).all()` 取最近 20 条

每次请求的会话由 `get_db()` 借出、`finally` 归还（`yield` + `Depends`）。

## 三、为什么不都写在 main.py

1. 改动隔离：改 /ask 不会碰坏 /health
2. 能单独测：算答案那步不用起服务器就能验证
3. 换实现只改一处：答案从硬编码换成调 AI，只动服务层
