"""组合练习：复用开启／关闭围栏识别，按章节分块并标记超长。"""

from pathlib import Path
from runpy import run_path


# 加载你已完成的函数，不运行各文件的 __main__ 检查；本段无需修改。
# 数字开头的练习文件名不能直接写在普通 import 语句中。
exercise_dir = Path(__file__).resolve().parent
parse_opening_fence = run_path(str(exercise_dir / "05_opening_fence.py"))["parse_opening_fence"]
is_closing_fence = run_path(str(exercise_dir / "04_closing_fence.py"))["is_closing_fence"]
mark_chunks = run_path(str(exercise_dir / "03_mark_oversized.py"))["mark_chunks"]


def split_sections(body):
    chunks = []
    current_lines = []
    active_fence = None

    for line in body.splitlines(keepends=True):
        if active_fence is not None:
            # TODO 1：调用 is_closing_fence，传入当前行、已记录的 char 和 length。
            # 仅当返回 True 时，将 active_fence 设回 None。
            if (is_closing_fence(line, active_fence["char"], active_fence["length"])):
                active_fence = None
        else:
            # TODO 2：调用 parse_opening_fence(line)，结果保存为 opening。
            # opening 不是 None 时，将它赋给 active_fence。
            # 否则，若当前行是二级标题且 current_lines 非空，
            # 保存上一块并重置 current_lines（复用第二题的写法）。
            opening = parse_opening_fence(line)
            if opening is not None:
                active_fence = opening
            elif line.startswith("## ") and current_lines:
                chunks.append("".join(current_lines))
                current_lines = []

        # 沿用第二题：每一行都保留，包括开启与关闭围栏。
        current_lines.append(line)

    if current_lines:
        chunks.append("".join(current_lines))
    return chunks


def preview_chunks(body, max_chars):
    # TODO 3：先调用 split_sections，再把结果交给 mark_chunks，返回标记结果。
    return mark_chunks(split_sections(body), max_chars)


if __name__ == "__main__":
    cases = [
        ("普通章节", "## A\n正文\n## B\n", ["## A\n正文\n", "## B\n"]),
        ("语言围栏", "## A\n```python\n## 隐藏\n```\n## B", ["## A\n```python\n## 隐藏\n```\n", "## B"]),
        ("不能提前关闭", "## A\n````md\n```\n## 隐藏\n````\n## B", ["## A\n````md\n```\n## 隐藏\n````\n", "## B"]),
        ("不同符号不能关闭", "~~~\n```\n## 隐藏\n~~~\n## B", ["~~~\n```\n## 隐藏\n~~~\n", "## B"]),
        ("关闭行不能有语言名", "```\n```python\n## 隐藏\n```\n## B", ["```\n```python\n## 隐藏\n```\n", "## B"]),
        ("多个代码块", "```\n## 隐藏一\n```\n~~~\n## 隐藏二\n~~~\n## B", ["```\n## 隐藏一\n```\n~~~\n## 隐藏二\n~~~\n", "## B"]),
        ("缩进与 CRLF", "导语\r\n## A\r\n   ~~~py\r\n## 隐藏\r\n  ~~~~ \t\r\n## B", ["导语\r\n", "## A\r\n   ~~~py\r\n## 隐藏\r\n  ~~~~ \t\r\n", "## B"]),
        ("未闭合", "## A\n```python\n## 隐藏", ["## A\n```python\n## 隐藏"]),
        ("无标题", "正文\n\n", ["正文\n\n"]),
        ("空正文", "", []),
    ]
    for name, body, expected in cases:
        actual = split_sections(body)
        assert actual == expected, f"{name}：期望 {expected!r}，实际 {actual!r}"
        assert "".join(actual) == body, f"{name}：原文发生变化"
        records = preview_chunks(body, 8)
        assert records == mark_chunks(expected, 8), f"{name}：标记结果不一致"
        print(f"{name}：分块、原文保留与标记通过")
