# 容错设计记录

本文件记录项目的三道工程护栏：**超时、重试、幂等**。每一条都写清：配了什么、为什么是这个值、不设会怎样。

---

## 一、超时（Day 9）

### 配置在哪

`service/database.py` 的 `create_engine`：

```python
engine = create_engine(
    DATABASE_URL,
    echo=True,
    connect_args={"connect_timeout": 5},
    pool_timeout=5,
)
```

### 两个参数分工

| 参数 | 管什么 | 单位 | 本项目值 |
|---|---|---|---|
| `connect_args={"connect_timeout": 5}` | **建立连接**最多等几秒（TCP 连上、MySQL 应答认证） | 秒 | 5 |
| `pool_timeout=5` | **从连接池借一个已有连接**最多等几秒（池子被占满时排队） | 秒 | 5 |

一个是"连不上"，一个是"排不上队"。只设前一个，会在池子耗尽时无限排队；只设后一个，会在数据库没响应时卡死第一条连接。

### 为什么是 5 秒

- 本地 MySQL 正常建连在 **50 ms 量级**（Day 8 实测首次查询 49.9 ms 里就含建连），5 秒是它的 100 倍，正常情况绝不会误伤
- 用户体感上，一个请求等超过 5 秒基本已经算"卡住"了，再等只会让人以为服务死了
- 本阶段是本地单机项目，不需要照顾跨机房高延迟，5 秒足够宽

上线到远端数据库、或网络质量差时，这个值要按实际 RTT 重新评估（通常设 RTT 的 3—5 倍）。

### 不设会怎样

1. **请求堆积**：数据库没响应时，请求会一直挂到操作系统的 TCP 超时（可能几十秒到两分钟），这期间连接和线程都被占着
2. **连接池耗尽**：`QueuePool` 能同时开的连接数是 `pool_size`（默认 **5**）+ `max_overflow`（默认 **10**）= **最多 15 个**（已实测 `pool.size()==5`、`_max_overflow==10`）。前 5 个是常驻连接，第 6—15 个是临时"溢出连接"，用完就关。**真正开始排队的是第 16 个请求**。`pool_timeout` 管的就是这段排队时间：等满就抛 `TimeoutError`。若 `pool_timeout` 不设（默认 30 秒），现象是"服务不报错、请求卡半分钟"；若把 `max_overflow` 设成 0，第 6 个就开始排队。
3. **故障放大**：一个小抖动会被拖成全站不可用

### 实测记录（2026-11-17）

用临时脚本各建一个 engine（`connect_timeout=2`），量从发起连接到抛错的耗时：

| 目标 | 耗时 | 异常 | 原因 |
|---|---|---|---|
| `10.255.255.1`（黑洞地址，无人应答） | **2.05 秒** | `OperationalError` | `(2003, "Can't connect to MySQL server on '10.255.255.1' (timed out)")` |
| `127.0.0.1`（真实本机，密码故意写错） | **0.02 秒** | `OperationalError` | `(1045, "Access denied for user 'root'@'localhost'")` |
| 池子占满（`pool_size=5, max_overflow=0, pool_timeout=2`，第 6 个连接） | **2.01 秒** | `TimeoutError` | `QueuePool limit of size 5 overflow 0 reached, connection timed out, timeout 2.00` |

结论：**"对面没反应"会等满超时上限才放弃；"对面明确拒绝"是立刻失败**，两者不是一回事，超时只治前一种。

另外核验过：`engine.pool._timeout == 5`，池类型 `QueuePool`、容量 5；`SELECT 1` 返回 1，说明加了参数不影响正常连库。

### 这一条要记住的结论

**超时解决的是"等太久"，不是"失败"。** 超时之后，这个请求仍然是失败的——只是失败得早、失败得干净。它不替你决定接下来怎么办：**要么重试（Day 10），要么直接把错误报给调用方**。这是两道分开的功课，超时只做前半道。

### 接口层端到端实测（2026-11-17）

引擎层和池层都量过了，但清单第 2 项要的是**接口层**：数据库连不上时，`/ask` 到底是卡死还是按时返回 5xx。

难点还是那个：`DATABASE_URL` 里主机写死 `localhost`，要造故障就得改文件、再改回来。这次的办法是**在程序启动前把 `database.SessionLocal` 换掉**（monkey patch），仓库代码一个字没动。临时模块放在 `%TEMP%\badbeprobe\`，测完连目录一起删：

```python
import sys
sys.path.insert(0, r"D:\Code\fastapi-learn\service")

