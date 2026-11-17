# Day 1 学习记录（2026-11-15）

## 今天完成了什么

1. 搭起项目骨架：`service/main.py`，两个接口
   - `GET /health` → `{"status": "OK"}`
   - `GET /` → `{"message": "tutor-quality service running"}`
2. 能在本地把服务跑起来，并用浏览器 / 请求验证返回 200
3. 初始化 git 仓库，提交第一个 commit，分支改为 `main`
4. 配置 SSH 密钥，把本地仓库推送到 GitHub 公开仓库

## 环境

| 项 | 值 |
|---|---|
| 系统 | Windows 11 |
| 编辑器 | VS Code（集成终端 PowerShell） |
| Python | `D:\anaconda\envs\fastapi_learn\python.exe` |
| 仓库 | `github.com/1079314927/fastapi-learn` |

## 遇到的问题和解决方式

| # | 现象 | 真正的原因 | 怎么解决 |
|---|---|---|---|
| 1 | `TypeError: FastAPI.get() missing 1 required positional argument: 'path'` | `app = FastAPI` 少了括号，`app` 拿到的是类而不是实例，`app.get` 自然缺参数 | 改成 `app = FastAPI()` |
| 2 | `python main.py` 敲下去，终端什么都不打印，也不监听端口 | FastAPI 是 ASGI 应用，本身不会自己开服务器；直接 `python` 跑只是把模块导入了一遍 | 用服务器启动：`python -m uvicorn main:app --reload` |
| 3 | `git add.` 报 `git: 'add.' is not a git command` | 命令和参数之间缺了空格，git 把 `add.` 整体当成子命令名去找 | 写成 `git add .`（点前面有空格） |
| 4 | 提交后分支叫 `master`，远程默认是 `main`，两边对不上 | git 旧版本的默认分支名是 master | `git branch -M main` 强制改名 |
| 5 | 在资源管理器里把 `Readme.md` 改成 `README.md`，但 `git status` 什么都不显示 | Windows 文件名不区分大小写，git 也按不区分大小写比较路径，纯大小写改动视为「没变」 | 走两步：`git mv Readme.md Readme_tmp.md` → `git mv Readme_tmp.md README.md` |
| 6 | `git push` 之前，`git remote -v` 里是 `https://...` 地址 | `git remote add` 时填的是网页地址，HTTPS 不走 SSH，每次都要密码 / Token | `git remote set-url origin git@github.com:1079314927/fastapi-learn.git` |
| 7 | GitHub 网页经常打不开、`curl` 连接超时 | DNS 被污染，`github.com` 解析到不可用的 IP | 在 `hosts` 里写多条可用的 github.com 记录，让系统自动回退；改完 `ipconfig /flushdns` |
| 8 | 往 GitHub 贴公钥，报 `Key is invalid. You must supply a key in OpenSSH public key format` | 贴进去的不是公钥（私钥开头是 `-----BEGIN OPENSSH PRIVATE KEY-----`），或者在终端里选文字复制时把提示符一起带进去了 | 只复制 `id_ed25519.pub` 那一行（开头 `ssh-ed25519 AAAA...`），用 `Get-Content ... | Set-Clipboard` 写剪贴板再用 `Ctrl+V` |
| 9 | 把公钥整行粘进终端，报 `CommandNotFoundException` | 终端把这一长串当成命令去执行了 | 粘贴到 GitHub 网页的输入框里，不是粘到终端里 |

## 今天真正记住的几件事

- **`git add .` 的那个点不是标点，是「当前目录」**，前面必须有空格。
- **`.gitignore` 里写 `__pycache__/`（不带前导斜杠）会匹配任意层级**；写 `/__pycache__/` 才只匹配根目录。`git status` 里看不到它，就说明规则生效了。
- **`git remote add` 成功是静默的**，不打印任何东西，要用 `git remote -v` 去核对。
- **`git mv` / `git push` 这类命令必须在仓库目录里执行**，`ssh-keygen`、`ssh -T` 这类在哪个目录都行。
- **SSH 和 HTTPS 是两条路**：远程地址 `git@github.com:...` 开头走 SSH，`https://` 开头走 HTTPS。
- **私钥留在本机、公钥才上传**：公钥给别人没关系，私钥等于钥匙。

## 明天（day2）要做的事

- 在 `service/main.py` 里加业务接口，把请求参数和响应模型用起来
- 开始写 `tests/`，把接口验证从「手动点浏览器」换成可重复执行
- 继续在 `day1-notes.md` 后面追加当天记录，不另开新文件

## Day 2 学习记录

### 今天完成了什么

1. 新建 `service/models.py`，用 Pydantic 定义请求体：`class AskRequest(BaseModel): question: str`
2. 在 `service/main.py` 加 `POST /ask`：接一个 `AskRequest`，返回 `{"answer": ..., "question": ...}`
3. 加输入校验：空串、纯空格都返回 `400 {"error": "question不能为空"}`；缺字段由 FastAPI 自动回 `422`
4. 提交并推送：`bd633db day2: POST /ask with input validation`，本地和远程一致

### 实测记录

| 请求 | 返回 |
|---|---|
| `POST /ask`，`{"question":"正常内容"}` | `200`，正文带回 `answer` 和原问题 |
| `POST /ask`，`{"question":""}` | `400`，正文 `{"error":"question不能为空"}` |
| `POST /ask`，`{"question":"   "}` | `400`，正文 `{"error":"question不能为空"}` |
| `POST /ask`，`{}`（缺 question） | `422`，`detail` 里写明 `question` 字段缺失 |

### 遇到的问题和解决方式

| # | 现象 | 真正的原因 | 怎么解决 |
|---|---|---|---|
| 1 | 想用 `req.question == ""` 拦空问题，纯空格却照样过 | 空串和"全是空格"不是一回事，`==` 只认内容完全相等 | 先 `.strip()` 去掉首尾空格再比：`if req.question.strip() == "":` |
| 2 | 地址栏打开 `127.0.0.1:8000/ask`，得到 `{"detail":"Method Not Allowed"}` | 浏览器地址栏只会发 GET，`/ask` 是 POST，还必须带请求体 | POST 只能走 `/docs` 里的 Try it out，或者用脚本发请求 |
| 3 | 缺 `question` 字段返回的是 `422`，不是自己写的 `400` | `422` 是 FastAPI 进函数之前做的参数校验，函数体根本没跑 | 这是框架自动行为，不用自己写；`400` 只负责"字段有了但内容不合规" |
| 4 | 想等晚上把 day2 和 day3 攒在一起提交 | 一个 commit 混两天的工作，清单要的三条独立提交就少一条，以后也看不出哪天做了什么 | day2 收尾时先把 `main.py` 里 day3 的 `/history` 占位删掉，只提交 day2 的内容 |
| 5 | 在 `service/` 子目录里 `git add .`，`docs/` 的改动没被带上 | `.` 只代表"当前目录"，在子目录里 add 只能收子目录里的东西 | 在仓库根目录执行 `git add .`；add 完先 `git status` 核对清单 |
| 6 | 本地文件和远程文件字节数差几字节，怀疑内容丢了 | Windows 里存的是 CRLF 换行，git 提交时转成 LF，每行少 1 字节 | 用"行数差 = 字节差"对账，或用 jsDelivr 拉远程原文逐字比对，内容一致就不用管 |

### 今天真正记住的几件事

- **`git add .` 的那个点是"当前目录"**，在子目录里跑会漏掉外面的改动。
- **add 完先 `git status`，再 `git commit`**，看清到底提交了哪几个文件。
- **commit message 用清单原文**（`day2: POST /ask with input validation`）：前缀 + 动词 + 路径 + 关键点，不写"更新代码""fix"这种空话。
- **`422` 和 `400` 分工不同**：`422` 是字段缺失或类型不对，框架在进函数前就挡了；`400` 是内容不合规，得自己写。
- **输入校验要把极端情况都试一遍**：正常、空串、纯空格、缺字段。

### 明天（day3）要做的事

- 给服务配 logging，在 `POST /ask` 里打三处日志
- 加 `GET /history`，先返回空列表
- 提交：`day3: logging + GET /history stub`

## Day 3 学习记录（2026-11-15）

### 今天完成了什么

1. 给 `service/main.py` 加 logging：6 行配置，放在 `import` 之后、`app = FastAPI()` 之前
2. `POST /ask` 里加三处日志：收到问题（INFO）、空问题被拦截（WARNING）、返回结果（INFO）
3. 新增 `GET /history`，先返回空列表 `[]`
4. 亲眼确认日志真的打出时间、级别、消息

### 实测记录

起服务后发了四条请求：

| 请求 | 返回 |
|---|---|
| `GET /history` | `200`，正文 `[]` |
| `POST /ask`，`{"question":"我在学FastAPI"}` | `200`，正文 `{"answer":"这是硬编码的答疑结果","question":"我在学FastAPI"}` |
| `POST /ask`，`{"question":""}` | `400`，正文 `{"error":"question不能为空"}` |
| `POST /ask`，`{"question":"   "}` | `400`，正文 `{"error":"question不能为空"}` |

终端日志：

