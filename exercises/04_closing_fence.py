"""练习：已知开启围栏的符号和长度，判断当前行能否关闭代码块。"""


def is_closing_fence(line, fence_char, opening_length):
    # 输入约定：line 是单行文本，fence_char 为反引号或 ~，opening_length >= 3。
    # 本题不解析列表、引用容器或开启围栏；空白预处理已提供。
    marker = line.rstrip("\r\n")
    unindented = marker.lstrip(" ")
    indent = len(marker) - len(unindented)
    if indent > 3:
        return False
    candidate = unindented.rstrip(" \t")

    # TODO 1：candidate 的长度少于 opening_length 时，立即返回 False。
    if (len(candidate) < opening_length):
        return False
    # TODO 2：逐字符遍历 candidate；发现任何字符不等于 fence_char，
    # 立即返回 False。不要只检查第一个字符或使用 count() 统计总数。
    for char in candidate:
        if (char != fence_char):
            return False

    # TODO 3：所有检查通过后返回 True，注意放在字符循环外。
    return True


if __name__ == "__main__":
    cases = [
        ("同长度", "```", "`", 3, True),
        ("更长", "`````", "`", 4, True),
        ("太短", "```", "`", 4, False),
        ("不同符号", "~~~", "`", 3, False),
        ("波浪号", "~~~~", "~", 3, True),
        ("混合符号", "```~", "`", 3, False),
        ("尾随文字", "```python", "`", 3, False),
        ("允许的空白", "   ``` \t\r\n", "`", 3, True),
        ("缩进过多", "    ```", "`", 3, False),
        ("空行", "\n", "`", 3, False),
        ("中间空格", "`` `", "`", 3, False),
        ("普通正文", "正文", "`", 3, False),
    ]
    for name, line, char, length, expected in cases:
        actual = is_closing_fence(line, char, length)
        assert actual is expected, f"{name}：期望 {expected!r}，实际 {actual!r}"
        print(f"{name}：通过")
