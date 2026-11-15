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
