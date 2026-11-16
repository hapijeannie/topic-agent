"""练习：补全两处 TODO，只识别代码块外的二级标题。"""


def find_headings(body):
    in_code_block = False
    headings = []

    for line in body.splitlines():
        if line == "```":
            # TODO 1：将 in_code_block 取反，再赋值给自己。
            in_code_block = not in_code_block
            continue

        # TODO 2：不在代码块内且以 "## " 开头时，将 line 加入 headings。
        if line.startswith('## ') and (not in_code_block):
            headings.append(line)

    return headings


if __name__ == "__main__":
    body = """## 缓存失效
更新文章后，需要清除旧缓存。
```
## 这是代码中的文字
```
## 缓存更新
下一次访问时重新生成缓存。
"""
    assert find_headings("## 标题\n正文") == ["## 标题"]
    assert find_headings(body) == ["## 缓存失效", "## 缓存更新"]
    assert find_headings(body.replace("\n", "\r\n")) == [
        "## 缓存失效",
        "## 缓存更新",
    ]
    assert find_headings("") == []
    print("四组练习检查通过。")
