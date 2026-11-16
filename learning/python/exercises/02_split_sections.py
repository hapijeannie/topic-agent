"""练习：按代码块外的二级标题分块，完整保留正文与换行。"""


def split_sections(body):
    chunks = []
    current_lines = []
    in_code_block = False

    for line in body.splitlines(keepends=True):
        # 只在识别围栏时移除换行；存储时仍使用原始 line。
        marker = line.rstrip("\r\n")

        # TODO 1：遇到围栏时切换状态。
        # 注意：围栏本身也要保留，不能直接 continue 丢掉它。
        if (marker == '```'):
            in_code_block = not in_code_block

        # TODO 2：遇到块外的二级标题，且 current_lines 非空时，
        if (line.startswith('## ') and current_lines and not in_code_block):
            chunks.append("".join(current_lines))
            current_lines = []
        # 将已有行拼成字符串加入 chunks，然后将 current_lines 重设为空列表。
        # 当前标题属于新块，不属于上一块。

        # TODO 3：每一行都加入 current_lines，包括标题、空行和围栏。
        current_lines.append(line)

    # TODO 4：循环结束后，如果还有尚未保存的行，将最后一块加入 chunks。
    if (current_lines):
        chunks.append("".join(current_lines))
    return chunks


if __name__ == "__main__":
    cases = [
        ("两个章节", "## A\n正文 A\n## B\n正文 B", ["## A\n正文 A\n", "## B\n正文 B"]),
        ("标题前导语", "导语\n## A\n正文", ["导语\n", "## A\n正文"]),
        ("代码块保护", "## A\n```\n## 伪标题\n```\n## B\n", ["## A\n```\n## 伪标题\n```\n", "## B\n"]),
        ("没有标题", "正文\n\n结尾\n", ["正文\n\n结尾\n"]),
        ("空正文", "", []),
        ("连续标题", "## A\n## B", ["## A\n", "## B"]),
        ("标题前缀", "### A\n##无空格\n## B", ["### A\n##无空格\n", "## B"]),
        ("CRLF 与围栏", "## A\r\n```\r\n## 隐藏\r\n```\r\n## B", ["## A\r\n```\r\n## 隐藏\r\n```\r\n", "## B"]),
        ("未闭合围栏", "## A\n```\n## 隐藏", ["## A\n```\n## 隐藏"]),
    ]
    for name, body, expected in cases:
        actual = split_sections(body)
        assert actual == expected, f"{name}：期望 {expected!r}，实际 {actual!r}"
        assert "".join(actual) == body, f"{name}：原文发生变化"
        print(f"{name}：通过")