import database                                        # 先载入（此时 SessionLocal 指向 localhost）

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

bad_engine = create_engine(
    "mysql+pymysql://root:x@10.255.255.1:3306/tutor_ai?charset=utf8mb4",
    connect_args={"connect_timeout": 5},
)
database.SessionLocal = sessionmaker(bind=bad_engine, autoflush=False)   # 换路标

from main import app                                   # 最后才导入 main
```

`main.py` 里是 `from database import SessionLocal`，所以 **`import main` 必须排在换路标之后**，否则 `main` 拿到的是旧的那个。

结果（服务起在 8001）：

| 请求 | 状态码 | 耗时 |
|---|---|---|
| `POST /ask`（库指向黑洞） | **500** | **5.13 秒** |
| `GET /health`（同时发，不碰库） | **200** | **0.037 秒** |

服务端日志：

```text
sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (2003, "Can't connect to MySQL server on '10.255.255.1' (timed out)")
```

三条结论：

1. **超时配置确实在接口层生效**：请求没有挂死，5 秒左右变成 500
2. **一个接口卡住不等于全站卡住**：`/health` 同时仍然 0.037 秒返回，因为它不碰数据库
3. **失败得干净**：500 是明确信号，调用方立刻能知道该重试还是放弃

---

## 二、重试（Day 10）

### 配置在哪

`service/retry.py`（Day 10 新建）：

```python
import logging
import time

from sqlalchemy.exc import OperationalError, TimeoutError as PoolTimeout

logger = logging.getLogger(__name__)

RETRYABLE_CODES = {2003, 2006, 2013}

def is_retryable(exc):
    if isinstance(exc, PoolTimeout):
        return True
    if isinstance(exc, OperationalError) and exc.orig is not None:
        return exc.orig.args[0] in RETRYABLE_CODES
    return False

def retry_call(fn, max_retries=2, delay=0.5):
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as exc:
            if not is_retryable(exc):
                logger.error("不是可重试异常，立刻上抛：%s", exc)
                raise
            if attempt == max_retries:
                logger.error("最终失败：已重试%d次，放弃", max_retries)
                raise
            logger.warning("第%d次重试（原因：%s），%.1f秒以后再试", attempt + 1, exc, delay)
            time.sleep(delay)
```

`/ask` 里这样接入（`main.py`）：

```python
    keyword = req.question.strip()

    def do_query():
        return db.query(Question).filter(Question.question.contains(keyword)).first()

    row = retry_call(do_query)
