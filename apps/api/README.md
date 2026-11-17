# Python 后端

当前包含 Markdown 解析、章节分块与只读 CLI 预览；FastAPI 健康接口已通过本地 HTTP 验证，数据库与模型调用尚未接入。

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

官方资料：[FastAPI 入门](https://fastapi.tiangolo.com/tutorial/first-steps/) 与 [Vercel FastAPI 入口](https://vercel.com/docs/frameworks/backend/fastapi) 。已核对路由、返回 JSON 与入口约定；尚未进行线上部署验证。

## 数据库连接检查

在仓库根目录执行：

```bash
npm run db:check
```

输入：用户配置的 `apps/api/.env.local` 中的 DATABASE_URL，或进程已有的同名环境变量。已有环境变量优先，不会被本地文件覆盖；脚本按自身位置查找文件，不依赖终端工作目录。

流程：加载配置 → 连接 PostgreSQL（连接超时１０秒）→ 执行 SELECT 1 → 验证结果 → 关闭连接。只检查连接，不建表、不写数据、不检查文章表是否存在。不会读取或改动博客配置。

成功输出 `Database connection successful.`，退出码为０；缺少配置、连接失败或结果异常时退出码为１。失败提示不包含原始数据库异常、连接字符串或密码。不要把配置值贴入聊天或日志。

脚本使用 python-dotenv 读取环境文件、psycopg 连接数据库；不改变 FastAPI 的 /health，也不会让应用自动加载环境文件。首次拉取代码需先执行 `.venv/bin/python -m pip install -r apps/api/requirements.txt`。

官方资料：[Psycopg 连接、查询与资源关闭](https://www.psycopg.org/psycopg3/docs/basic/usage.html) 、[python-dotenv 环境变量优先级](https://bbc2.github.io/python-dotenv/) 。

## 数据库表结构

`schema.sql` 保存首版 articles 与 chunks 建表 SQL，显式使用 public schema。已获授权在本地连接配置指向的 neondb 执行并核验，两表初始均为空；应用尚未接入文章保存。

该文件只用于首次初始化，不能重复执行，也不会在启动或部署时自动执行。其他数据库或分支须先核对目标及同名表，并确认 schema 操作授权；执行时将整个文件放在一个事务中。
