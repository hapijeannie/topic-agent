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
