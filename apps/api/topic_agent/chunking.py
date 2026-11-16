"""按行首二级标题分块，保护围栏代码，保留原文并标记字符预算超限。"""


def _opening_fence(line):
    marker = line.rstrip('\r\n')
    candidate = marker.lstrip(' ')
    if len(marker) - len(candidate) > 3 or not candidate:
        return None
    char = candidate[0]
    if char not in ('`', '~'):
        return None
    length = 0
    for value in candidate:
        if value != char:
            break
        length += 1
    if length < 3 or (char == '`' and '`' in candidate[length:]):
        return None
    return char, length


def _closes_fence(line, char, length):
    marker = line.rstrip('\r\n')
    candidate = marker.lstrip(' ')
    if len(marker) - len(candidate) > 3:
        return False
    candidate = candidate.rstrip(' \t')
    return len(candidate) >= length and all(value == char for value in candidate)


def chunk_body(body: str, max_chars: int) -> list[dict]:
    """返回带原文的章节块；预算是字符数，不是 token 上限。"""
    if type(max_chars) is not int or max_chars <= 0:
        raise ValueError('max_chars 必须是正整数')
    sections = []
    current_lines = []
    active_fence = None
    for line in body.splitlines(keepends=True):
        if active_fence is not None:
            if _closes_fence(line, *active_fence):
                active_fence = None
        else:
            opening = _opening_fence(line)
            if opening is not None:
                active_fence = opening
            elif line.startswith('## ') and current_lines:
                sections.append(''.join(current_lines))
                current_lines = []
        current_lines.append(line)
    if current_lines:
        sections.append(''.join(current_lines))
    return [
        {'index': index, 'text': text, 'char_count': len(text),
         'oversized': len(text) > max_chars}
        for index, text in enumerate(sections)
    ]
