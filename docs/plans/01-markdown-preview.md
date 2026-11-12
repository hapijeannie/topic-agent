# Markdown 只读导入预览实施计划

目标：先交付可运行的 Python 解析核心与命令行预览，供后续网页上传复用；不声称第一版五项已经完成。

依据：`docs/project-brief.md` 第一版五项；用户已批准执行。本次由主助手实现辅助解析和校验，正文切片作为后续个人练习，不替用户完成。

## 范围与接口

- `topic_agent/ingestion.py`：`parse_markdown(raw: str, source_namespace: str, ownership: str) -> Document`，只接受带 Frontmatter 的文章，title 必填，slug 或 id 必有其一；保留原文、正文、未知元数据。ownership 显式传 owned 或 reference，source_namespace 用于区分来源集合。
- Document 保存 source_id、title、description、body、raw、metadata、declared_status、published_at、content_hash。元数据日期转换为 ISO 文本；draft 为布尔才映射为来源声明状态，不代表线上验证。
- `topic_agent/preview.py`：通过 `python -m topic_agent.preview DIRECTORY --source NAME --ownership owned|reference` 预览目录顶层 .md 文件。JSON 输出摘要及逐文件错误，不默认输出全文；任一文件失败返回非零，继续报告其他文件。
- 同批相同标识且同内容标记 duplicate，不同内容标记 conflict 并失败；跨批次和数据库幂等本次不实现。
- 不自动猜缺失标识和标题，不执行 YAML 对象标签；拒绝重复字段、非法日期、非布尔 draft、空正文。

## 依赖与资料

- Python 标准库提供 SHA-256、日期校验、命令行参数和 unittest。
- PyYAML 6.0.3：标准库无 YAML 解析，项目尚无同类依赖；选择安全加载器，补充重复键检查，避免手写不完整的 YAML 解析器。
- 已打开 [PyYAML 文档](https://pyyaml.org/wiki/PyYAMLDocumentation) 和 [官方发布页](https://github.com/yaml/pyyaml/releases/tag/6.0.3)，发布说明包含 Python 3.14 支持；闭合 PR 页面本次读取失败，维护响应速度未核实，不宣称已全面审计依赖。
- [hashlib 文档](https://docs.python.org/3/library/hashlib.html)：SHA-256 摘要；不用于语义相似度。
- [CommonMark 代码块规范](https://spec.commonmark.org/0.31.2/#fenced-code-blocks)：用于后续切片练习。此步不渲染或重写正文。

## 步骤

- [x] 先添加解析与 CLI 的行为测试，缺少模块时预期失败；该首次运行包含缺失模块导致的导入及 JSON 错误，不将其记为完整行为验收。
- [x] 实现解析、元数据校验、来源标识与原始文本哈希；运行解析测试。
- [x] 实现只读批次预览，验证混合成功失败、重复标识、空目录与错误路径。
- [x] 全套１５项测试通过；对原博客７篇文章运行预览，前后文件哈希一致。
- [x] 更新 README、阶段计划、ROADMAP 和每日记录；本地提交记录以 git log 为准，不自动推送。

## 重点检查

引号内冒号与多行简介必须正确解析；CRLF 正文保留；未知字段不丢；YAML 重复字段不静默覆盖；来源声明与实际发布状态严格区分。上述均以合成样本测试。跨来源同 slug 不冲突，同来源同 slug 的差异版本不擅自覆盖。

## 下一学习点

用户完成切片规则讨论与小练习后，再实现切片；然后准备数据库 schema 的具体方案供用户确认。当前命令行仅是底层验证入口，正式交付仍为网页工作台。