```

`do_query` 写在 `ask` 里面，是为了让它直接借用外层的 `db` 和 `keyword`——这样 `retry_call` 保持最简形态（只接受一个不带参数的函数）。放到模块级就得给 `retry_call` 加 `*args` 转发参数，那是 pytest 那一批再做的事。

### 两个函数分工

| 函数 | 管什么 |
|---|---|
| `is_retryable(exc)` | **判断这次错误值不值得再试一次**（纯判断，不动手） |
| `retry_call(fn, ...)` | **按次数和间隔真的去重复执行**（动手的那个） |

拆成两个的好处：判断逻辑能单独测、单独调，以后改策略只改一处。

### 哪些错误重试，哪些不重试

| 错误码 | 含义 | 重试？ | 为什么 |
|---|---|---|---|
| **2003** | 连不上服务器（超时 / 被拒绝） | ✅ | 网络抖动、数据库重启，过一会儿可能就好了 |
| **2006** | 服务端把连接踢了（gone away） | ✅ | 连接被中间设备或服务端回收，重拿一条新连接可能就正常 |
| **2013** | 查询做到一半连接断了（lost connection） | ✅ | 是"连接断了"，不是"语句错了" |
| 其它错误码 | — | ❌ | 认不出来就别乱试 |
| **1045** | 密码错 Access denied | ❌ | 密码不会因为等两秒就变对 |
| **1049** | 库不存在 Unknown database | ❌ | 名字写错，重试一万次也还是不存在 |
| **1064** | SQL 语法错 | ❌ | 代码写错了，重试只会重复犯错 |
| **`PoolTimeout`**（SQLAlchemy 池超时） | 池子被占满，排队排不上 | ✅ | 只是"那一刻忙"，等一会儿池子会空出来 |

`PoolTimeout` 是 `sqlalchemy.exc.TimeoutError` 的别名。**它和 Python 内置的 `TimeoutError` 没有任何继承关系**，`except TimeoutError` 抓不到池超时——所以必须显式 import SQLAlchemy 那个，并起别名避免撞名。

### 为什么是 2 次 / 0.5 秒

- **2 次**：一次重试只是"碰运气"，两次能覆盖"数据库重启 / 网络闪断"这类秒级抖动；再多就是拿用户时间赌运气
- **0.5 秒**：MySQL 重启、连接回收通常在 1 秒内恢复，0.5 秒间隔足够错开；间隔再长，用户等得更久
- **不做指数退避**：本阶段是本地单机 + 单实例，2 次 × 0.5 秒的固定间隔够用；指数退避（0.5s、1s、2s…）是以后真遇到"服务端被重试打垮"才需要的

### 为什么不无限重试

**重试把"单次等待"乘上尝试次数。** 实测数据（见下）：

| 单次尝试 | 尝试次数 | 用户实际等待 |
|---|---|---|
| 4.1 秒（连接被拒，Windows 上试 IPv6 + IPv4） | 3 次 + 2 次 sleep | **13.26 秒** |
| 5 秒（黑洞地址，`connect_timeout=5`） | 3 次 + 2 次 sleep | **约 16 秒** |

还有更关键的一条：**数据库真挂了时，每个重试中的请求都继续占着连接池和线程。** 并发一高，重试会把"一个服务慢"放大成"整个服务被自己的重试压垮"（雪崩）。次数和间隔就是这道阀门。

### 实测记录（2026-11-17）

**判定层：**

| 输入 | `is_retryable` | 期望 |
|---|---|---|
| `OperationalError (2003, timed out)` | **True** | 可重试 |
| `OperationalError (1045, Access denied)` | **False** | 不可重试 |

**正常路径（库正常）：**

| 请求 | 结果 |
|---|---|
| `POST /ask`（"直角三角形"） | **200，173.5 ms**，匹配到题库答案；日志里**没有**"重试"字样 |
| `GET /history` | **200，11.7 ms** |

**故障路径（把库端口改成没监听的 3307）：**

| 时间（本机日志） | 日志内容 |
|---|---|
| 17:31:38.908 | 收到问题 |
| **17:31:43.000** | `[WARNING] 第1次重试（原因：(2003, ... [WinError 10061] 由于目标计算机积极拒绝，无法连接。)），0.5秒以后再试` |
| **17:31:47.575** | `[WARNING] 第2次重试（原因：同上）` |
| **17:31:52.163** | `[ERROR] 最终失败：已重试2次，放弃` |
| 同上 | `POST /ask HTTP/1.1" 500 Internal Server Error` |

**总耗时 13.26 秒**（38.908 → 52.163），拆开正好三段：

```text
3 次尝试 × 约 4.1 秒  ≈ 12.3 秒
2 次间隔 × 0.5 秒     =  1.0 秒
合计                  ≈ 13.3 秒
```

一次尝试 4.1 秒，**不是 `connect_timeout=5` 起了作用**——"积极拒绝"本该立刻返回。实测直连 `localhost:3307` 单次要 **2.06 秒**（Windows 会先后试 IPv6 `::1` 和 IPv4 `127.0.0.1`），pymysql 两个地址都试，于是变成 4 秒。

**这条实测顺带说明：超时和重试是叠加的。** 用户等的时间 = 尝试次数 × 单次耗时 + 间隔总和。

### 这一条要记住的结论

**重试解决的是"瞬时故障"，不是"持续故障"。** 数据库真挂了、密码真错了，重试只会把 5 秒变成 16 秒——它买的是"抖动一次能自愈"，不是"挂了也能救"。

三个必须想清楚的问题：

1. **值不值得重试**——按错误码判断，认不出来的一律不重试
2. **重试几次、隔多久**——次数乘单次耗时就是用户的等待上限
3. **被重试的动作是否"可重复执行"**——读操作随便重试；写操作重复执行会产生重复数据，那是 Day 11 幂等要管的事

### 还没做的一步（记录在案）

- **没有单元测试**：`is_retryable` 和 `retry_call` 目前只靠手工构造异常验证，下一批 pytest 补用例
- **没有区分读 / 写**：现在只包了 `/ask` 的查询动作；将来有写库动作时，重试要配合幂等键
- **没有退避和随机抖动**：固定 0.5 秒，多实例并发时重试节奏会同步（thundering herd），本阶段单实例可忽略

