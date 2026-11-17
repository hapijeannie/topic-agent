# 公众号选题与写作知识 Agent

工作名：`content-agent`。

本地目录：`/Users/yanjun/Desktop/study/ai/fuxi-pro`。CLI 接续先读 AGENTS.md、ROADMAP.md 和当前阶段文档；迁移记录见 [2026-11-13](docs/daily/2026-11-13.md)。

用于长期积累文章、链接、图片和灵感，查询历史选题，发现值得延伸的角度，并在人工确认后创建和执行写作任务。

核心链路：身份与权限 → 必要信息补全 → 知识检索 → 业务记录查询 → 任务草稿 → 人工确认与执行 → 失败恢复 → 结果验收。

## 目标形态与技术选型

最终为精简网页工作台：Next.js 展示素材导入、检索引用、选题与任务确认；Python FastAPI 提供核心业务接口；PostgreSQL／pgvector 保存业务数据和向量。采用 Python 主要为匹配 S 岗位的明确语言要求，岗位依据见 [L／S 要求与映射](docs/job-requirements.md) 。

优先按上传入库、RAG 检索问答、Agent 确认创建任务依次交付，RAG 初版即建立固定评测集。先完成最小闭环，版本管理、多租户、多 Agent 等后续推进。

部署方向为 Vercel 上的 Next.js 与 FastAPI，加独立 PostgreSQL；健康接口已上线，Neon 已接入本地开发，新导入接口与网页尚未部署。后续公开部署需单独确认。Docker 后续独立练习验收，平台部署不替代容器化技能。当前命令行只用于开发验证。

## 仓库结构

```text
apps/
  api/                     # Python 业务代码、测试和依赖
  web/                     # Next.js 工作台，目前只有素材入库页
learning/python/
  notes/                   # 学习笔记与 imgs 配图
  exercises/               # 个人练习
docs/                      # 需求、岗位、计划、阶段和学习记录
AGENTS.md                  # 协作与目录约定
ROADMAP.md                 # 唯一进度源
```

不预建共享 packages 或引入构建编排。沿用根目录 `.venv`，不移动虚拟环境；Python 包名仍为 `topic_agent`。下面命令均从仓库根目录执行；在后端目录内执行的方法见 [API README](apps/api/README.md) 。

## 当前使用方式

当前已实现 Markdown 解析、章节分块、两表事务保存、`POST /documents` 和本地上传页。向量化和模型调用尚未实现。命令行仍是调试入口。

FastAPI 入口位于 `apps/api/main.py`。健康接口已部署；导入接口只在本地验证，尚未重新部署。根目录执行 `npm run dev:api` 启动，`npm run test:api` 运行测试。接口说明见 [API README](apps/api/README.md) 。

在项目根目录运行（本次验证环境为 Python 3.14.7）：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r apps/api/requirements.txt
PYTHONPATH=apps/api .venv/bin/python -m topic_agent.preview /path/to/markdown --source technical-blog --ownership owned
PYTHONPATH=apps/api .venv/bin/python -m unittest discover -s apps/api/tests -v
```

`--source` 是稳定的来源集合名；`--ownership` 必须显式指定 `owned`（自己的文章）或 `reference`（外部参考）。混合归属的目录需分批处理，程序不猜作者归属。

只读取目录顶层 `.md` 文件，输出 JSON 元信息和逐文件错误，不打印全文或修改文件。成功退出码为０，存在解析错误、同标识内容冲突或无可处理文件时为１。输出的 `ready` 只表示解析通过，不表示已入库或可检索。`declared_status` 是文件头的发布声明，不是线上核验。

支持带 Frontmatter 的文章，title 和 slug／id 必填。重复键、非法日期、非布尔 draft、空正文会报错；保留未知字段，暂不支持 YAML 别名。正文不重写。预览提供批内重复检测；实际存储根据来源集合、来源标识及内容指纹实现跨次重复跳过，内容变化时事务覆盖文章及分块，保留文章 ID。

本地网页使用：先安装后端 requirements 和前端依赖 `npm install --prefix apps/web`，按 [后端登录配置](apps/api/README.md#个人登录配置) 配置数据库与 GitHub OAuth，然后分别在两个终端执行 `npm run dev:api` 和 `npm run dev:web`，访问 http://localhost:3000 。页面包含上传、素材列表、正文及分块详情，只允许指定 GitHub 账号访问；鉴权配置缺失时拒绝素材访问。真实 GitHub 登录及完整网页验收待配置后完成，下一步见 [路线图](ROADMAP.md#下一步执行顺序) 。

## 分块预览：输入、输出与执行流程

输入为 Markdown 目录和正整数字符预算。`--max-chars` 默认 1000，是可调整的预览阈值，不是 token 限制或最佳切片长度。超过预算只标记，不截断、不丢弃，也不会单独导致非零退出码。非法预算的 CLI 退出码为２。

可直接运行合成样例：

```bash
PYTHONPATH=apps/api .venv/bin/python -m topic_agent.preview apps/api/tests/fixtures/chunk_preview --source demo --ownership owned --max-chars 7
```

样例文件：[sample.md](apps/api/tests/fixtures/chunk_preview/sample.md) 。正文为 `## A\n甲乙\n## B\n乙\n`，末尾包含换行。预期完整报告仍包含现有来源、状态等信息，每篇文章新增以下字段：

```json
{
  "chunk_count": 2,
  "oversized_count": 1,
  "chunks": [
    {"index": 0, "char_count": 8, "oversized": true},
    {"index": 1, "char_count": 7, "oversized": false}
  ]
}
```

执行流程：读取原始字节 → 解析 Frontmatter 与正文 → 仅将正文传入 `chunk_body` → 保护代码围栏并按行首 `## ` 分块 → 计算字符数和超长标记 → 输出摘要。文件头不参与正文分块，换行计入字符数。

内部接口 `topic_agent.chunking.chunk_body(body, max_chars)` 返回包含 `text` 原文的字典列表；命令行输出只包含序号、字符数和标记，不输出分块正文。预览不生成持久化 ID；实际保存时由数据库生成文章与分块 ID。

支持范围：行首二级标题、标题前导语、反引号／波浪号围栏、围栏长度匹配与语言说明。保留原文和换行，未闭合围栏保护到末尾。不实现完整 Markdown 的列表／引用容器、HTML 与缩进代码块语义；当前摘要仅供只读预览，不等于可入库或可检索。

个人验收：先运行上面的命令，再将预算改为 8；应仍为两块，但两个 `oversized` 都为 false。解释为什么末尾换行也被计数、预算改变为什么不改变分块数量。

## 文档入口

- [项目规范](AGENTS.md)
- [真实进度](ROADMAP.md)
- [需求与边界](docs/project-brief.md)
- [第一阶段：基线理解与素材导入](docs/stages/01-baseline-and-ingestion.md)
- [首次项目记录](docs/daily/2026-11-12.md)

原博客继续独立运行，本项目不直接改写其文件或数据库。
