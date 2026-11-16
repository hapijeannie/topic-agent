# 个人编码练习

所有学习用代码统一放在此目录，按 `01_topic_name.py` 编号命名。业务实现仍放在 `topic_agent/`，练习不直接接入业务模块。

协作方式：助手先解释 Python 语法和 API、提供骨架；用户填写 TODO；助手检查并运行验证。未填写的骨架不代表功能完成。

## ０１：识别代码块外的标题

编辑文件：[01_find_headings.py](01_find_headings.py) 。只需补充函数内两处 TODO。

本题限定：代码围栏是独占一行的三个反引号，没有语言标记和缩进；只识别以 `## ` 开头的标题。本题不覆盖完整 Markdown 规范。

| Python 写法 | JS／TS 对照 | 用途 |
|---|---|---|
| `def name(body):` | `function name(body) {}` | 定义函数，Python 使用缩进表示代码块 |
| `False`、`True` | `false`、`true` | 布尔值 |
| `not value` | `!value` | 取反 |
| `a and b` | `a && b` | 两个条件同时成立 |
| `body.splitlines()` | 类似 `body.split(/\r?\n/)` | 分行，也支持其他换行符 |
| `for line in lines:` | `for (const line of lines)` | 逐行遍历 |
| `line.startswith("## ")` | `line.startsWith("## ")` | 检查前缀 |
| `headings.append(line)` | `headings.push(line)` | 添加列表元素 |
| `continue` | `continue` | 跳过本轮剩余代码 |
| `pass` | 空语句 | 占位，填充逻辑后替换 |

在项目根目录运行：

```bash
.venv/bin/python exercises/01_find_headings.py
```

文件末尾的 `if __name__ == "__main__":` 表示直接运行文件时执行检查；导入文件时不执行。`assert` 用来核对实际结果，不符合预期时抛出 `AssertionError`。

本题已由用户填写并通过四组检查，以及三级标题／无空格标题、多个代码块、未闭合围栏三组额外检查。

## ０２：按标题保留正文分块

编辑文件：[02_split_sections.py](02_split_sections.py) 。填写四处 TODO，不必修改文件末尾的检查代码。

第一题返回标题列表；本题返回完整章节的字符串列表。使用 `current_lines` 暂存当前章节，遇到下一标题时保存上一章节，最后再保存末尾章节。

规则：沿用第一题的简化围栏与二级标题规则；标题属于新块；标题前的导语单独保留；没有标题时全文为一块；空正文返回空列表。保留所有空行、代码围栏与原始换行，拼回后必须等于输入。暂不处理长度预算，不接入业务模块。

新增语法与 API：

| Python | JS／TS 对照或含义 |
|---|---|
| `body.splitlines(keepends=True)` | 分行并保留每行的换行符；`keepends=True` 是具名参数 |
| `line.rstrip("\r\n")` | 去除末尾的 CR／LF 字符，仅用于识别围栏，不修改原始字符串 |
| `"".join(current_lines)` | 相当于 `current_lines.join("")`，不额外插入分隔符 |
| `if current_lines:` | 列表非空时成立；不同于 JS 中空数组也是真值 |
| `current_lines = []` | 让变量指向新的空列表 |

例如，输入 `"导语\n## A\n正文 A\n## B\n正文 B"`，期望输出：

```python
["导语\n", "## A\n正文 A\n", "## B\n正文 B"]
```

从项目根目录运行：

```bash
.venv/bin/python exercises/02_split_sections.py
```

本题已由用户完成：九组检查通过，且各组结果用 `"".join(...)` 拼接后与原文完全一致。

## ０３：标记超长分块

编辑文件：[03_mark_oversized.py](03_mark_oversized.py) 。填写三个 TODO，文件末尾是已提供的验收检查。

输入是第二题那样的字符串列表，本题独立练习，不要求导入前一题。输出为字典列表，每块包含序号 `index`、原文 `text`、字符数 `char_count` 和布尔标记 `oversized`。超长时保留整块，不截断、不拆分、不丢弃；等于预算不算超长。

本题按字符数练习流程，不是 token 计数，也不证明内容符合任何模型输入限制。Python 的 `len(str)` 计算 Unicode 码点，换行也计数；不是字节数或严格的视觉字符数。模型硬上限以后通过对应 tokenizer 检查。

