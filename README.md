# 初中数学答疑服务

[![tests](https://github.com/1079314927/fastapi-learn/actions/workflows/test.yml/badge.svg)](https://github.com/1079314927/fastapi-learn/actions/workflows/test.yml)

给初中数学家教用的答疑后端：学生发来题目，服务匹配同类题、返回解题步骤和常见错因，每次提问都留痕可追溯，为后续评测 AI 回答做准备。当前只覆盖题库内 5 道题，不接大模型，不判断学生答案对错。

## 为什么做这个

AI 家教最麻烦的地方不是答不出来，是**答错了没人知道**——同一个问题问两次措辞不一样，答案可能更好也可能更差，事后还查不到当时到底说了什么。

所以第一阶段先不接模型，把"能记录、能复现、能评测"的底座搭起来：三条接口、提问落库、25 条自动化用例、每次 push 自动跑。题库和接口现在都是最小形态，第二阶段才往上面挂评测层——**这是设计选择，不是没做完**。

## 跑一次看效果

三条接口：`POST /ask` 匹配题库（命中返回解题步骤和常见错因）；`GET /history` 取最近 20 条提问记录；`GET /health` 只探活、不碰数据库。

下面这条命令带了 `X-Request-ID: demo-001`，是为了演示幂等：同一个 ID 再发一次，返回完全相同的结果，库里也只留一条记录。

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -H "X-Request-ID: demo-001" \
  -d '{"question":"直角三角形两条直角边为 6、8，求斜边；若斜边为 13、一条直角边为 5，求另一条直角边"}'
```

```json
{
  "answer": "1. 第一问：6²+8²=36+64=100，斜边 = √100 = 10\n2. 第二问：13²-5²=169-25=144，另一直角边 = √144 = 12",
  "common_mistake": "把斜边当直角边代进 a²+b²=c²；开方后只写负数解或漏写单位",
  "matched": true,
  "question": "直角三角形两条直角边为 6、8，求斜边；若斜边为 13、一条直角边为 5，求另一条直角边"
}
```

`answer` 是题库 `steps` 那一列的原文照搬，不是模型生成的——这一版还没有模型。

> PowerShell 里没有 `curl`（那是 `Invoke-WebRequest` 的别名），要写 `curl.exe`；反斜杠续行在 PowerShell 里不成立，请把整条命令拼成一行。

题库里没有对应的题时走另一条路：

```json
{
  "answer": "题库暂未收录该题",
  "matched": false
}
```

只返回这两个键，`common_mistake` 和 `question` 都不出现。空输入或纯空格则直接返回 400。

## 怎么跑起来

需要 Python 3.12 和 MySQL 8。建议在自己的环境里跑，别装进系统 Python：

```bash
conda activate fastapi_learn
```

以下命令**都在仓库根目录下执行**：

```bash
pip install -r requirements.txt        # requirements.txt 就在仓库根

export DB_PASSWORD=你的密码             # PowerShell: $env:DB_PASSWORD="你的密码"

cd service
python init_db.py                      # 无输出即成功，库里多出 questions / ask_logs 两张表
python seed.py                         # 输出：插入完成 5 条
uvicorn main:app --reload              # 监听 http://127.0.0.1:8000
```

再开一个终端，**回到仓库根目录**（不是 `service/`）跑测试：

```bash
python -m pytest tests -q -p no:cacheprovider
```

预期：`25 passed`。

| 报错 | 原因 |
|---|---|
| `ModuleNotFoundError: No module named 'service'` | 不在仓库根跑 pytest，或把 `python -m` 省掉了 |
| `(1045, "Access denied")` | `DB_PASSWORD` 没设或不对 |
| `(2003, "Can't connect")` | MySQL 没起，或端口 / 主机名写错 |
| 终端刷满 SQL 语句 | 正常。`engine` 开了 `echo=True`，学习期故意留着 |

> PowerShell 5.1 不支持 `&&`，上面命令请一行一行敲。

## 怎么保证它是对的

25 条用例，8 个文件：`health` 2 条、正常匹配 4 条、缺参 3 条、非法输入 4 条、边界值 4 条、服务异常 3 条、幂等 3 条，加 2 条纯单元（`is_retryable` 的判定表、`retry_call` 的重试次数）。

服务异常那 3 条不是 mock 出来的：另起一个 8001 端口的服务、把 `DB_PASSWORD` 改成错的，用真库返回的 1045 来验证"立刻失败、不在 500 之上再重试"。

`.github/workflows/test.yml`，push 到 main 和发起 PR 时触发，打 tag 不触发。跑在 `ubuntu-latest` 上，每次全新分配、跑完销毁；配一个 `mysql:8` 的 service 容器，用容器内 `mysqladmin ping` 做健康检查。

八步：checkout → setup-python 3.12 → 装依赖 → 真连一次库 → `init_db.py` 建表 → `seed.py` 灌数据 → `python -m pytest` → 上传 `report/` 作为 artifact（`if: always()`，红了也传）。

**这个 workflow 不是一直绿的。** 第 19 天连续跑了七次：三次真红、一次故意红、三次全绿。

| 提交 | 结果 | 暴露了什么 |
|---|---|---|
| `345e5f4` | 红 | 本地三个提交没 push，CI 上 `requirements.txt` 直接 404 |
| `78eaaae` | 红 | `/history` 裸奔，接住了 `/ask` 抛 500 时废掉的那条连接，报 `ConnectionResetError` |
| `b5f1e0e` | 红 | try/except 加在了 `/history`，守错了门——要守的是 `/ask` |
| `5c3d922` | 绿 | 改成在 `/ask` 里显式返回 500 |
| `2daf29f` | 绿 | 加这枚徽章 |
| `bde904b` | 红（故意） | 把 `==200` 改成 `==201`，验证用例真的会拦住 |
| `e292883` | 绿 | 改回来 |

七次的日志都还留在 Actions 的运行列表里，从徽章点进去就能翻到。

## 技术决策

**超时定 5 秒，不是 30 秒。** `connect_timeout=5`、`pool_timeout=5`。这两个都是**连接层**的等待，和表有多大无关——库没起、网络卡顿、连接池被占满，都会卡在这一步。5 秒是内网服务的常规量级；设 30 秒的代价是一个卡死的请求会把 worker 占住半分钟。
*代价*：当前数据量下还没真触发过，这个值是按经验定的，不是压出来的。

**只重试 2003 / 2006 / 2013，1045 立刻失败。** `retry_call` 最多重试 2 次（合计 3 次尝试），间隔 0.5 秒，另外把连接池超时也算进可重试。前三个是连接层的临时故障（连不上、连接断了、连接超时），换条连接有救；1045 是密码错，重试三次只是把同一个错误犯三遍，还拖慢响应。
*代价*：白名单必然会漏，只能靠把连接池超时补进来兜一部分。

**幂等做两层，不是一层。** 进程内 `_CACHE` 挡重复（快，不查库）；`ask_logs.request_id` 唯一索引挡重启和多进程之后的重复（真）。只留前者，重启就失忆；只留后者，每次重复请求都要撞一次数据库约束。
*代价*：`_CACHE` 不跨进程，多 worker 部署时它只算加速，不算保证。

**必须 `python -m pytest`，不能裸 `pytest`。** `-m` 决定 `sys.path[0]` 是当前目录还是 `Scripts\`，`conftest.py` 里 `from service.database import ...` 靠的就是前者。裸 `pytest` 直接 `ModuleNotFoundError`，而且报错长得很不像路径问题。

## 分层与数据流

```
调用方（浏览器 / Swagger / 测试脚本 / CI）
   │  HTTP
   ▼
路由层  main.py —— 参数校验 / 幂等检查 / 异常兜底        ┐
   │                                                    │ 日志层
   ▼                                                    │ 结构化输出
服务层  题库匹配与格式化（现仍在 main.py 内，待拆出）      │ request_id
   │                                                    │ 路径 / 耗时
   ▼                                                    │ 状态
数据层  models.py + database.py —— ORM / 连接池 / 超时 / 重试┘
   │
   ▼
MySQL  tutor_ai
       ├ questions   题库 5 条：question / knowledge_point / steps / common_mistake
       └ ask_logs    提问记录：question / matched / request_id（唯一索引）
```

图上那一层"服务层"目前还和路由层合在 `main.py` 里，拆分是下一步的第一件事。

## 已知限制

- **匹配只做单边 `contains`**：只查 `questions.question` 一列，`knowledge_point` 里的词匹配不到；问题比题库原文长也匹配不到
- **`connect_timeout` 未在接口层验证**：host/port 硬编码，造不出"连接建立阶段超时"的局面，这段只有单元测试覆盖
- **单元测试会多连一次库**：继承了 conftest 的 autouse 清库 fixture，属于已知冗余，升级条件写在 `docs/test-design.md`
- **依赖未锁版本**：`requirements.txt` 只写包名不写版本，上游大版本升级可能改变行为

## 下一步

分两条线走。

**先补工程欠账**：把匹配逻辑从 `main.py` 拆到独立的服务层（让图里那层变成真的）、锁住依赖版本。

**再开评测层**：计划 6 个维度——知识点正确性、步骤一致性、超纲检测、分层讲解匹配、多轮对话稳定性、幻觉率——加一个最小可用的 LLM-as-Judge 脚本，用仓库里真实的失败用例和误判记录作佐证。**先只做前两个维度跑通，其余边跑边补。本阶段评测层零实现。**

## 维护

个人项目，维护者是我（[@1079314927](https://github.com/1079314927)）。发现问题直接提 Issue。

更多细节在 `docs/`：`architecture.md`（分层）、`resilience.md`（超时与重试）、`test-design.md`（用例设计与降级）、`day1-notes.md`（每日复盘，含踩坑过程）。