```
2026-11-15 20:45:55 [INFO] 查询历史记录
2026-11-15 20:45:55 [INFO] 收到问题：'我在学FastAPI'
2026-11-15 20:45:55 [INFO] 返回结果：这是硬编码的答疑结果。
2026-11-15 20:45:55 [INFO] 收到问题：''
2026-11-15 20:45:55 [WARNING] 问题为空，已拦截。
2026-11-15 20:45:55 [INFO] 收到问题：'   '
2026-11-15 20:45:55 [WARNING] 问题为空，已拦截。
```

### 遇到的问题和解决方式

| # | 现象 | 真正的原因 | 怎么解决 |
|---|---|---|---|
| 1 | `logger = logging.getLogger(__name__)` 整行看不懂，看实验也看不懂 | 把它当成一段魔法代码去背；其实是普通赋值，`__name__` 是 Python 自动给的值 | 拆成"领一本叫 main 的本子"：`getLogger("main")` 是向 logging 要一本按名字登记的记事本，`__name__` 在 uvicorn 下就等于 `main` |
| 2 | 以为 `__name__` 在 `main.py` 里永远是 `"main"` | `__name__` 的值取决于运行方式：`python main.py` 直接跑是 `"__main__"`，被 uvicorn 导入才是 `"main"` | 用 uvicorn 启动时打印确认，日志前缀显示的确实是 `main` |
| 3 | 想用 `AskRequest.question` 取用户的问题 | `AskRequest` 是类（空白模板），值只存在 FastAPI 照模板造出来的实例 `req` 上；直接读类属性会 `AttributeError` | 只写 `req.question`。参数名 `req` 可以随便改，冒号后的 `AskRequest` 不能改 |
| 4 | 日志写在 `return` 后面，一行都不出 | `return` 一执行函数就结束，它后面的代码永远不跑 | 三处日志都放在各自的 `return` 之前 |
| 5 | `format` 末尾多打了一个空格，不确定能不能加 | `format` 是模板字符串，除 `%(...)s` 以外的字符都会原样输出，行尾那个空格什么都看不见 | 空格只放在两段之间的分隔位置，行尾不加 |
| 6 | 空串和纯空格的日志在终端里长得一样，分不出当时收到的到底是什么 | 默认用 `str` 输出，内容原样显示，空格和空都"看不见" | 加 `!r` 走 `repr`：打出 `''` 和 `'   '`，边界一眼可辨 |
| 7 | `/history` 为什么该返回 `[]` 而不是 `{}` | 历史记录是一串数据，前端按列表循环；空字典不能循环，前端会报错 | 先用空列表把接口形状定住，以后再往里填记录 |
| 8 | 地址栏打开 `127.0.0.1:8000/ask` 显示 `{"detail":"Method Not Allowed"}` | 浏览器地址栏只能发 GET，`/ask` 是 POST，还得带请求体 | POST 要走 `/docs` 里的 Try it out，或者用脚本发请求 |

### 今天真正记住的几件事

- **`logging.basicConfig` 只配一次**，写在 `import` 之后、`app = FastAPI()` 之前；调两次第二次会被静默忽略。
- **日志级别是"最低门槛"**：设成 `INFO`，`info` 和 `warning` 都会输出，`debug` 被丢掉。
- **日志必须写在 `return` 之前**，否则等于没写，而且不会报错。
- **`{}` 默认走 `str`，`{!r}` 走 `repr`**：后者给字符串加引号、把换行显示成 `\n`，回查日志时更可靠。
- **类是模板，实例才有值**：`AskRequest.question` 读不到，`req.question` 才对。
- **`[]` 是空列表、`{}` 是空字典**，形状不同，前端处理方式也不同。

### 明天（day4）要做的事

- 写 `docs/architecture.md`：文字版分层图（路由层 `main.py` → 服务层 `service.py` → 数据层暂未接入），写清每层职责，以及为什么不把所有代码都塞进 `main.py`
- 提交：`day4: architecture doc`

## Day 4 学习记录（2026-11-15）

### 今天完成了什么

1. 新建 `docs/architecture.md`，画了文字版分层图：路由层 `service/main.py` → 服务层（`service.py` 待建，逻辑暂时还在 `main.py`）→ 数据层（未接入，`/history` 先返回写死的 `[]`）
2. 写清每层的职责（负责什么 / 不负责什么），以及"为什么不把所有代码都塞进 `main.py`"
3. 复核 `service/` 下的文件结构：`main.py`、`models.py` 已在；`service.py`、`logger.py` 按清单"如有"的口径，暂不单独建
4. 提交并推送：`a60988c day4: architecture doc`

### 实测记录

| 动作 | 结果 |
|---|---|
| `git log --oneline -1` | `a60988c day4: architecture doc` |
| `git rev-list --left-right --count origin/main...main` | `0  0`（本地和远程完全一致） |
| 远程 `docs/architecture.md` | 1027 B；本地 1064 B，差 37 字节 = 34 行 CRLF 换成 LF，内容一致 |

### 遇到的问题和解决方式

| # | 现象 | 真正的原因 | 怎么解决 |
|---|---|---|---|
| 1 | 写完 `architecture.md` 整篇排版乱掉，后半段全变成代码块 | 围栏写法错了两处：开头写成 ` ``` 调用方…`，把后面那行文字当成了"语言名"；结尾 `[]``` ` 没独占一行，围栏没合上 | 围栏的三个反引号必须**独占一行**：开头行只放语言名（可留空），结尾行只放 ` ``` `；改完核对围栏成对（第 5 行开、第 16 行合） |
| 2 | 看不懂 FastAPI `lifespan` 里的 `yield`："暂停一下有什么用" | 把 `yield` 当成 `return` 在理解：以为函数到这就结束了 | `return` 是结束、不再回来；`yield` 只是**暂停**，把控制权交出去，外面干完还能回来接着跑 |
| 3 | 追问"`my_demo` 函数怎么会知道中间要暂停，去执行 `main` 里的代码" | 以为是函数自己会跳出去 | **不是它跳**，是 `async with` 这条语句 + `@asynccontextmanager` 这套机制**规定好了顺序** |
| 4 | `lifespan` 里我根本没写过 `async with`，那"缩进块"到底在哪 | 那句 `async with lifespan(app):` 是 **FastAPI 内部替我们写的** | 缩进块 = **FastAPI 自己的服务器主循环**（监听端口、不停收请求）；只有按 `Ctrl+C` 关服务，这块才结束，`yield` 后面的释放代码才会执行 |
| 5 | 不理解"先准备、后收尾"为什么非得靠 `yield` 分开 | 没想到没有 `yield` 时代码会一口气跑完 | 没有这个暂停，建表和释放连接会连着执行，**数据库刚建好就被关掉，服务根本没机会运行** |

### yield 那件事，一句话记住

`yield` 把函数切成三段：**准备 → 对外服务 → 收尾**。

最小例子（`@asynccontextmanager` + `async with`）的输出顺序永远是：

```
① 准备工作
② 中间正在干活
③ 收尾工作
```

缩进块里有多少行、跑多久，收尾就等多久；**整块跑完才会回到 `yield` 后面**。

（另外记一条：`@asynccontextmanager` 装饰的函数**只能有一个 `yield`**，写两个会报错；多个 `async with` 嵌套时"先进后出、后开的先收尾"。）

### 今天真正记住的几件事

- **分层不是为了好看**：改动能隔离、每层能单独测、换实现只改一处。
- **Markdown 围栏必须独占一行**，开头行后面只能跟语言名；否则整篇会被吞进代码块。
- **`return` 是结束，`yield` 是暂停**，停完还要回来。
- **`async with` 的缩进块跑完，才轮到 `yield` 后面**，不是跑一句就回去一次。
- **`lifespan` 的缩进块是 FastAPI 的服务器循环**，这就是"服务一直在跑、关服务才释放资源"的原因。
- **本地和远程字节数差几字节不用慌**，多半是 CRLF 换成 LF，用"行数差 = 字节差"对账即可。

### 明天（day5）要做的事

- 启动 MySQL，建库 `tutor_ai`、建表 `questions`
- 装 `sqlalchemy` + `pymysql`
- 写 `service/database.py`，能解释 engine / SessionLocal / 为什么连接信息不该写死
## Day 5 学习记录（2026-11-16）

### 今天完成了什么

1. 启动 MySQL：管理员终端 `net start MySQL80`，再用全路径 `mysql.exe -u root -p` 登录成功
2. 建库 `tutor_ai`（`CHARACTER SET utf8mb4`），`SHOW DATABASES` 能看到，`USE tutor_ai` 返回 `Database changed`
3. 建表 `questions` 六列（`id` / `question` / `knowledge_point` / `steps` / `common_mistake` / `created_at`），`DESC questions` 逐行核对
4. 在 `fastapi_learn` 环境装依赖：`sqlalchemy 2.1.8` + `PyMySQL 1.2.4`
5. 新建 `service/database.py`：`DATABASE_URL` + `engine` + `SessionLocal`
6. 实测连通：`SELECT 1` 返回 `1`

### 实测记录

| 动作 | 结果 |
|---|---|
| `net start MySQL80` | `MySQL 服务已经启动成功。` |
| `CREATE DATABASE tutor_ai CHARACTER SET utf8mb4;` | `Query OK, 1 row affected` |
| `SHOW DATABASES;` | 列表里出现 `tutor_ai` |
| `USE tutor_ai;` | `Database changed` |
| `DESC questions;` | `6 rows in set`；`id` 行 `PRI` + `auto_increment`，`created_at` 行 `CURRENT_TIMESTAMP` |
| `pip install sqlalchemy pymysql` | `Successfully installed pymysql-1.2.4 sqlalchemy-2.1.8` |
| `SELECT 1` | 返回值 `1` |

### 遇到的问题和解决方式

| # | 现象 | 真正的原因 | 怎么解决 |
|---|---|---|---|
| 1 | 双击 MySQL 客户端窗口闪一下就没了，或报 `Can't connect ... (10061)` | 客户端只是"登录工具"，服务没启动就没有进程应答 | 管理员终端 `net start MySQL80`，服务起来后再用客户端登录 |
| 2 | `conda activate fastapi_learn` 之后 `sys.executable` 还是 `D:\anaconda\python.exe`，提示符前也没有 `(fastapi_learn)` | 这台机器没执行过 `conda init`，PowerShell 里的 `conda` 只是外部程序 `conda.bat`；外部程序改不了父终端的 PATH，子进程一退改动就没了 | 装包直接指定解释器全路径：`& 'D:\anaconda\envs\fastapi_learn\python.exe' -m pip install ...`；想彻底修好就 `conda init powershell` 后重开终端 |
| 3 | 包看起来装上了，`import` 仍报 `No module named 'sqlalchemy'` | 装进了 `base` 环境，不是 `fastapi_learn` | 装之前先 `python -c "import sys; print(sys.executable)"`，确认路径是 `...\envs\fastapi_learn\python.exe` |
| 4 | `sqlalchemy.exc.NoSuchModuleError: Can't load plugin: sqlalchemy.dialects:mysql.pysql` | URL 里驱动名写成 `pysql`，少了 `my` | 改成 `mysql+pymysql://`；报错里那个名字就是 URL 里 `+` 后面那截 |
| 5 | `ImportError: cannot import name 'engine' from 'database'` | `service/database.py` 是 0 字节的空文件（建了文件，但没保存/没粘内容） | 粘贴代码后 `Ctrl+S`；标签页文件名旁的小白点消失才算真存进磁盘 |
| 6 | `sessionmaker` 的参数表里找不到 `autocommit` | 参数表末尾有 `**kw`，剩下的关键字参数会原样转给 `Session`；`autocommit` 是 1.x 的遗留参数 | 2.0 之后已没有自动提交模式，删掉即可：`sessionmaker(bind=engine, autoflush=False)` |
| 7 | `echo=True` 后看到的 SQL 比自己写得多 | `autoflush` 默认 True，查询前会先把攒着的改动偷偷发出去 | 学习期写 `autoflush=False`，日志里每条 SQL 都能对上自己的代码 |
| 8 | 重启电脑后再连库，直接报 `2003 / 10061` | `MySQL80` 的启动类型是 `Manual`，开机不会自己起 | 管理员执行 `Set-Service -Name MySQL80 -StartupType Automatic`，改成开机自启 |
| 9 | 密码直接写进了 `database.py`（复盘中已隐去，不把密码写进仓库） | 仓库是 Public，一旦 commit 密码就公开 | 第 7 天 commit 前改读环境变量：`setx DB_PASSWORD` + `os.getenv('DB_PASSWORD')` |