## 三、幂等（Day 11）

前两条解决"等太久"和"抖一下"。第三条解决另一个问题：**同一个请求被重复发了**——用户手抖点了两次提交、前端超时后自己重发、网络层重传。没有幂等，一次业务会被执行三遍，落三条记录。

### 配置在哪

**① 接口签名：接一个可选的请求头**

```python
@app.post("/ask")
async def ask(req: AskRequest, db: Session = Depends(get_db),
              x_request_id: str | None = Header(default=None, alias="X-Request-ID")):
    request_id = x_request_id or uuid.uuid4().hex
    logger.info(f"收到问题：{req.question!r}，request_id={request_id}")
```

- `Header(default=None, alias="X-Request-ID")`：客户端带了就把那串字取出来，没带就是 `None`
- `alias` 是"外面的名字"：HTTP 头上叫 `X-Request-ID`，代码里的变量叫 `x_request_id`，同一个东西两种叫法
- `x_request_id or uuid.uuid4().hex`：有号就用对方的号，没号就现场生成一个 32 位十六进制串

**② 数据库：`ask_logs` 加一列 + 唯一索引**

```sql
ALTER TABLE ask_logs ADD COLUMN request_id VARCHAR(64) NULL;
ALTER TABLE ask_logs ADD UNIQUE INDEX uk_ask_logs_request_id (request_id);
```

`models.py` 里对应的声明：

```python
request_id: Mapped[str | None] = mapped_column(String(64), unique=True)
```

**③ 查重逻辑：命中就直接返回上次结果**

```python
_CACHE: dict[str, dict] = {}          # 模块级：request_id → 上次返回内容

...
    if request_id in _CACHE:
        logger.info(f"命中幂等，request_id={request_id}，直接返回上次结果")
        return _CACHE[request_id]      # 不查库、不落库
...
    resp = {...}
    _CACHE[request_id] = resp          # 处理完先把结果存一份
    return resp
```

**顺序是关键：查重写在 `db.add` 之前。** 命中就提前 `return`，根本走不到插库那一步——**"不重复落库"是靠这个顺序实现的，不是靠后面的代码**。

### 幂等键从哪来

| 谁生成 | 怎么生成 | 幂等生效吗 |
|---|---|---|
| **前端**（生产常见） | 用户点"提交"时生成一个 UUID，**重发时带同一个** | ✅ 生效 |
| **手动填**（本阶段手测） | 在 `/docs` 的 `X-Request-ID` 框里填固定串，比如 `test-1` | ✅ 生效，只是号由人肉生成 |
| **服务端兜底**（`or uuid4()`） | 没带就现场生成一个 | ❌ 不生效——每次都是新号，重发会被当成新请求 |

**兜底那行的真实作用只是"字段不空着"**，它不提供防重能力。真正的幂等靠**调用方每次重发都带同一个号**。

没有前端时，这个号并不难得到：发起请求的人（你、Postman、以后的前端）自己填一个固定串就是有效的幂等键。

### 为什么用唯一索引

代码里的 `_CACHE` 查重挡在入口，但代码可能漏（多进程、重启、并发同时进来）。**唯一索引是数据库层面的最后一道闸**：同一个 `request_id` 想插第二条，MySQL 直接拒绝（`IntegrityError`）。

两道一起上：

| 层 | 作用 | 挡什么 |
|---|---|---|
| 代码 `_CACHE` 查重 | 命中直接返回，**省掉一次查库和一次插入** | 正常场景的重复请求 |
| 数据库唯一索引 | 插第二条直接失败 | 代码漏判、并发卡在同一瞬间、多进程各自的内存查重失效 |

### 不设会怎样

- **接口层**：同一次提交被执行多遍，返回多条记录
- **业务层**：如果是"扣款""下单""发通知"，就是重复扣款、重复下单、重复打扰用户
- **数据层**：日志表被重复数据污染，统计口径失真

对一个只读的查题接口，重复记录看起来"只是脏数据"；但这条路的终点是写操作，那时候就是钱的问题。

### 实测记录（2026-11-17）

**表结构（18:03:33 执行两条 ALTER 后生效）：**

```text
列:   ['id', 'question', 'matched', 'created_at', 'request_id']
索引: [('uk_ask_logs_request_id', True)]
```

**取号：**

```text
不带头        → request_id=e6858906a5bc4d26b6b7b48119e5e805   （32 位自动生成）
头=abc        → request_id=abc                                  （用了传进来的）
```

