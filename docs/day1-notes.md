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