| Python | JS／TS 对照与说明 |
|---|---|
| `len(text)` | 类似字符串长度，但与 JS 的 UTF-16 长度在部分字符上不同 |
| `for index, text in enumerate(chunks):` | 类似 `for (const [index, text] of chunks.entries())`，从 0 编号 |
| `record = {"name": "demo", "active": True}` | 类似 JS 对象；本题使用字符串键，不省略键和值 |
| `record["name"]` | 取字典字段，不使用 `record.name` |
| `count > limit` | 比较表达式直接得到布尔值，不必再写 if／else |
| `results.append(record)` | 类似 `results.push(record)` |

示例：`mark_chunks(["你好", "abcd"], 3)` 的期望结果：

```python
[
    {"index": 0, "text": "你好", "char_count": 2, "oversized": False},
    {"index": 1, "text": "abcd", "char_count": 4, "oversized": True},
]
```

参数校验已提供：`raise ValueError(...)` 类似 JS 的 `throw new Error(...)`；`type(...) is int` 在这里检查整数并排除布尔值。无需修改校验或测试部分。

运行：

```bash
.venv/bin/python exercises/03_mark_oversized.py
```

本题已由用户完成，预算边界、中文和换行、完整代码、空列表、空字符串及非法预算检查全部通过。

## ０４：判断关闭围栏

编辑文件：[04_closing_fence.py](04_closing_fence.py) 。填写三个 TODO，输入中的开启围栏符号和长度由调用方提供，本题不识别开启围栏。

目的：防止过早退出代码块后，把代码里的标题误当作章节边界。关闭围栏必须使用同一种符号，长度不少于开启围栏，不能混合其他字符；关闭围栏可以有至多三个前导空格，尾部只能是空格或制表符。