**落库：**

```text
id=15  request_id='demo1'                          （手填）
id=16  request_id='95033be800d54490aaeaf100c0efd615'（自动生成）
id=14  request_id=None                            （加列之前的老数据）
```

**幂等（18:45 实测）：**

```text
idem-A 第 1 次  → 正常处理
idem-A 第 2 次  → 返回内容与第 1 次完全一样；日志出现"命中幂等，request_id=idem-A，直接返回上次结果"
idem-B、idem-C  → 各处理一次
```

```text
测试后 TOTAL = 19
ROW 19 'idem-C' / 18 'idem-B' / 17 'idem-A' / 16 自动生成 / 15 'demo1' / 14 None
CNT idem-A = 1     CNT idem-B = 1     CNT idem-C = 1
```

**4 次请求只新增 3 条记录**——重复的那次被挡在入口，既没查库也没落库。

**本人另在 `/docs` 上按清单手测过一遍（`test-1` 连发两次、`test-2` / `test-3` 各一次），结果一致。**

### `_CACHE` 的边界（重要）

`_CACHE` 是**进程内的普通字典**，不是数据库：

| 情况 | 后果 |
|---|---|
| 服务重启 | 字典清空，之前的 id 全忘；同一个号再发会被当成新请求，**又插一条** |
| 多进程 / 多 worker | 每个进程各存各的字典，请求落到不同进程就**彼此看不见** |
| 服务扩容到多台机器 | 完全失效 |

注意区分：**`ask_logs` 里的 `request_id` 是持久化的**，重启后还在；丢的只是"上次返回内容"这份缓存。所以重启后能查到"这个 id 来过"，但没有答案可返回——要在重启后仍能直接返回旧结果，就得把结果本身存起来（Redis，或 `ask_logs` 再加一列 `answer`）。

### 这一条要记住的结论

**幂等解决的是"重复请求"，和超时、重试是三件不同的事。**

| 机制 | 解决什么 | 触发场景 |
|---|---|---|
| 超时 | **等太久** | 对方不响应（沉默、黑洞、慢查询） |
| 重试 | **瞬时故障** | 抖一下能自愈（连接被重置、池子短暂占满） |
| 幂等 | **重复请求** | 同一个业务被发了多次（手抖重发、客户端超时重发） |

**三者会叠加出现，但各自管一段：** 超时决定"等多久就放弃"，重试决定"放弃之前再试几次"，幂等决定"重试/重发造成的重复执行只算一次"。这就是为什么"被重试的动作必须是可重复执行的"——读操作天然可重复，写操作必须配幂等键。

### 还没做的一步（记录在案）

- **结果存在内存里**：`_CACHE` 重启失效、多进程不共享；生产应换 Redis 或给 `ask_logs` 加 `answer` 列
- **没有清理机制**：`_CACHE` 只增不减，长时间跑会一直占内存（本阶段请求量小，可忽略）
- **唯一索引冲突没有显式处理**：真撞上并发会抛 `IntegrityError` 变成 500，理想做法是捕获后回查旧记录再返回
- **没有单测**：幂等判定目前只靠手工请求验证，下一批 pytest 补用例

## 四、三者关系表（Day 12）

| 机制 | 解决什么问题 | 不设的后果 | 本项目的配置 |
|---|---|---|---|
| **超时** | 等太久 | 请求堆积、连接池耗尽 | 连接超时 5 秒（`connect_timeout=5`）；从池里排队取连接 5 秒（`pool_timeout=5`） |
| **重试** | 瞬时故障 | 一次抖动就失败 | 最多 2 次，间隔 0.5 秒；只对 `2003 / 2006 / 2013` 和池超时生效 |
| **幂等** | 重复请求 | 重复落库、重复执行 | `X-Request-ID` → `ask_logs.request_id` 唯一索引，`_CACHE` 命中即返回 |

### 一次 /ask 请求里，三者在哪一层生效

```text
请求进来
  │
  ├─ 第 1 层：幂等（main.py 的 _CACHE 查重，在 db.add 之前）
  │     命中 → 直接返回上次结果，后面的流程一步都不走
  │
  ├─ 第 2 层：重试（retry.py 的 retry_call 包住 do_query）
  │     查库失败且可重试 → 隔 0.5 秒再来，最多 2 次
  │
  └─ 第 3 层：超时（database.py 的引擎参数，最底层）
       连不上对端 → connect_timeout 5 秒后抛出
       池里没空闲连接 → pool_timeout 5 秒后抛出
       抛出的异常往上交给重试判断，决定是再来一次还是认输
```