### 今天真正记住的几件事

- **MySQL 是"服务"，不是文件**：数据一直在硬盘上，服务不跑就连不上；服务停了不等于数据丢了。
- **客户端 ≠ 服务端**：DataGrip / MySQL 客户端只负责"登录 + 发 SQL"，真正应答的是 `MySQL80` 这个服务。
- **建库建表用 SQL 做，Python 只负责读写**：SQLAlchemy 的模型类只是"图纸"，不会自己建表（显式 `create_all` 除外）。
- **"目录"和"环境"是两件事**：提示符里的 `(fastapi_learn)` 才是环境，`PS D:\Code\...` 只是当前文件夹。
- **驱动名就是 URL 里 `+` 后面那截**：报错说找不到哪个名字，回去查这两个字母。
- **`SELECT 1` 是最干净的体检**：不碰任何表，能返回 `1` 说明驱动、端口、账号、库全通。
- **`echo=True` 负责看 SQL，`autoflush=False` 负责让 SQL 不偷偷多出来**，两个一起用日志才干净。

### 明天（day6）要做的事

- `service/models.py` 加 SQLAlchemy 模型 `Question`，映射 `questions` 表
- 写 `service/seed.py`，插入 5 条真实初中数学题，跑完用 `SELECT * FROM questions;` 确认
- 待办：第 7 天 commit 前把 `database.py` 里的密码改成环境变量

## Day 6 学习记录（2026-11-16）

### 今天完成了什么

1. `service/models.py` 里加 `Base`（`DeclarativeBase`，SQLAlchemy 的“登记簿”），再写 `Question` 模型，映射 `questions` 表六列
2. 新建 `service/seed.py`，写入 5 条真实的初中数学题（因式分解、分式方程、二次函数配方、勾股定理、不等式组），每道都带知识点、步骤、易错点
3. 跑 `python seed.py` 插入成功，表里 5 条，`created_at` 由数据库自动填
4. 能讲清 ORM 模型（`Question`）和 Pydantic 模型（`AskRequest`）的区别

### 实测记录

| 动作 | 结果 |
|---|---|
| `db.query(Question).count()`（模型体检） | 返回 `0`，`echo` 打出 `FROM questions` 和六个列名全对，证明表名、列名映射成功 |
| `python seed.py` | 5 条 `INSERT` + `COMMIT`，终端打印 `插入完成 5 条`；`COUNT = 5`，第一条 `id=1`、`created_at=2026-11-16 21:23:02` |
| INSERT 语句本身 | 列里**没有 `created_at`**，但表里有值 → 印证 `server_default` 是数据库在填 |
| 再跑一次 `seed.py` | 变成 10 条（重复）→ `DELETE FROM questions WHERE id > 5;` 后回到 5 条 |
| 查 `AUTO_INCREMENT` | 行数 5、最大 id 5、**下一个发号 11** |
| Pydantic 手测 5 种输入 | 缺字段 → `ValidationError`（→ 422）；传数字 → `ValidationError`；多传字段 → 被忽略；**空字符串 → 通过** |

### 遇到的问题和解决方式

| # | 现象 | 真正的原因 | 怎么解决 |
|---|---|---|---|
| 1 | `class  base(DeclarativeBase)` 小写 | 类名按惯例首字母大写，且小写易与 Pydantic 的 `BaseModel` 看混 | 改成 `class Base(DeclarativeBase)` |
| 2 | 体检报“表不存在” | `__tablename__ = "question"` 少了个 `s` | 必须和 MySQL 里真实的表名 `questions` 一字不差 |
| 3 | 体检报 `Unknown column 'create_at'` | 属性名 `create_at` 少了个 `d` | 改成 `created_at`，和表里的列名对齐 |
| 4 | `ModuleNotFoundError: No module named 'database'` | 站在仓库根目录 `D:\Code\fastapi-learn` 跑，而 `database.py` 在 `service` 子目录 | `cd D:\Code\fastapi-learn\service` 再跑；Python 只在**当前目录**找模块 |
| 5 | `seed.py` 说有内容但跑起来是空 | 磁盘上仍是 **0 字节**，粘贴后没保存；而且**空文件也能通过 `py_compile`** | `Ctrl+S`，看标签页小白点消失；不能靠“语法 OK”判断有没有内容 |
| 6 | `from service.database import SessionLocal` 报错 | `service` 不是包（没有 `__init__.py`），也不是从仓库根用 `-m` 跑 | 同目录兄弟文件直接 `from database import SessionLocal` |
| 7 | `NameError: name 'QUESTION' is not defined` | 定义的是 `QUESTIONS`（复数），用的是单数 | 定义什么名字，用就写什么名字，一个字母都不能差 |
| 8 | 一堆 `SyntaxError` | ① 前一字段末尾漏逗号 → 相邻两个字符串被**自动拼接**，再撞上 `:` 就报错；② 字典之间 `}` 后面漏逗号 | 键值对末尾补逗号（尾逗号合法，推荐留着）；**相邻两个字典之间必须有逗号** |
| 9 | `db.close` 写了但连接没还 | 少了括号，只引用了个方法没调用 | `db.close()` |
| 10 | 打印出来是文字 `插入完成,len(QUESTIONS)` | `len(...)` 被写在引号里 | `print("插入完成", len(QUESTIONS), "条")`——引号内一切都是文字 |
| 11 | 表里变成 10 条 | `seed.py` 是**追加**不是覆盖，跑两次就是两份 | 先 `DELETE FROM questions WHERE id > 5;` 只留一份；以后重跑前先清空 |
| 12 | `SELECT *` 排版全乱 | `steps` 里有 `\n`，客户端真的按换行显示，把表格撑开 | 只查短字段，或用 `SELECT * FROM questions\G`（竖排） |

