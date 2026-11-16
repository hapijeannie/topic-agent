"""练习：保留每块原文，添加序号、字符数和超长标记。"""


def mark_chunks(chunks, max_chars):
    # 输入约定：chunks 是字符串列表，max_chars 是正整数。
    # 参数校验已提供，本题只填写循环内的三个 TODO。
    if type(max_chars) is not int or max_chars <= 0:
        raise ValueError("max_chars 必须是正整数")

    results = []
    for index, text in enumerate(chunks):
        # TODO 1：使用 len() 计算 text 的字符数，保存为 char_count。
        char_count = len(text)

        # TODO 2：创建字典 record，包含以下四个键：
        # "index"：当前序号，从 0 开始。
        # "text"：原始 text，不截断、不去空白。
        # "char_count"：刚计算的字符数。
        # "oversized"：字符数严格大于 max_chars 时为 True，否则为 False。
        record = {
            "index": index,
            "text": text,
            "char_count": char_count,
            "oversized": char_count > max_chars
        }

        # TODO 3：将 record 加入 results。
        results.append(record)

    return results


if __name__ == "__main__":
    cases = [
        ("短于、等于和超过预算", ["ab", "abc", "abcd"], 3, [2, 3, 4], [False, False, True]),
        ("中文与换行", ["你好\n", "A\r\nB"], 3, [3, 4], [False, True]),
        ("完整保留代码", ["```\nprint(1)\n```"], 5, [16], [True]),
        ("空列表", [], 3, [], []),
        ("空字符串", [""], 3, [0], [False]),
    ]
    for name, chunks, budget, lengths, flags in cases:
        before = chunks.copy()
        actual = mark_chunks(chunks, budget)
        assert len(actual) == len(chunks), f"{name}：块数不一致"
        for index, record in enumerate(actual):
            expected = {
                "index": index,
                "text": chunks[index],
                "char_count": lengths[index],
                "oversized": flags[index],
            }
            assert record == expected, f"{name}：期望 {expected!r}，实际 {record!r}"
            assert type(record["oversized"]) is bool, f"{name}：标记必须是布尔值"
        assert chunks == before, f"{name}：输入被修改"
        print(f"{name}：通过")

    for invalid in (0, -1, 1.5, "3", True):
        try:
            mark_chunks([], invalid)
        except ValueError:
            continue
        raise AssertionError(f"非法预算未被拒绝：{invalid!r}")
    print("非法预算：通过")