**顺序很重要：幂等在最外层（先挡重复），重试在中间（挡抖动），超时在最底层（兜住无限等待）。** 三层各自独立：幂等命中时重试和超时都不会被触发；超时触发时重试可能把它接住再试一次；重试失败时向客户端抛 5xx。

### 三件事各解决什么（一句话版）

- **超时**：解决"等太久"——它不解决失败，只决定"多久之后不再等"
- **重试**：解决"瞬时故障"——只买"抖动一次能自愈"，不买"服务挂了也能救"
- **幂等**：解决"重复请求"——让重复执行只算一次

**它们会叠加出现，但不互相替代**：超时后要不要重试，是重试的决定；重试和重发会不会造成重复执行，是幂等的决定。

### 结构化日志（Day 12）

`main.py` 里每条结论日志都改成了"人话 + JSON 字段"的写法：`%(asctime)s [%(levelname)s]` 由 `basicConfig` 打在前面，后面跟一段 `json.dumps`。

```python
logger.info(json.dumps({"msg": "匹配到题库", "request_id": request_id,
                        "path": "/ask", "method": "POST", "question_id": row.id,
                        "duration_ms": round((time.perf_counter()-start)*1000, 1),
                        "status": "matched"}, ensure_ascii=False))
```

**为什么选"拼 JSON"而不是 `extra`：** 清单两种写法都允许，但 `extra` 必须改 `basicConfig` 的格式串，而格式串是全局的——`retry.py` 的三行重试日志、`/health`、`echo=True` 打出来的 SQL 回显都不带 `request_id`，一旦格式串里写了 `%(request_id)s`，它们每条都会刷一屏 `ValueError: Formatting field not found in record: 'request_id'`（实测见下）。拼 JSON 只影响改过的那几行，别处一个字不用动。

```text
--- ① 带 request_id 的日志 ---
2026-11-17 22:41:39,539 [INFO] req=s-1 收到问题
--- ② 没带的日志（retry / health / SQL 回显）---
--- Logging error ---
ValueError: Formatting field not found in record: 'request_id'
```

**实测输出（四条验收，2026-11-17 23:08）：**

```text
{"msg": "收到问题", "request_id": "f-1", "path": "/ask", "method": "POST", "question": "直角三角形"}
{"msg": "匹配到题库", "request_id": "f-1", "path": "/ask", "method": "POST", "duration_ms": 58.1, "status": "matched", "question_id": 4}
{"msg": "命中幂等，直接返回上次结果", "request_id": "f-1", "path": "/ask", "method": "POST", "duration_ms": 0.2, "status": "idempotent_hit"}
{"msg": "查询历史记录：最近20条", "request_id": "f-2", "path": "/history", "method": "GET", "count": 20, "duration_ms": 5.0, "status": "ok"}
{"msg": "问题为空，已拦截", "request_id": "f-3", "path": "/ask", "method": "POST", "duration_ms": 0.2, "status": "bad_request"}
```

**同一个 id 的两次请求，耗时 58.1 ms → 0.2 ms**，日志自己就把"省了一次查库"证明了。

**每条日志都能回答这四个问题：**

| 想知道的 | 看哪个字段 |
|---|---|
| 谁调的 | `request_id` |
| 调了什么 | `path` + `method` + `question` |
| 花了多久 | `duration_ms` |
| 成功还是失败 | `status` |

**`status` 取值：**

| 值 | 含义 |
|---|---|
| `matched` | 题库命中，200 |
| `unmatched` | 题库未收录，200 |
| `idempotent_hit` | 同一 `request_id` 重复请求，返回旧结果 |
| `bad_request` | 问题为空，400 |
| `ok` | `/history` 查询成功 |

**一条坑（记着）：** 字典里写 `"duration_ms": round(...)`，**别加引号**。加了引号就变成一个死字符串，日志里会打出 `"duration_ms": "round((time.perf_counter()-start)*1000,1)"` 这种原文——第一版就这么写错过，被日志自己暴露出来了。

**还没做的一步：** `retry.py` 里那三行重试日志仍是散装文本（`第 1 次重试（原因：…）`），没带 `request_id`。要统一得让 `retry_call` 收一个 `request_id` 参数再往下传，属于下一批的事。