### 今天真正记住的几件事

- **对表的名字不能改**：`__tablename__` 的值、模型属性名会直接变成 SQL 里的表名列名，必须和数据库一字不差；能换词的才是“自己起的名”。
- **大小写是约定**：类首字母大写（`Question`）、常量全大写（`QUESTIONS`）、列名和变量全小写（`question`）。Python 不强制，但人能一眼分清角色。
- **少一个逗号，报错常出现在下一行**：因为相邻字符串会自动拼接，真正的错在拼接之后。
- **逗号是分隔符**：字典内部最后一对可省（写了也没错），**两个字典之间必须有**。
- **`add` 只是进篮子，`commit` 才真的写库，`close()` 要带括号**。
- **数据库填的默认值 = `server_default`**：`INSERT` 语句里看不到该列，表里却有值。
- **`id` 发号器只增不回退**：`DELETE` 删数据不回收号码，所以清掉 6—10 后下一个是 11；要归零只能 `TRUNCATE`（连数据一起清）。
- **Pydantic 不拦空字符串**：`""` 是合法 `str`；“问题不能为空”是我在 `main.py` 里自己写的 `if`，业务规则归代码，结构调整归 Pydantic。
- **两个模型各管一层，互不认识**：`AskRequest` 不碰数据库，`Question` 不懂 HTTP/JSON，中间靠 `main.py` 把它们接起来。

### ORM 模型 vs Pydantic 模型（对比）

| 对比项 | Pydantic 的 `AskRequest` | SQLAlchemy 的 `Question` |
|---|---|---|
| 管谁 | 外面进来的**请求** | 仓库里的**表数据** |
| 有表名 | 无 | `__tablename__ = "questions"` |
| 连数据库 | **不连** | **连** |
| 主要职责 | JSON 变对象、检查类型/必填/多余字段 | 把一行数据搬进/搬出表 |
| 数据方向 | **进**（校验完交给代码） | **存**（和库一一对应） |
| 报错形式 | `ValidationError` → FastAPI 回 **422** | SQL 报错，如 `Unknown column` |
| 附加能力 | 自动生成 `/docs` 里的请求示例 | 自动拼 `INSERT` / `SELECT` |

一句话：**`AskRequest` 是门口的安检，`Question` 是仓库的货架；两个东西各管一层，中间由 `main.py` 的代码把它们接起来。**

### 明天（day7）要做的事

- 改 `POST /ask`：按关键词去 `questions` 表模糊匹配，查到返回 `steps` 和 `common_mistake`，查不到返回 `{"answer": "题库暂未收录该题", "matched": false}`
- 新建 `ask_logs` 表（id、question、matched、created_at），每次请求落一条
- 手动测试三条：题库里有的题、题库里没有的题、空字符串（仍 400）
- 第一次 commit（`day5` 起的改动一起提交）：`day7: /ask queries DB and logs requests`；提交前确认 `database.py` 已读环境变量、仓库里没有明文密码

## Day 7 学习记录（2026-11-16）

### 今天完成了什么

1. MySQL 里建 `ask_logs` 表（`id`、`question`、`matched`、`created_at`），`matched` 用 `BOOLEAN`
2. `service/models.py` 加 `AskLog` 模型，把布尔这列写成 `Mapped[bool] = mapped_column(Boolean, ...)`
3. `service/main.py` 加 `get_db()`：用 `yield` 借出会话、`finally` 里归还
4. `POST /ask` 改成真查库：`query` → `filter(...contains...)` → `first`；同时 `db.add(AskLog(...))` + `db.commit()` 落一条日志
5. 三条手测全过；`ask_logs` 累计 7 条真实记录

### 实测记录

| 动作 | 结果 |
|---|---|
| 建表后看结构 | `id` INTEGER 非空、`question` TEXT 非空、`matched` **TINYINT** 非空、`created_at` DATETIME 默认 `CURRENT_TIMESTAMP` |
| `db.query(AskLog).count()` | `0`，`echo` 打出 `FROM ask_logs` 和四列，映射成功 |
| POST `直角三角形` | 200，返回 `steps` + `common_mistake` + **`matched: true`**（布尔，不是字符串） |
| POST `三角函数怎么算` | 200，`{"answer": "题库暂未收录该题", "matched": false}` |
| POST `""` | **400**，`{"error": "question不能为空"}` |
| 查 `ask_logs` | 7 条，`matched` 是真布尔 True/False，`created_at` 自动带时间 |

### 遇到的问题和解决方式

| # | 现象 | 真正的原因 | 怎么解决 |
|---|---|---|---|
| 1 | `ImportError: cannot import name 'boolean'` | 写成小写；库里的类名就是 `Boolean` | 照库的写法 `from sqlalchemy import Boolean`；报错里的 `Did you mean: 'Boolean'?` 基本就是大小写错了 |
| 2 | 接口返回 `"answer": "row.steps"`、`"matched": "False"` | **引号里的一切都是文字**，`row.steps` 被框住就成了字面字符串 | 固定文字才加引号；`row.steps`、`True`、`False` 都不加 |
| 3 | `SessionLocal` 被 import 了两次 | 复制粘贴时多留了一行 | 删掉重复的第 9 行 |
| 4 | 拿“勾股定理”测，返回“暂未收录” | 这四个字只在 `knowledge_point` 列，`question` 列里没有；且 `contains` 是单边的 | 测要用题目里的词（如 `直角三角形`）；品类问题留到 day8 之后优化 |
| 5 | 输入“直角三角形怎么判断”匹配不到 | `Question.question.contains(输入)` 要求**题目包含输入**，输入比题目长就不可能成立 | 单边匹配的固有局限，记下来当优化项 |
| 6 | uvicorn 那个窗口敲不进命令 | uvicorn 前台运行、占着终端，没有提示符 | 另开一个终端；或直接用 `http://127.0.0.1:8000/docs` 的 Try it out |
| 7 | 浏览器直接开 `/ask` 报 `Method Not Allowed` | 地址栏只能发 GET，`/ask` 只收 POST | 用 `/docs` 页面或终端发 POST |

### 今天真正记住的几件事

- **`BOOLEAN` 就是 `TINYINT(1)` 的别名**：数据库没有真布尔，存 `1`/`0`；`Mapped[bool]` ↔ `Boolean` ↔ `TINYINT(1)` 三层自动转换，Python 里写 `True`，库里存 `1`，JSON 里输出 `true`。
- **`try/finally` 不是“抓错误”，是“保证收尾”**：路由函数报错时异常从 `yield` 弹回来，只有 `finally` 能保证 `db.close()` 执行；这里故意不写 `except`，错误要原样抛出去。
- **`Depends(get_db)` = FastAPI 替你调用它**：把 `yield` 出来的 `db` 直接塞进参数，自己不用 `get_db()`。
- **查库三件套**：`db.query(Question)` = `FROM questions`、`.filter(...)` = `WHERE ...`、`.first()` = `LIMIT 1`；查不到返回 `None`，所以 `matched = row is not None`。
- **`add` 是进篮子、`commit` 才落库**，和 `seed.py` 完全一样的规矩。
- **JSON 里的布尔没引号**：Python 写 `True`/`False`，返回给前端自动变 `true`/`false`；带引号就是字符串。
- **匹配方式决定能力上限**：只查 `question` 一列 + `contains` 单边，所以“勾股定理”（只在知识点里）和“直角三角形怎么判断”（比题目长）都匹配不到——这是已知缺口，不是 bug。

### 明天（day8）要做的事

- `GET /history` 改成从 `ask_logs` 查最近 20 条返回
- 查询前后加日志：记查询条件、返回条数、**耗时**
- 更新 `docs/architecture.md`：数据层已接入，补表结构和查询路径
- `git commit -m "day8: /history queries DB + query logging"` 并 push
- （可选，day8 之后独立小提交）`/ask` 同时匹配 `question` 和 `knowledge_point`

## Day 8 学习记录（2026-11-16）

### 今天完成了什么

1. `GET /history` 从"返回写死的 `[]`"改成真查库：`query(AskLog)` + `order_by(created_at.desc())` + `limit(20)` + `all()`
2. 给查询加了耗时统计：`time.perf_counter()` 取前后两个时间点相减，日志里打出"返回 N 条，耗时 x ms"
3. 用列表推导把 `AskLog` 对象批量转成字典（也写了一版普通 `for` + `append` 对照，最后只留推导）
4. 更新 `docs/architecture.md`：数据层从"未接入"改成"已接入"，补了两张表的字段、连接配置位置、两条查询路径
5. 删掉 `main.py` 末尾注释掉的旧写法，保持仓库里只有一种写法

### 实测记录

| 动作 | 结果 |
|---|---|
| `GET /history` | **200，7 条**，按时间倒序：id 6（直角三角形 true）、7（三角函数怎么算 false）、5、4、3、2、1 |
| 返回字段 | `id` / `question` / `matched`（真布尔）/ `created_at`（ISO 时间串）全对 |
| 第一条日志 | `查询历史记录：最近20条` |
| 第二条日志 | `返回7条，耗时73.5ms` |
| 连续请求三次 | **49.9 ms → 2.5 ms → 2.4 ms**（差近 20 倍） |
| `main.py` 语法检查 | `py_compile` 通过 |
| 全仓库密码扫描 | 无明文密码 |

