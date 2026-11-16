# 分块只读预览实施计划

> 执行方式：使用 executing-plans，在当前 main 工作区按已批准范围实施，不另建工作树。

## 已批准设计

将练习中的围栏保护、二级标题分块和超长标记接入现有只读预览。业务模块不导入 exercises；保留用户练习。内部保留完整分块原文，命令行仅输出摘要。无新依赖、不写数据库、不调用模型、不发布。

输入：已有 Markdown 文件、来源、归属，以及字符预算。示例正文 `## A\n甲\n## B\n乙`、预算 6，输出两块，字符数 7 和 6，只有第一块超长。

流程：读取原始字节 → parse_markdown → Document.body → 分块与标记 → 文章预览附加 chunk_count、oversized_count、chunks（序号、字符数、标记）。保留现有重复／冲突状态及退出码语义。

## 接口与文件

- 新增 `topic_agent/chunking.py`：`chunk_body(body: str, max_chars: int) -> list[dict]`；每条包含 index、text、char_count、oversized。预算必须为正整数，拒绝布尔值。空字符串返回空列表。
- 修改 `topic_agent/preview.py`：`preview_directory(directory, source, ownership, max_chars=1000)`；CLI 新增 `--max-chars`，默认 1000，仅为可调整的预览阈值，不宣称最佳切片长度或模型 token 上限。非法 CLI 预算由 argparse 拒绝；函数调用返回顶层 error。
- 新增 `tests/test_chunking.py`，扩展 `tests/test_preview.py`；README、阶段、每日记录与 ROADMAP 同步。

## 支持边界与评审重点

- 仅行首 `## ` 划分章节；前导正文保留为独立块。保持原始换行、围栏及正文，超长只标记。
- 围栏支持反引号／波浪号、连续长度、语言说明、至多三个前导空格；块内只匹配关闭。未闭合则保留至末尾。
- 不宣称完整 Markdown 解析，不处理列表／引用容器、HTML 或缩进代码块语义。
- 测试覆盖 CRLF 原文保留、短关闭／异符号／带文字关闭不误切、空正文／前导正文、预算相等／非法预算、CLI 不泄露正文及旧重复／冲突流程不变。

## 实施与验证

- [x] 添加行为测试，先运行确认新增能力缺失时失败。
- [x] 实现分块模块与预览接入，不修改练习文件。
- [x] 运行完整 unittest，使用合成 Markdown 做只读 CLI 验收，验证输入字节不变。
- [x] 检查 diff，更新文档和真实验证记录。
- [ ] 用户亲自运行样例并解释输出，作为业务接入后的学习验收。

## 实际验证

- 初次运行新增测试：缺少 chunking 模块导致导入错误，缺少摘要字段导致 KeyError，CLI 未识别 --max-chars 导致断言失败；明确记录为能力缺失阶段，不声称全部是行为断言失败。
- 实现后 `.venv/bin/python -m unittest discover -s tests -v`：２４项全部通过，含原有１５项。
- 合成文件 `tests/fixtures/chunk_preview/sample.md`：预算 7 时字符数 8、7，标记 True、False；预算 8 时均 False。两次 CLI 均退出０，ready=1，原文件 SHA-256 一致，未输出正文。
- 本次未重新扫描真实博客文章，不将旧的七篇解析验收说成新的分块验收。未增加依赖，未提交或推送。
- 遵守项目不自动创建子对话的约定，本轮由主助手检查改动与测试，无独立子代理审查。
