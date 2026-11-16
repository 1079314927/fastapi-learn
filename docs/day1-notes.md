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

