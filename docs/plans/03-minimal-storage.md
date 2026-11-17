# 最小存储方案（两表已创建，事务存储已实现）

2026-11-17：用户报告 `npm run import:sample` 符合预期。随后新增本地 `POST /documents` 和上传页。同一合成身份返回 duplicate。页面尚未部署。

2026-11-17 实施：新增 topic_agent/storage.py，复用现有 Document 与分块列表。采用 INSERT ON CONFLICT DO NOTHING 后读取原指纹，避免先查询再插入的身份竞争；不增加更新策略或重试框架。返回 status、article_id、chunk_count，重复／冲突返回已有记录的信息。新增 import_sample.py 作为个人验收入口，用户运行一次新增和一次重复；不新增算法练习。数据库自动验证使用外层回滚事务及随机来源，测试行不持久保留，自增序列可能前进。

2026-11-17 执行记录：用户明确批准创建两表，使用本项目 apps/api/.env.local 指向的连接；只读核对实际数据库为 neondb、schema 为 public，无同名关系。随后在单一事务执行 apps/api/schema.sql，并通过新连接核对全部字段、主键、外键、联合唯一约束和 CHECK 约束；两表记录数均为０。未改环境配置、未写文章、未启用向量扩展。仅对该连接目标执行，不代表 Preview／Production 的其他分支也已建表。

## 范围与选择

沿用既有 PostgreSQL 方向，后续接 pgvector，避免先做另一套存储再迁移。本步只保存文章和分块，不创建向量列、不启用扩展、不调用模型。只支持新增、重复跳过、内容变化报告冲突；不更新、不删除、不引入版本表或分块规则版本。

用户已提供 L／S 岗位全文，见 `docs/job-requirements.md`；S 明确要求 Python，L 强调 RAG 与全栈交付。已使用独立 Neon 资源 fuxi-db，本地连接目标为 neondb/public；环境配置由用户管理，不读取博客环境配置，不连接其生产数据库。

## 输入、输出与流程

输入：现有合成 Markdown `apps/api/tests/fixtures/chunk_preview/sample.md`，实际 import:sample 命令使用 source_namespace=storage-demo、ownership=owned；不修改输入文件。

首次导入：返回 status=imported、chunk_count=2，数据库新增一篇文章及两个分块。
原样重试：返回 status=duplicate，记录总数不增加。
同来源标识、不同内容：返回 status=conflict，已有文章与分块保持不变。

实际流程：解析 → 分块 → 开启事务 → INSERT ON CONFLICT DO NOTHING → 已存在则读取指纹并报告重复／冲突，新文章则插入全部分块 → 提交后报告 imported。分块写入失败时整篇回滚。当前接口一次处理一篇，未实现批量上传。

## 已执行表结构

以下为已批准的表结构，实际执行文件为 apps/api/schema.sql，显式指定 public schema。仅适用于不存在同名表的数据库；不要重复执行，不能在每次导入时自动建表。

```sql
CREATE TABLE articles (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_namespace text NOT NULL,
    source_id text NOT NULL,
    ownership text NOT NULL CHECK (ownership IN ('owned', 'reference')),
    title text NOT NULL,
    source_path text NOT NULL,
    raw text NOT NULL,
    body text NOT NULL,
    metadata jsonb NOT NULL,
    content_hash text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (source_namespace, source_id)
);

CREATE TABLE chunks (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    article_id bigint NOT NULL REFERENCES articles(id),
    chunk_index integer NOT NULL CHECK (chunk_index >= 0),
    text text NOT NULL,
    UNIQUE (article_id, chunk_index)
);
```

metadata 保留已有 Frontmatter 的简介、发布声明、日期和未知字段。source_path 保存导入文件的来源路径，用于引用回溯；不是自动抓取链接。char_count 可从文本计算，oversized 依赖预览预算，暂不持久化。重复导入以原始内容指纹为准；来源集合保持稳定，归属或来源路径的变更不在本步提供更新入口。

不使用级联删除。保留文章原文和分块正文，后续可据 article_id 回查来源。尚无多租户或账号访问控制，只能作为本地／私人开发入口使用。

## 实施改动与验收

- storage 模块、建表 SQL、FastAPI 导入接口与 Next.js 上传页已存在；preview 保持只读，CLI 只作调试入口。
- 已安装 Psycopg 到项目 .venv，依赖版本记录在 apps/api/requirements.txt；没有安装全局依赖。
- 验收新增一次、原样重复、内容冲突、分块写入失败回滚，保留原有２４项测试。真实数据库测试前确认专用测试目标，不对博客库运行测试，不用仅有 mock 的通过结果声称入库完成。
- 用户只需亲自运行一次导入及一次重复导入，解释记录数为何不变；不新增独立算法练习。

## 审批边界

上述两表已获用户批准并创建。后续 schema 变更、迁移或对其他分支初始化仍须单独确认；不得覆盖已有表，不改博客库，不写 .env 或输出连接凭据。当前下一步是网页真实验收，不需重新建表。

官方依据（此前已打开核对）：[约束](https://www.postgresql.org/docs/current/ddl-constraints.html) 与 [事务](https://www.postgresql.org/docs/current/tutorial-transactions.html) 。建表与存储事务已有真实数据库验证记录，最新状态以 ROADMAP.md 为准。
