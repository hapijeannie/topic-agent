"""练习：识别开启围栏，返回符号和连续数量；不是开启围栏则返回 None。"""


def parse_opening_fence(line):
    # 沿用第四题的缩进规则；不解析列表或引用容器。
    marker = line.rstrip("\r\n")
    candidate = marker.lstrip(" ")
    if len(marker) - len(candidate) > 3 or not candidate:
        return None

    fence_char = candidate[0]
    if fence_char not in ("`", "~"):
        return None

    length = 0
    # TODO 1：逐字符遍历 candidate，统计开头连续的 fence_char。
    # 遇到不同字符就 break；相同则让 length 增加 1。
    for char in candidate:
        if (char == fence_char):
            length += 1
        else:
            break

    # TODO 2：连续数量不足 3 时，返回 None。
    if (length < 3):
        return None
    # 围栏后可以写 python 等说明；反引号围栏的说明中不能包含反引号。
    # 这条规则已提供，本题不要求解析或返回语言名。
    info = candidate[length:]
    if fence_char == "`" and "`" in info:
        return None

    # TODO 3：返回包含 "char" 和 "length" 两个键的字典。
    return {
        "char": fence_char,
        "length": length
    }


if __name__ == "__main__":
    cases = [
        ("普通围栏", "```", {"char": "`", "length": 3}),
        ("语言标记", "```python\n", {"char": "`", "length": 3}),
        ("更长围栏", "````markdown", {"char": "`", "length": 4}),
        ("波浪号", "~~~python", {"char": "~", "length": 3}),
        ("允许缩进", "   ~~~~ \r\n", {"char": "~", "length": 4}),
        ("数量不足", "``python", None),
        ("不能累计不连续符号", "~~x~~", None),
        ("反引号说明不合法", "```py`thon", None),
        ("波浪号说明允许反引号", "~~~py`thon", {"char": "~", "length": 3}),
        ("缩进过多", "    ```", None),
        ("普通正文", "正文", None),
        ("空行", "\n", None),
    ]
    for name, line, expected in cases:
        actual = parse_opening_fence(line)
        assert actual == expected, f"{name}：期望 {expected!r}，实际 {actual!r}"
        print(f"{name}：通过")
