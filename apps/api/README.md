# Python 后端

当前包含 Markdown 解析、章节分块与只读 CLI 预览；FastAPI 服务、数据库与模型调用尚未接入。

- `topic_agent/`：业务代码，不导入学习练习。
- `tests/`：unittest，fixtures 为合成素材。
- `requirements.txt`：后端依赖，安装到仓库根目录 `.venv`。

从本目录运行：

```bash
../../.venv/bin/python -m unittest discover -s tests -v
../../.venv/bin/python -m topic_agent.preview tests/fixtures/chunk_preview --source demo --ownership owned --max-chars 7
```

根目录运行方式和安装说明见 [项目 README](../../README.md) 。本目录作为未来 Python 部署边界，暂未添加部署配置。