### 遇到的问题和解决方式

| # | 现象 | 真正的原因 | 怎么解决 |
|---|---|---|---|
| 1 | 起服务后 `GET /history` 返回 **500**，日志里 `Access denied for user 'root'@'localhost' (using password: YES)` | 那个进程里**没有 `DB_PASSWORD`**：`setx` 只对"之后新开的进程"生效，父进程早于它启动就读不到 | 关掉终端重开；或临时把用户变量读进当前会话再起服务 |
| 2 | 列表推导 `[{...} for r in rows]` 看不懂，觉得"倒过来写了" | 它是 `result=[]` + `for` + `append` 三件事压成一行 | 方括号就是篮子，最前面是 `append` 里的东西，`for` 说明数据从哪来 |
| 3 | 注释版 `result.append"id":row.id, ...)` 会报语法错 | `append` 漏了左括号 `(`，字典漏了左花括号 `{` | 写成 `append({"id": row.id, ...})` |
| 4 | 第一次请求 49.9 ms，怀疑代码慢 | 第一次要跟 MySQL **建立连接**（认证 + 握手） | 连接留在池里复用，第 2、3 次只要 2.5 ms |

### 今天真正记住的几件事

- **`order_by(...desc())` = `ORDER BY ... DESC`、`limit(20)` = `LIMIT 20`**：排序和限量就是在 SQL 后面加两句。
- **`.all()` 与 `.first()` 的区别**：`all()` 返回**列表**（空表给 `[]`），`first()` 返回一个对象或 `None`。
- **`time.perf_counter()` 是秒表**：开始按一次、结束按一次，相减得花了几秒；×1000 变毫秒；`{cost:.1f}` 是保留一位小数的格式化写法。
- **列表推导 `[要什么 for 从哪来]`**：方括号 = 新列表，最前面 = 每条要变成什么，后面 = 数据从哪来；不顺手就退回普通 `for` + `append`，功能完全一样。
- **ORM 对象不会自动变成 JSON**，要手动写成字典（`{"id": r.id, ...}`）再交给 FastAPI。
- **第一次请求慢是"建连接"，不是"代码慢"**：连接池复用后快 20 倍。
- **环境变量只对之后新开的进程生效**——这条今天不是听说的，是真撞到了 500。

### 下一批（第 9—12 天）要做的事

- 第 5—8 天这批（接 MySQL + ORM 落库）到此收官
- 下一批：容错设计（超时、重试、幂等）+ pytest
- 备选小优化：`/ask` 改成同时匹配 `question` 和 `knowledge_point`

## Day 9 学习记录（2026-11-17）

### 今天完成了什么

1. `service/database.py` 的 `create_engine` 加了两道护栏：`connect_args={"connect_timeout": 5}`（建连接最多等 5 秒）和 `pool_timeout=5`（从池里借连接最多等 5 秒）
2. 三个层次各测了一遍超时：**引擎层**、**连接池层**、**接口层**（`/ask` 真等超时）
3. 新建 `docs/resilience.md`，写完第一条（超时）：配置、为什么 5 秒、不设会怎样、实测数据
4. 弄清一条最重要的结论：**超时解决的是"等太久"，不是"失败"**

### 实测记录

| 检查 | 结果 |
|---|---|
| `engine.pool._timeout` | **5**（参数确实生效） |
| 池类型与容量 | `QueuePool`；`pool_size=5` + `max_overflow=10` → **最多 15 个连接** |
| `SELECT 1` | 返回 1（加参数没有破坏正常连库） |
| 黑洞地址 `10.255.255.1`，`connect_timeout=2` | **2.05 秒**，`OperationalError`（2003 Can't connect ... timed out） |
| 本机 `127.0.0.1`，密码故意写错 | **0.02 秒**，`OperationalError`（1045 Access denied） |
| 池子占满（`pool_size=5, max_overflow=0, pool_timeout=2`，第 6 个连接） | **2.01 秒**，`TimeoutError`（QueuePool limit of size 5 overflow 0 reached） |
| **接口层**：`POST /ask`（库指向黑洞） | **500，耗时 5.13 秒** |
| **接口层**：`GET /health`（同时发，不碰库） | **200，耗时 0.037 秒** |

### 遇到的问题和解决方式

| # | 现象 | 真正的原因 | 怎么解决 |
|---|---|---|---|
| 1 | `TypeError: Invalid argument(s) 'poll_timeout' sent to create_engine()` | 把 `pool_timeout` 写成了 `poll_timeout`，少一个 `l`；`create_engine` 不认识这个名字 | 改成 `pool_timeout=5`；报错会直接点名是哪个参数不认识 |
| 2 | 以为"池子只有 5 个连接，第 6 个就排队" | `QueuePool` 还能溢出：`pool_size=5` + `max_overflow=10` = **15** | 实测 `pool.size()` 和 `pool._max_overflow`；真正排队的是**第 16 个** |
| 3 | 以为"不可达地址"是"地址存在但连不上" | 准确说是"**可达但没有应答**"（沉默）；"有人应答但拒绝"是完全另一种情况 | 用三种失败形态区分（见下） |
| 4 | 想验证接口层 5xx，但 `database.py` 的 `localhost` 是硬编码，不方便改 | 需要一个"不改文件也能把连接指向别处"的办法 | **monkey patch 换掉 `database.SessionLocal`**（做法见下一节） |

### 三种"连不上"，只有一种会等超时

| 情况 | 谁在回应 | 结果 | 耗时 |
|---|---|---|---|
| 端口没开（如 `127.0.0.1:3307`） | 有机器，回复"我这儿没这个端口"（RST） | `ConnectionRefusedError` | **立刻** |
| 地址不存在 / 无路由 | 网络设备回复"到不了"（ICMP） | 立刻失败（错误码不同） | **立刻** |
| **地址无人应答（黑洞）** | **没人回话** | 一直等到**自己的超时** | **到超时上限**（2.05 / 5.13 秒） |

**测超时只能用第三种。** 用拒绝连接的地址，测出来的永远是"立刻失败"，根本不是超时。

### 验证超时的做法（不改代码，monkey patch）

目标：证明"数据库连不上时，`/ask` 是卡死还是 5 秒后返回 500"。难点：`DATABASE_URL` 里主机是硬编码的 `localhost`，改了要改回来，容易漏。

做法是**在程序启动前，把 `database.SessionLocal` 这块路标改指到黑洞地址**。临时文件放在 `%TEMP%`，不碰仓库：

```python
import sys
sys.path.insert(0, r"D:\Code\fastapi-learn\service")   # ① 让 Python 找得到 database.py

import database                                        # ② 载入它（此时 SessionLocal 指向 localhost）

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BAD_URL = "mysql+pymysql://root:x@10.255.255.1:3306/tutor_ai?charset=utf8mb4"
bad_engine = create_engine(BAD_URL, connect_args={"connect_timeout": 5})   # ③ 造"指向黑洞"的 engine
database.SessionLocal = sessionmaker(bind=bad_engine, autoflush=False)     # ④ 换路标

from main import app                                   # ⑤ 最后才载入 main.py
```

启动和测试：

```powershell
# 用 8001 端口，避开日常的 8000
uvicorn bad_db_app:app --port 8001
```

```python
# 掐表发一个 /ask，看状态码和耗时
body = json.dumps({"question": "直角三角形"}, ensure_ascii=False).encode("utf-8")
req = urllib.request.Request("http://127.0.0.1:8001/ask", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
t0 = time.perf_counter()
try:
    urllib.request.urlopen(req)
except urllib.error.HTTPError as e:
    print(f"状态码 {e.code}，耗时 {time.perf_counter()-t0:.2f}s")   # → 500，5.13s
```

**为什么 ⑤ 必须最后：** `main.py` 第 5 行是 `from database import SessionLocal`，这行在 **`import main` 那一瞬间**执行，等于"把当时的路标复制一份存到 main 里"。

```
先换路标 → 再 import main    ⇒ main 拿到的是黑洞路标 ✅
先 import main → 再换路标    ⇒ main 早就复制走 localhost，白换 ❌
```

**为什么"好 engine 和坏 engine 同时存在"不是问题：** 名字只保存最后一次赋的值，第 ④ 行一赋值，`SessionLocal` 就只指向坏的；好 engine 从此没人引用，进程结束一起消失。**证据是结果本身**——如果运行时拿的是好 engine，`/ask` 应该返回 200 和题库答案；实测是 500 / 5.13 秒，说明拿的确实是坏的。

**为什么 `import database` 不会执行两遍：** Python 把载入过的模块存在 `sys.modules` 里，第二次 `import` 直接取缓存。

**顺带一条衔接：** 这个手法就是 pytest 里 `monkeypatch.setattr(...)` 干的事。第 13 天给"服务异常"写用例时，用的是同一招，只是换成官方写法。

### 今天真正记住的几件事

