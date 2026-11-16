# 最小存储方案（待确认数据库目标，未执行）

## 范围与选择

沿用既有 PostgreSQL 方向，后续接 pgvector，避免先做另一套存储再迁移。本步只保存文章和分块，不创建向量列、不启用扩展、不调用模型。只支持新增、重复跳过、内容变化报告冲突；不更新、不删除、不引入版本表或分块规则版本。

用户已提供 L／S 岗位全文，见 `docs/job-requirements.md`；S 明确要求 Python，L 强调 RAG 与全栈交付。当前 shell PATH 中未找到 psql 或 docker，不能由此认定机器完全未安装或没有远程服务。目标实例、独立数据库名称和访问方式待确认；不读取博客环境配置，不连接其生产数据库。

## 输入、输出与流程

输入：现有合成 Markdown `tests/fixtures/chunk_preview/sample.md`，source=demo、ownership=owned；不修改输入文件。

首次导入：返回 status=imported、chunk_count=2，数据库新增一篇文章及两个分块。
原样重试：返回 status=duplicate，记录总数不增加。
同来源标识、不同内容：返回 status=conflict，已有文章与分块保持不变。

流程：解析 → 根据来源与 source_id 查询 → 判断重复或冲突 → 新文章分块 → 单篇事务中插入文章和全部分块 → 成功提交后报告 imported。分块写入失败时整篇回滚。批量输入按篇提交，单篇失败不撤销此前已成功的文章。

## 拟议表结构

以下 SQL 仅为审阅文本，不是已执行的迁移。仅用于本项目独立数据库中不存在同名表的情况；初始化应显式执行，不能在每次导入时偷偷建表。

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

- 计划新增 storage 模块、显式建表 SQL，复用 ingestion 与 chunking，现有 preview 保持只读；随后同一功能阶段提供 FastAPI 导入接口与 Next.js 上传页。CLI 只作调试入口，不继续单独扩展为最终产品。
- PostgreSQL 驱动拟使用 Psycopg，标准库和现有 PyYAML 不提供 PostgreSQL 连接；获准实施后核对官方用法及依赖版本，只安装到项目 .venv。
- 验收新增一次、原样重复、内容冲突、分块写入失败回滚，保留原有２４项测试。真实数据库测试前确认专用测试目标，不对博客库运行测试，不用仅有 mock 的通过结果声称入库完成。
- 用户只需亲自运行一次导入及一次重复导入，解释记录数为何不变；不新增独立算法练习。

## 审批边界

待确认具体独立 PostgreSQL 目标后，再请求批准在该目标执行上述两表创建。风险是指定数据库新增表和测试记录；不得覆盖已有表，不改博客库，不安装全局依赖，不写 .env 或输出连接凭据。本方案文档更新不等于获准执行 schema 或基础设施配置。

官方依据（本轮已打开核对）：[约束](https://www.postgresql.org/docs/current/ddl-constraints.html) 与 [事务](https://www.postgresql.org/docs/current/tutorial-transactions.html) 。方案尚未经数据库执行验证。