已打开核对 [CommonMark 0.31.2 第４.５节](https://spec.commonmark.org/0.31.2/#fenced-code-blocks) 的相关规则。本题仅练习独立行判断，不处理列表、引用容器或完整 Markdown 语法；空白预处理已提供，不必修改。

例如：`is_closing_fence("```", "`", 4)` 应返回 `False`，因为长度不足；`is_closing_fence("`````", "`", 4)` 应返回 `True`。

语法与 API：

| 写法 | 含义 |
|---|---|
| `len(candidate)` | 候选围栏的字符数 |
| `for char in candidate:` | 逐字符遍历字符串，类似 JS 的 `for (const char of candidate)` |
| `char != fence_char` | 判断字符是否不同 |
| `return False` | 立即退出整个函数，类似 JS 的 `return false` |
| `marker.lstrip(" ")` | 仅去除开头的普通空格 |
| `text.rstrip(" \t")` | 去除末尾的空格与制表符 |

区分：`continue` 仅跳到下一轮循环；`return` 结束整个函数。只有所有字符都符合要求才能返回 `True`，不能检查完第一个字符就返回。

运行与验收：

```bash
.venv/bin/python exercises/04_closing_fence.py
```

本题已由用户完成，十二组样例全部通过。不自动改写已完成的练习。

## ０５：识别开启围栏

编辑文件：[05_opening_fence.py](05_opening_fence.py) 。填写三个 TODO。

第四题需要调用方告诉它开启围栏的符号和数量，本题负责从开头行提取这些信息。例如输入 `"````python"` 返回 `{"char": "`", "length": 4}`；输入普通正文则返回 `None`。函数只应在代码块外用于识别开启围栏；块内应该使用第四题判断关闭，不能把代码中的类似文本当作新开启围栏。

依据前面已核对的 [CommonMark 第４.５节](https://spec.commonmark.org/0.31.2/#fenced-code-blocks) ：开启围栏至少包含三个连续的同类符号，允许尾随语言等说明；反引号围栏的说明中不得出现反引号。缩进检查与说明检查已提供。不解析列表、引用容器，也不提取语言字段。

| Python 写法 | 含义与 JS／TS 对照 |
|---|---|
| `None` | 表示没有结果，类似 JS 的 `null`；不是字符串 `"None"` |
| `candidate[0]` | 取第一个字符；空字符串会报错，所以前面已判空 |
| `length += 1` | 增加 1；Python 没有 JS 的 `length++` |
| `break` | 退出当前循环，继续执行循环后的代码；不是退出函数 |
| `candidate[length:]` | 从 length 位置取到末尾，类似 `candidate.slice(length)` |
| `"`" in info` | 判断字符串中是否包含反引号，类似 `.includes(...)` |
| `fence_char not in ("`", "~")` | 判断是否不属于两种允许的符号；括号内是元组 |

这次遇到不同字符时要 `break`，因为语言名是允许的。例如 `"```python"` 中，读到 `p` 时停止计数，得到 3，继续后面的校验。不能因为读到 `p` 就直接认定整行无效。

运行：

```bash
.venv/bin/python exercises/05_opening_fence.py
```

本题已由用户完成，十二组检查通过。下一步组合开启识别、关闭判断与章节分块，验证整条练习链路。

## ０６：组合分块与超长标记

编辑文件：[06_chunk_pipeline.py](06_chunk_pipeline.py) 。填写三处 TODO，加载辅助函数、逐行保存和末尾保存已提供。不修改前五题或业务模块。

本题把第二题的分块思路与第三、四、五题组合。第二题的布尔状态只能说明是否在块内；现在用 `active_fence` 同时记录块内状态、符号和长度。

| active_fence 的值 | 含义 | 当前行的处理 |
|---|---|---|
| `None` | 在代码块外 | 识别开启围栏；若不是围栏，才考虑标题分块 |
| `{"char": "`", "length": 4}` | 在四个反引号开启的块内 | 只检查能否关闭，不能按标题分块，也不能重新识别开启围栏 |

例如，读到四个反引号开启围栏后记录字典；随后读到三个反引号，关闭判断返回 False，保持原状态；读到四个反引号时才恢复 None。

新增或复用语法：

| 写法 | 含义 |
|---|---|
| `active_fence is None` | 判断是否没有活动代码块，类似 JS 的 `activeFence === null` |
| `active_fence is not None` | 判断是否正在代码块内 |
| `active_fence["char"]` | 读取已记录的符号；仅在字典非 None 时读取 |
| `if ...: / elif ...: / else:` | 对应 JS 的 if／else if／else，分支同级缩进 |
| `result = function(value)` | 调用函数并保存返回值；本题三个辅助函数已加载，可以直接调用 |

函数接口：

```python
parse_opening_fence(line)                 # 返回字典或 None
is_closing_fence(line, char, length)       # 返回布尔值
mark_chunks(chunks, max_chars)            # 返回带标记的字典列表
```

文件头的 `run_path` 用于加载固定的本地练习文件，返回可取出函数的字典；默认不会触发其 `if __name__ == "__main__"` 检查。`Path(__file__).resolve().parent` 定位当前文件所在目录。这段已提供，不是本题要填写的部分。

注意：判断一行时，只走块内或块外的一条分支；不能关闭后又在同一轮把同一围栏当成新的开启。每行仍然只保存一次。

运行：

```bash
.venv/bin/python exercises/06_chunk_pipeline.py
```

验收结果：用户已完成，十组用例的章节边界、原文拼接一致性和超长标记检查通过。标题仍仅识别行首 `## `；未覆盖完整 Markdown 的列表、引用、HTML 或缩进代码块，也未接入模型和数据库。用户反馈对整体流程仍困惑，先复盘样例，再评估业务模块接入方案。

### 第六题复盘：输入、输出与执行流程

目标：把文章分成可保留上下文的章节，保护代码内的伪标题，并标记需要进一步处理的超长块。本轮不新增编码任务。

具体输入：

````python
body = "导语\n## 示例\n```python\n## 代码里的文字\n```\n## 总结\n完成"
max_chars = 20
````

完整预期输出（已调用现有函数核验）：

````python
[
    {"index": 0, "text": "导语\n", "char_count": 3, "oversized": False},
    {"index": 1, "text": "## 示例\n```python\n## 代码里的文字\n```\n", "char_count": 30, "oversized": True},
    {"index": 2, "text": "## 总结\n完成", "char_count": 8, "oversized": False},
]
````

执行流程：

| 当前行或步骤 | 状态与动作 | 已保存的块数 |
|---|---|---|
| 导语 | 块外，将当前行加入暂存列表 | 0 |
| 示例标题 | 保存导语，清空暂存，再放入当前标题 | 1 |
| 开启围栏 | 记录反引号与数量 3，进入代码块；原行照常保存 | 1 |
| 代码里的标题文字 | 块内，只检查关闭条件；保留在当前章节 | 1 |
| 关闭围栏 | 清除活动围栏状态；原行照常保存 | 1 |
| 总结标题 | 保存示例章节，清空暂存，再放入当前标题 | 2 |
| 完成 | 加入当前章节的暂存列表 | 2 |
| 循环结束 | 保存暂存的总结章节 | 3 |
| 超长标记 | 依次计算 3、30、8 个字符，只有第二块严格超过 20 | 3 |

三个变量的职责：`active_fence` 记录代码块状态；`current_lines` 暂存当前章节；`chunks` 保存已经结束的章节。字符预算只决定标记，不决定这次的章节边界，不会截断原文。

个人理解检查：把预算从 20 改成 30，哪些输出字段会变，分块数量是否会变？先用自然语言回答即可。原文拼接一致性已验证；理解程度仍待回答确认。