- **`connect_timeout` 管"造新连接要多久"**（含 TCP 握手和密码认证）；**`pool_timeout` 管"等现成连接要多久"**（池子忙时排队）。一个是"连不上"，一个是"排不上队"，两个都设才封死。
- **池子容量 = `pool_size`(5) + `max_overflow`(10) = 15**，溢出连接用完就关；第 16 个才开始排队，抛 `TimeoutError`。
- **`TimeoutError`（借不到连接）和 `OperationalError`（连不上/断开/认证失败）是两个不同异常**，Day 10 的重试要按它们区分。
- **超时 ≠ 失败**：超时只是"失败得早、失败得干净"，之后仍要自己决定重试还是报错。
- **一个接口卡住不会拖死整个服务**：实测同时发 `/health`，仍 0.037 秒返回。
- **monkey patch 三要点**：模块属性可以重新赋值、`import` 顺序决定复制到哪个值、`sys.modules` 保证只载入一次。

### 明天（day10）要做的事

- 新建 `service/retry.py`：最多重试 2 次、间隔 0.5 秒
- 只对"可重试异常"生效：`2003 timed out` 重试，`1045 Access denied` **不重试**
- 把 `/ask` 的数据库查询包进重试逻辑
- 手动制造故障，看日志是否出现"第 1 次重试 / 第 2 次重试 / 最终失败"
- 在 `resilience.md` 写第二条
---

## Day 10 学习记录（2026-11-17）

### 今天完成了什么

1. 新建 `service/retry.py`：`is_retryable()` 只认可重试异常，`retry_call()` 最多重试 2 次、间隔 0.5 秒
2. 把 `/ask` 的查库动作收进内部函数 `do_query`，再包进 `retry_call`
3. 手动把库端口从 3306 改成 3307，亲眼看到"第 1 次重试 / 第 2 次重试 / 最终失败"三行日志，以及 13.26 秒后的 500
4. 在 `docs/resilience.md` 写第二条（重试）：哪些错误码重试、为什么是 2 次 0.5 秒、为什么不无限重试、实测数据
5. 弄清一条最重要的结论：**重试解决的是"瞬时故障"，不是"持续故障"**

### 实测记录

| 检查 | 结果 |
|---|---|
| `is_retryable(OperationalError(2003, timed out))` | **True**（可重试） |
| `is_retryable(OperationalError(1045, Access denied))` | **False**（不可重试，立刻上抛） |
| 正常 `POST /ask`（"直角三角形"） | **200，173.5 ms**，匹配到题库答案，日志**没有**"重试"字样 |
| 正常 `GET /history` | **200，11.7 ms** |
| 故障 `POST /ask`（本机手测，库端口改 3307） | **500，总耗时 13.26 秒**，三行日志齐 |
| 故障 `POST /ask`（助手侧验证，`127.0.0.1:3307`，`connect_timeout=2`） | **500，7.17 秒**，三行日志齐 |
| 直连 `localhost:3307`（量"积极拒绝"的真实耗时） | **2.06 秒**（Windows 会先试 IPv6 `::1` 再试 IPv4） |

**本机日志的四个时间点：**

| 时间 | 内容 | 距上一行 |
|---|---|---|
| 17:31:38.908 | 收到问题 | — |
| 17:31:43.000 | `[WARNING] 第1次重试`（2003，WinError 10061 积极拒绝） | 4.09 秒 |
| 17:31:47.575 | `[WARNING] 第2次重试` | 4.57 秒 |
| 17:31:52.163 | `[ERROR] 最终失败：已重试2次，放弃` → 随后 `POST /ask 500` | 4.59 秒 |

**13.26 秒的账：**

```text
3 次尝试 × 约 4.1 秒 ≈ 12.3 秒
2 次间隔 × 0.5 秒    =  1.0 秒
合计                 ≈ 13.3 秒
```

一次尝试要 4.1 秒，**不是 `connect_timeout=5` 在起作用**——"积极拒绝"本该立刻返回。实测直连 `localhost:3307` 单次要 2.06 秒，pymysql 会把 IPv6 和 IPv4 都试一遍，所以变成 4 秒。**这条说明：超时和重试是叠加的，用户等的时间 = 尝试次数 × 单次耗时 + 间隔总和。**

### 遇到的问题和解决方式

| # | 现象 | 真正的原因 | 怎么解决 |
|---|---|---|---|
| 1 | `if exc.orig.args[0] in RETRYABLE_CODE` 后面少冒号 | Python 的 `if` / `for` / `def` 行尾必须有 `:` | 补上 `:` |
| 2 | `is_retryable` 第二个分支直接 `return True` | 漏了"错误码在集合里"这个判断，1045 也会被当成可重试 | 改成 `return exc.orig.args[0] in RETRYABLE_CODES` |
| 3 | `isinstance(exc, PollTimeout)` | `Pool`（池）拼成了 `Poll`（投票），名字对不上就 `NameError` | 改成 `PoolTimeout` |
| 4 | `"%.1f 秒"` 写成了 `"%1.f 秒"` | `%1.f` 会被当成"宽度 1"，小数位没定义，输出被截成整数 | 用 `%.1f`；实测 `"%1.f" % 0.5` 输出 `0` |
| 5 | `IndentationError: expected an indented block after 'for' statement on line 18` | `for` 循环体整段没缩进 | 循环里的每行统一退 4 空格 |
| 6 | `max_tries=2` 配 `range(max_tries+1)` | 名字说"2 次"，实际会跑 3 次，口径打架 | 改名 `max_retries`（**重试** 2 次，首次不算重试），配 `range(max_retries+1)` |
| 7 | Pylance 报黄标 `Import "retry" could not be resolved from source` | 编辑器静态分析找不到模块（VS Code 打开的是仓库根，`service` 不在分析路径），**不是运行报错** | 先不管，跑起来正常 |
| 8 | 测完忘了把端口改回 3306 | 改端口是"手动造故障"的代价：文件里留了错的配置 | 核对发现后改回 3306，再打一次 `/ask` 确认 200 |

### 一个坑：两种"超时"不是一家人

| 名字 | 从哪来 | 什么时候抛 |
|---|---|---|
| `sqlalchemy.exc.TimeoutError`（项目里别名 `PoolTimeout`） | SQLAlchemy | 从连接池借连接排队超过 `pool_timeout` |
| `TimeoutError` | Python 内置 | 网络 / 文件等 IO 超时（socket 层） |

**两者没有任何继承关系**，`except TimeoutError` 抓不到池超时。所以必须显式 `from sqlalchemy.exc import TimeoutError as PoolTimeout`，起别名避免和内置的撞名。

### 验证重试的做法（不改代码，换 SessionLocal）

思路和 Day 9 验证超时一样：**在程序启动前把"路标"换掉**。但这次要换的是 `main` 里的那个名字：

```python
import sys
sys.path.insert(0, r"D:\Code\fastapi-learn\service")

import main                                    # 先导入 main（此时它已经持有一个正常的 SessionLocal）

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

bad = create_engine("mysql+pymysql://root:x@127.0.0.1:3307/tutor_ai",
                    connect_args={"connect_timeout": 2}, pool_timeout=2)
main.SessionLocal = sessionmaker(bind=bad, autoflush=False)   # 改的是 main 里的名字
app = main.app
```

**为什么改 `main.SessionLocal` 而不是 `database.SessionLocal`：** `main.py` 第 5 行是 `from database import SessionLocal`——**import 那一刻就把名字复制过去了**。之后再改 `database` 里的那个，`main` 完全不知道。这是"赋值是复制，不是绑定"的一个实例。

