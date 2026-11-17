# Python 后端

## 个人登录配置

先安装更新后的依赖：在根目录运行 `.venv/bin/python -m pip install -r apps/api/requirements.txt`。新增 Authlib 处理 OAuth，itsdangerous 签名会话，HTTPX 提供异步 HTTP 客户端与测试支持。

由用户在 `apps/api/.env.local` 中保留 DATABASE_URL，并填写以下配置；不要将真实值提交或发到聊天：

```dotenv
GITHUB_CLIENT_ID=你的OAuth应用ClientID
GITHUB_CLIENT_SECRET=你的OAuth应用ClientSecret
GITHUB_ALLOWED_USER_ID=你的GitHub数字ID
SESSION_SECRET=自行生成至少32字符的随机字符串
APP_URL=http://localhost:3000
```

在 GitHub 的 Settings → Developer settings → OAuth Apps 创建应用，本地 Homepage URL 填 `http://localhost:3000`，Authorization callback URL 填 `http://localhost:3000/backend/auth/callback`。数字 ID 是 GitHub 用户 API 返回的 `id`，不是用户名。随机会话密钥可自行运行 `.venv/bin/python -c 'import secrets; print(secrets.token_urlsafe(32))'` 生成，仅保存到环境配置。

两个终端分别运行 `npm run dev:api` 和 `npm run dev:web`，访问 http://localhost:3000/login 。全程使用同一个 localhost 地址，不混用 127.0.0.1。允许账号登录后进入列表；其他账号拒绝访问。未登录素材请求返回 401，配置缺失返回 503；`/health` 始终公开。写入与注销还要求 Origin 与 APP_URL 一致。

接口：`GET /documents?limit=20&offset=0` 返回 items、has_more；limit 为１至１００。`GET /documents/{id}` 返回正文、元数据及有序分块，不存在返回 404。`GET /auth/me` 返回当前身份，`POST /auth/logout` 清除会话。

GitHub token 不保存到浏览器会话；会话最长８小时，Cookie 为 HttpOnly、SameSite=Lax，HTTPS 环境另启用 Secure。注销只清除当前浏览器 Cookie。线上部署前需把 APP_URL 与 OAuth 回调改为前端 HTTPS 地址，并配置后端环境变量、前端服务端 API_URL；本次未改环境文件或部署。当前真实 GitHub 登录和完整网页链路待验收。

当前包含 Markdown 解析、章节分块、事务保存和 FastAPI 导入接口。健康接口已上线；`POST /documents` 已与本地 Next.js 上传页连接，新接口尚未部署。模型调用尚未实现。

- `topic_agent/`：业务代码，不导入学习练习。
- `tests/`：unittest，fixtures 为合成素材。
- `requirements.txt`：后端依赖，安装到仓库根目录 `.venv`。

从本目录运行：

```bash
../../.venv/bin/python -m unittest discover -s tests -v
../../.venv/bin/python -m topic_agent.preview tests/fixtures/chunk_preview --source demo --ownership owned --max-chars 7
```

根目录运行方式和安装说明见 [项目 README](../../README.md) 。本目录作为未来 Python 部署边界，暂未添加部署配置。

## 最小 API：个人填写与验收

直接在 `main.py` 填写真实应用的第一条路由，不另建重复练习。

- 输入：`GET /health`，无请求体和参数。
- 完整预期输出：HTTP 200，Content-Type 为 application/json，正文为 `{"status":"ok"}`。
- 流程：Uvicorn 接收请求 → FastAPI 匹配路由 → 调用 health → 把返回字典序列化为 JSON。
- API：FastAPI() 创建应用；@app.get 注册 GET 路由；def 定义函数；return 返回值。
- 个人填写已完成：用户返回包含 status 的字典。Python 字典需要显式写键和值，不支持 JS 对象属性简写。
- 验收：通过 npm 脚本启动后，实际 HTTP 请求返回 200、application/json 和 {"status":"ok"}。

在仓库根目录启动：

```bash
npm run dev:api
```

`main:app` 表示 main.py 中的 app 对象；`--app-dir` 指向后端目录；`--reload` 在修改后重新加载，仅供本地开发。

根目录 package.json 的 dev:api 执行 `.venv/bin/python -m uvicorn main:app --app-dir apps/api --reload`，无需先激活虚拟环境。`npm run test:api` 执行现有 unittest；npm 仅负责命令入口，Python 依赖仍由 pip 安装。

另开终端验证：

```bash
curl -i http://127.0.0.1:8000/health
```

health 只证明服务能响应，不检查数据库。完成本地验收后再部署 Vercel，项目 Root Directory 选择 apps/api；main.py 中的 app 是官方支持的入口。数据库创建与关联安排在服务部署后。

