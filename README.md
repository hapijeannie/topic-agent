# 公众号选题与写作知识 Agent

工作名：`content-agent`。

用于长期积累文章、链接、图片和灵感，查询历史选题，发现值得延伸的角度，并在人工确认后创建和执行写作任务。

核心链路：身份与权限 → 必要信息补全 → 知识检索 → 业务记录查询 → 任务草稿 → 人工确认与执行 → 失败恢复 → 结果验收。

## 当前使用方式

当前已实现 Markdown 只读解析预览，尚无网页、数据库写入或向量化。Python 核心后续供网页上传复用，命令行不是最终产品界面。

在项目根目录运行（本次验证环境为 Python 3.14.7）：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m topic_agent.preview /path/to/markdown --source technical-blog --ownership owned
.venv/bin/python -m unittest discover -s tests -v
```

`--source` 是稳定的来源集合名；`--ownership` 必须显式指定 `owned`（自己的文章）或 `reference`（外部参考）。混合归属的目录需分批处理，程序不猜作者归属。

只读取目录顶层 `.md` 文件，输出 JSON 元信息和逐文件错误，不打印全文或修改文件。成功退出码为０，存在解析错误、同标识内容冲突或无可处理文件时为１。输出的 `ready` 只表示解析通过，不表示已入库或可检索。`declared_status` 是文件头的发布声明，不是线上核验。

支持带 Frontmatter 的文章，title 和 slug／id 必填。重复键、非法日期、非布尔 draft、空正文会报错；保留未知字段，暂不支持 YAML 别名。正文不重写。批内重复检测已实现，跨批入库幂等待数据库阶段实现。

## 文档入口

- [项目规范](AGENTS.md)
- [真实进度](ROADMAP.md)
- [需求与边界](docs/project-brief.md)
- [第一阶段：基线理解与素材导入](docs/stages/01-baseline-and-ingestion.md)
- [首次项目记录](docs/daily/2026-11-12.md)

原博客继续独立运行，本项目不直接改写其文件或数据库。