临时模块放在 `%TEMP%\retryprobe\`，起在 8003，测完杀进程、删目录，仓库零改动。

### 今天问过的疑问（速查）

- `type(ex).__name__` → 类名字符串，如 `"OperationalError"`
- `ex.args` → 参数元组，`args[0]` 是 MySQL 错误码
- 集合 `{2003, 2006, 2013}` → 花括号、自动去重、无序，判断用 `in`
- `isinstance` → 认父类；`type()` 只认完全相等，抓异常一律用 `isinstance`
- 类名带括号 = 造实例；`class X(Exception)` 只是定义模具
- 继承 `Exception` 才能被 `raise` / `except` 认，参数会自动进 `args`
- `TimeoutError as PoolTimeout` → `as` 只改后一个名字
- `pool_timeout=5` 是**参数**（等几秒），`PoolTimeout` 是**异常**（超了抛出来），不是一回事
- 2003 连不上 / 2006 被服务端踢 / 2013 中途断——都是连接问题，不是 SQL 写错
- `raise` 立刻退出整个函数，不是 `break`
- 函数能用模块级全局变量 + 外层函数的局部变量；别人函数里的看不到
- 重试次数 ≠ 尝试次数：`max_retries=2` 配 `range(max_retries+1)` 会跑 3 次
- 自己复述的三轮流程（首次 → 第 1 次重试 → 第 2 次重试 → 放弃）已核对正确

### 今天真正记住的几件事

- **重试解决"瞬时故障"，不解决"持续故障"**：数据库真挂了，重试只是把 5 秒变成 16 秒
- **重试会放大等待**：用户等的时间 = 尝试次数 × 单次耗时 + 间隔总和
- **按错误码决定重不重试**：`2003 / 2006 / 2013` 和池超时重试；`1045 / 1049 / 1064` 立刻上抛
- **`raise` 会立刻中断整个函数**，连 `for` 一起跳出——它不是 `break`
- **内部函数能直接借用外层的 `db`、`keyword`**（因为生在 `ask` 里面）；挪到模块级就必须传参，`retry_call` 也得加 `*args`
- **异常长这样**：`type(ex).__name__` 拿类名、`ex.args` 是元组（`args[0]` 是错误码）、`ex.orig` 是底层 pymysql 抛的那个、`isinstance` 认父类而 `type()` 不认
- **"积极拒绝"和"沉默超时"是两种失败**：拒绝 ~2 秒/次（本机实测），沉默要等满 `connect_timeout`

### 明天（day11）要做的事

- 给 `POST /ask` 加请求头 `X-Request-ID`（可选，不传则服务端生成）
- 给 `ask_logs` 加一列 `request_id VARCHAR(64)`，加唯一索引
- `/ask` 收到请求先查同 `request_id`：有就直接返回上次结果，不重复查库、不重复落库
- 手测两条：同一 ID 连发两次（只多一条记录、返回相同结果）；不同 ID 发两次（多两条记录）
- 在 `resilience.md` 写第三条（幂等）
- 记住：**幂等解决的是"重复请求"，和超时、重试是三件不同的事**

## Day 11 学习记录（2026-11-17）

### 今天完成了什么

**1. 数据库：`ask_logs` 加一列 + 唯一索引**

```sql
ALTER TABLE ask_logs ADD COLUMN request_id VARCHAR(64) NULL;
ALTER TABLE ask_logs ADD UNIQUE INDEX uk_ask_logs_request_id (request_id);
```

18:03:33 执行、COMMIT 生效。验证结果：

```text
列:   ['id', 'question', 'matched', 'created_at', 'request_id']
索引: [('uk_ask_logs_request_id', True)]
```

**2. `models.py`：`AskLog` 多一个字段**

```python
request_id: Mapped[str | None] = mapped_column(String(64), unique=True)
```

**3. `main.py`：接请求头、取号、打日志、落库**

```python
from fastapi import Depends, FastAPI, Header
import uuid

@app.post("/ask")
async def ask(req: AskRequest, db: Session = Depends(get_db),
              x_request_id: str | None = Header(default=None, alias="X-Request-ID")):
    request_id = x_request_id or uuid.uuid4().hex
    logger.info(f"收到问题：{req.question!r}，request_id={request_id}")
    ...
    db.add(AskLog(question=req.question, matched=matched, request_id=request_id))
```

**4. 幂等查重：`_CACHE` + 命中提前返回**

```python
_CACHE: dict[str, dict] = {}

    if request_id in _CACHE:
        logger.info(f"命中幂等，request_id={request_id}，直接返回上次结果")
        return _CACHE[request_id]

    # ……正常处理……
    resp = {...}
    _CACHE[request_id] = resp
    return resp
```

**查重写在 `db.add` 之前**，命中就 `return`，走不到插库——这是"不重复落库"的真正实现方式。

### 实测记录

**取号：**

```text
不带头    → request_id=e6858906a5bc4d26b6b7b48119e5e805   （自动生成 32 位）
头=abc    → request_id=abc                                  （用了传进来的）
```

**落库：**

```text
id=15  request_id='demo1'                            （手填）
id=16  request_id='95033be800d54490aaeaf100c0efd615'  （自动生成）
id=14  request_id=None                              （加列前的老数据）
```

**幂等（18:45）：**

```text
idem-A 第 1 次  → 正常处理
idem-A 第 2 次  → 返回内容与第 1 次完全相同（True）；日志："命中幂等，request_id=idem-A，直接返回上次结果"
idem-B、idem-C  → 各处理一次
```

```text
TOTAL = 19
ROW 19 'idem-C' / 18 'idem-B' / 17 'idem-A' / 16 自动生成 / 15 'demo1' / 14 None
CNT idem-A = 1     CNT idem-B = 1     CNT idem-C = 1
```

**4 次请求只新增 3 条记录。** 本人另在 `/docs` 上按清单手测一遍（`test-1` 连发两次、`test-2` / `test-3` 各一次），结果一致。

### 遇到的问题和解决方式

**1. `ModuleNotFoundError: No module named 'pymysql'`**

原因：命令里的 `python` 指向的是**基础环境 `D:\anaconda`**，而 pymysql 只装在 `D:\anaconda\envs\fastapi_learn`。traceback 里的路径 `D:\anaconda\Lib\site-packages\sqlalchemy` 就是证据。

解决：命令一律写全路径 `D:\anaconda\envs\fastapi_learn\python.exe`；或先在当前窗口把环境目录前置到 `$env:Path`。

**2. 第一次核验时库里还是 4 列、0 个索引**

说明那两条 `ALTER` 没有真正执行成功（或没 COMMIT）。重跑后才有 `request_id` 列和 `uk_ask_logs_request_id`。

**3. VS Code 提示 `Failed to save 'main.py': The content of the file is newer`**

原因：文件被外部（助手）改过磁盘内容，编辑器手里还是旧版本，VS Code 拒绝保存以防覆盖。

解决：**绝不能点 `Overwrite`**（会用编辑器旧内容盖掉磁盘改动）。正确做法是先点 `Compare` 看差异，确认没有自己的独家改动后，`Ctrl+Shift+P` → **`File: Revert File`（文件: 还原文件）**，让编辑器重新从磁盘读取。

**4. 为什么 `$env:DB_PASSWORD` 那行自己不用写**

因为 `DB_PASSWORD` 是用户环境变量，你自己新开的终端会自动继承。助手那次要写，是因为它的窗口在设置变量之前就启动了，没继承到。

### 请求头这一坨怎么记住

**一句话：一个盒子两个名字。**

```text
对方那边：请求头写着  X-Request-ID: abc     ← 外面的名字（alias）
                ↓ 发请求
你这边：  放进变量    x_request_id           ← 代码里的名字
```

- 头 = **请求信封上的几行小字**（`Content-Type`、`User-Agent`、`X-Request-ID` 都是头）；信封里的信纸才是请求体
- `Header(default=None)` = 没带这个头时给空（`None`）；`Header(1)` = 没带时给 `1`
- `_CACHE` 初始是空的，**第一次查必然 miss，处理完顺手存一份，第二次才 hit**——"边查边存"

### 验证幂等的做法（不改代码）

**第一步：确认 `/docs` 里 `POST /ask` 出现了 `X-Request-ID` 输入框**（说明新代码已加载）。

**第二步：记条数**

```powershell
& 'D:\anaconda\envs\fastapi_learn\python.exe' -c "from database import SessionLocal; from models import AskLog; db=SessionLocal(); print('总数 =', db.query(AskLog).count()); db.close()"
```

**第三步：`/docs` 里同一个 id 连发两次**

| 次数 | question | X-Request-ID |
|---|---|---|
| 1 | 直角三角形 | `test-1` |
| 2 | 直角三角形 | `test-1` |

预期：两次响应相同；第 2 次日志出现"命中幂等"。

**第四步：核对**

```powershell
& 'D:\anaconda\envs\fastapi_learn\python.exe' -c "from database import SessionLocal; from models import AskLog; db=SessionLocal(); print('test-1 条数 =', db.query(AskLog).filter(AskLog.request_id=='test-1').count()); db.close()"
```

预期：总数只 +1，`test-1 条数 = 1`。

**第五步：换两个不同 id（`test-2`、`test-3`）各发一次**，预期总数再 +2。

### 今天问过的疑问（速查）

- `alias="X-Request-ID"` 没理解 —— 外面叫这个名字，代码里叫 `x_request_id`
- 盒子是不是既叫 `X-Request-ID` 又叫 `x_request_id` —— 是，同一个东西两边叫法不同
- 加个 `None` 是干什么的 —— "可能是空"
- 这个"头"又是什么 —— 请求信封上的小字，跟请求体不是一回事
- `Header(1)` 是什么效果 —— 没带这个头时值就是 `1`
- 为什么第三个参数会给我一个输入框 —— `/docs` 是自动生成的测试前端，替你往头上塞值
- 为什么第二个参数 `db` 不用填 —— 它写的是 `Depends`，程序自己造
- `request_id = x_request_id or uuid.uuid4().hex` 是什么 —— 有号用左，没号用右
- `_CACHE` 是空字典怎么查 —— 边查边存，第一次必然不命中
- 没前端哪来幂等键 —— 手填固定串（`test-1`）就是有效的幂等键
- 手填算不算"真正的幂等" —— 算，只是号由人肉生成
- 一直运行才能往字典里加吗 —— 是，重启就清空
- 对数据库做了什么 —— 加一列 + 加一个唯一索引

### 今天真正记住的几件事

- **`request_id in _CACHE` 要放在 `db.add` 之前**，否则命中也会先插一条
- **唯一索引是数据库层的最后一道闸**，代码查重漏了它还能兜住
- **兜底生成的号不防重**：每次都是新号，重发就是新请求
- **`_CACHE` 只在进程内存里活着**：重启清空、多进程各存各的，生产要换 Redis 或给 `ask_logs` 加 `answer` 列
- **幂等解决"重复请求"，超时解决"等太久"，重试解决"瞬时故障"**——三件事，各管一段

### 明天（day12）要做的事

- 把日志改成结构化格式：时间、级别、`request_id`、接口路径、耗时 ms、结果状态
- 确保 `/ask` 和 `/history` 的每条日志都能回答：谁调的、调了什么、花了多久、成功还是失败
- `resilience.md` 补一张三者关系表（超时 / 重试 / 幂等）
- 自查：不看代码口述——一次 `/ask` 进来，超时在哪层生效、重试在哪层生效、幂等在哪层生效
- `git commit -m "day12: timeout + retry + idempotency + structured logging"` 并 push

## Day 12 学习记录（2026-11-17）

### 今天完成了什么

**1. 日志改成结构化（拼 JSON 写法）**

`main.py` 加 `import json`，四个出口 + 入口 + `/history` 全部改成"人话 + JSON 字段"：

```python
logger.info(json.dumps({"msg": "匹配到题库", "request_id": request_id,
                        "path": "/ask", "method": "POST", "question_id": row.id,
                        "duration_ms": round((time.perf_counter()-start)*1000, 1),
                        "status": "matched"}, ensure_ascii=False))