官方资料：[FastAPI 入门](https://fastapi.tiangolo.com/tutorial/first-steps/) 与 [Vercel FastAPI 入口](https://vercel.com/docs/frameworks/backend/fastapi) 。健康接口已通过线上验证；素材接口已接个人鉴权，尚未部署。

## 数据库连接检查

在仓库根目录执行：

```bash
npm run db:check
```

输入：用户配置的 `apps/api/.env.local` 中的 DATABASE_URL，或进程已有的同名环境变量。已有环境变量优先，不会被本地文件覆盖；脚本按自身位置查找文件，不依赖终端工作目录。

流程：加载配置 → 连接 PostgreSQL（连接超时１０秒）→ 执行 SELECT 1 → 验证结果 → 关闭连接。只检查连接，不建表、不写数据、不检查文章表是否存在。不会读取或改动博客配置。

成功输出 `Database connection successful.`，退出码为０；缺少配置、连接失败或结果异常时退出码为１。失败提示不包含原始数据库异常、连接字符串或密码。不要把配置值贴入聊天或日志。

脚本使用 python-dotenv 读取环境文件、psycopg 连接数据库；不改变 FastAPI 的 /health。应用启动也会加载后端环境文件，进程变量优先。首次拉取代码需先执行 `.venv/bin/python -m pip install -r apps/api/requirements.txt`。

官方资料：[Psycopg 连接、查询与资源关闭](https://www.psycopg.org/psycopg3/docs/basic/usage.html) 、[python-dotenv 环境变量优先级](https://bbc2.github.io/python-dotenv/) 。

## 数据库表结构

`schema.sql` 保存首版 articles 与 chunks 建表 SQL，显式使用 public schema。已获授权在本地连接配置指向的 neondb 执行并核验。应用通过 `POST /documents` 写入文章，不会在启动时执行这份 SQL。

该文件只用于首次初始化，不能重复执行，也不会在启动或部署时自动执行。其他数据库或分支须先核对目标及同名表，并确认 schema 操作授权；执行时将整个文件放在一个事务中。

## 文章与分块事务保存

业务入口：`topic_agent.storage.save_document(conn, doc, chunks, source_path)`。输入为解析后的 Document、包含 index／text 的分块列表，以及来源路径。metadata 使用 Psycopg 的 Jsonb 适配，正文通过参数化 SQL 传递。

流程：进入事务 → 尝试插入文章并获取 ID → 已有身份则锁定文章并比较指纹 → 相同返回 duplicate；不同则更新文章、删除旧分块并写入新分块，返回 updated → 新身份保存文章与分块，返回 imported。覆盖保留文章 ID 和首次创建时间。任一步失败都回滚文章及分块，恢复原有内容。

独立导入使用空闲的 autocommit 连接，函数内显式 transaction 控制整篇提交。若调用方已有外层事务，函数使用保存点，最终提交由调用方负责。不提供独立删除接口或历史版本管理。

### 个人验收

输入固定为仓库合成文件 `tests/fixtures/chunk_preview/sample.md`，来源集合 storage-demo、归属 owned；正文为两块。命令只访问本项目 `apps/api/.env.local` 指定的数据库，不使用 shell 中的同名变量覆盖目标。

在仓库根目录连续执行两次：

```bash
npm run import:sample
```

首次完整输出示例（article_id 由数据库生成，以实际值为准）：

```json
{"status":"imported","article_id":42,"chunk_count":2}
```

再次输出同一个 ID：

```json
{"status":"duplicate","article_id":42,"chunk_count":2}
```

首次运行会持久化一篇合成文章及两个分块；重复运行不增加记录。已有同身份不同正文时返回 updated、退出码０，原子替换文章与分块；其他失败输出固定提示，避免泄露连接信息。验收覆盖请另建合成文件，不修改既有 fixture。

### 验证命令

`npm run test:api` 默认运行本地测试并跳过数据库测试；`npm run test:db` 显式连接项目数据库，验证新增、重复、覆盖、来源隔离、列表详情及新增／覆盖失败时的回滚。测试使用随机来源集合和外层回滚事务，不留下文章记录；自增 ID 序列可能前进，因此 ID 不保证连续。

官方事务依据：[Psycopg 事务与嵌套保存点](https://www.psycopg.org/psycopg3/docs/basic/transactions.html) 。

## 导入接口

`POST /documents` 接收一篇 Markdown，不接收多个文件，也不建表。请求 JSON：

```json
{
  "raw": "---\ntitle: 分块演示\nslug: chunk-demo\n---\n## A\n甲乙\n## B\n乙111\n",
  "source_namespace": "storage-demo",
  "ownership": "owned",
  "source_path": "tests/fixtures/chunk_preview/sample.md"
}
```

`source_path` 可省略，默认 `upload`。流程：验证登录和 Origin → 校验来源路径 → 解析 Frontmatter → 按 1000 字符预算分块 → 读取 `DATABASE_URL`（进程环境变量优先于 `apps/api/.env.local`）→ 调用 `save_document`。成功时 HTTP 200，正文与存储函数相同，例如 `{"status":"duplicate","article_id":8,"chunk_count":2}`。`imported`、`duplicate`、`updated` 都是 200，由 `status` 区分。

缺字段返回 422。Markdown 或来源不合法返回 400，`detail` 为校验说明，且不会连接数据库。未配置数据库或连接失败返回 503。写入失败返回 500 和固定的 `Import failed.`，不返回驱动异常或连接信息。

本地已用同一篇合成文章请求该接口，返回 duplicate、article_id 为 8、chunk_count 为 2，说明先前样例导入仍在，本次没有新增第二篇。非法正文返回 400。上传页通过 Next.js 转发到这个接口，说明见 [工作台 README](../web/README.md) 。