```

- 入口：`start = time.perf_counter()` 记起点
- 出口 4 个：`bad_request` / `idempotent_hit` / `unmatched` / `matched`（最后一个多带 `question_id`）
- `/history`：加了 `X-Request-ID` 参数，日志带 `path="/history"`、`count`、`duration_ms`、`status="ok"`

**2. `resilience.md` 补了第四部分**：三者关系表 + "一次 /ask 里三者在哪一层生效" + 结构化日志说明 + `status` 取值表。

**3. 提交**：`git commit -m "day12: timeout + retry + idempotency + structured logging"` 并 push（Day 9—11 的改动全部装进这一个提交）。

### 实测记录（2026-11-17 23:08）

**四条验收：**

```text
{"msg": "收到问题", "request_id": "f-1", "path": "/ask", "method": "POST", "question": "直角三角形"}
{"msg": "匹配到题库", "request_id": "f-1", "path": "/ask", "method": "POST", "duration_ms": 58.1, "status": "matched", "question_id": 4}
{"msg": "命中幂等，直接返回上次结果", "request_id": "f-1", "path": "/ask", "method": "POST", "duration_ms": 0.2, "status": "idempotent_hit"}
{"msg": "查询历史记录：最近20条", "request_id": "f-2", "path": "/history", "method": "GET", "count": 20, "duration_ms": 5.0, "status": "ok"}
{"msg": "问题为空，已拦截", "request_id": "f-3", "path": "/ask", "method": "POST", "duration_ms": 0.2, "status": "bad_request"}
```

| # | 验收项 | 结果 |
|---|---|---|
| 1 | `/ask` 命中 | `duration_ms=58.1`、`status=matched`、`question_id=4` ✅ |
| 2 | 同 id 第二次 | `duration_ms=0.2`、`status=idempotent_hit` ✅（58.1 → 0.2，日志自证省了一次查库） |
| 3 | `/history` | `path=/history`、`count=20`、`5.0 ms`、`ok` ✅ |
| 4 | 空问题 | `bad_request`、`0.2 ms` ✅ |

### 遇到的问题和解决方式

**1. `extra` 不能乱用：格式串是全局的**

`logger.info("msg", extra={...})` 只是把字段挂到记录上，要显示出来必须改 `basicConfig` 的 `format` 加占位。但**格式串一改，全项目每条日志都要求那几个字段**——`retry.py` 的三行重试日志、`/health`、`echo=True` 的 SQL 回显都不带 `request_id`，实测每条都刷：

```text
--- Logging error ---
ValueError: Formatting field not found in record: 'request_id'
```

**解决：改用"拼 JSON 进 message"**，格式串一个字不动，只影响改过的那几行。

**2. 字典里用 `=` 而不是 `:`**

写成 `"path"="/ask"` → `SyntaxError`。**字典里全是冒号，只有函数参数用等号。**

**3. 表达式加了引号，变成死字符串**

写成 `"duration_ms":"round((time.perf_counter()-start)*1000,1)",` → 虽然引号闭合后语法能过，但日志里打出的是那串**代码原文**：

```text
"duration_ms": "round((time.perf_counter()-start)*1000,1)"
```

**这个错是日志自己暴露的**——别的出口都是 `0.2`、`5.0`，只有命中那条是一坨文字。**删掉引号才算出数字。**

**4. 引号只开不闭 → `unterminated string literal`**

报错行号会直接指出哪一行，照着行号看引号。

### 一次 /ask 的完整时间线

```text
① 请求到达
   FastAPI 解析：body → req.question，请求头 → x_request_id
② 定编号
   request_id = x_request_id or uuid.uuid4().hex
③ 记"来过"
   入口日志：{"msg":"收到问题", request_id, path, method, question}
④ 空值检查
   空白？ → 是：打 bad_request 日志 → 返回 400（结束）
⑤ 【第 1 层・幂等】查 _CACHE
   这个 id 处理过？ → 是：打 idempotent_hit 日志 → 返回上次结果（结束，不碰数据库）
⑥ 【第 2 层・重试】查库，最多 3 次尝试、间隔 0.5 秒
   └ 每次尝试内部：【第 3 层・超时】
      取连接 pool_timeout 5 秒；连库 connect_timeout 5 秒
      超时/连不上 → 抛异常交回重试判断
        不可重试（1045 等）→ 立刻上抛
        可重试（2003/2006/2013/池超时）→ 隔 0.5 秒再试
        试满 2 次 → "最终失败" → 500
⑦ 落库
   db.add(AskLog(..., request_id=request_id)) + db.commit()
⑧ 出结论日志（按走的那条路，只打一条）
   matched / unmatched
⑨ 返回响应
```

**三层的位置关系：**

| 层 | 包住的范围 | 命中的后果 |
|---|---|---|
| 幂等（最外） | ⑤—⑨ 整段 | 直接跳过 ⑥⑦⑧，返回旧结果 |
| 重试（中间） | 只包 ⑥ 的查库动作 | 同一动作重复执行，⑦⑧ 照常走 |
| 超时（最内） | ⑥ 里的一次尝试 | 单次放弃，由重试决定是否再来 |

**为什么不能颠倒：** 幂等必须在落库前，否则重复请求已经插进去了；重试必须包住动作，包不住就没法重复；超时只管"这一次等多久"，管不了"试几次"。

**一句话：越靠外越早决定"做不做"，越靠内越晚决定"还等不等"。**

### 今天问过的疑问（速查）

- 日志里字段顺序有关系吗 —— 没关系，按名字取值；要紧的是名字别拼错
- 为什么不能用 `extra` —— 它要改全局格式串，会波及重试日志和 SQL 回显
- `basicConfig` 的 `format` 是什么 —— 所有日志共用的模板
- 括号是不是多了 —— `logger.warning(json.dumps({...}))` 是两对，内层给 `json.dumps`、外层给 `logger.warning`
- 字典里为什么有的用 `:` 有的用 `=` —— 字典用冒号，函数参数用等号
- 为什么值加了引号就不对 —— 加引号是文字，不加才是计算结果
- `time.perf_counter()` 和 `time.time()` 差在哪 —— 前者是掐表只增不减，后者是挂钟会被校时
- 算耗时为什么 ×1000 —— `perf_counter` 返回秒，要毫秒得乘
- `round(...,1)` 干什么 —— 留一位小数，去掉 `59.3827261` 这种噪音
- 为什么 `status` 要固定几档 —— 自由文本没法统计，枚举才能聚合
- `matched` 和 `unmatched` 都是 200 为什么要分开 —— 业务没查到不算错，但字段得区分
- 提交哈希 hash 是什么 —— 提交的身份证号，清单里记前 7 位
- 先提交再写复盘会不会漏文件 —— 会，所以顺序是先写复盘、再提交、清单最后补 hash

### 今天真正记住的几件事

- **`extra` 的代价是全局的**：格式串一改，所有日志都得带字段，包括改不到的 SQL 回显
- **拼 JSON 只影响改过的那几行**，是这个项目最省事的路
- **字典用 `:`，函数参数用 `=`**，写反就是语法错误
- **表达式别加引号**，加了就成死文本——这个错日志自己会告诉你
- **`perf_counter` 掐表算耗时，`time` 看挂钟记时刻**
- **`status` 枚举化才能真正统计**：`matched` / `unmatched` / `idempotent_hit` / `bad_request` / `ok`
- **三层顺序：幂等在门口、重试在中间、超时在最里**

### 下一批（第 13 天起）要做的事

按清单口径：**pytest 接口自动化，20+ 用例**，覆盖正常 / 缺参 / 非法输入 / 越界 / 服务异常；顺便给超时、重试、幂等各补用例（`is_retryable` 的判定、`retry_call` 的次数、幂等命中不重复落库）。可以看黑马教程里 pytest 那部分，或者直接看 pytest 官方文档。