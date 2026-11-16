import unittest

from topic_agent.chunking import chunk_body


class ChunkingTests(unittest.TestCase):
    def test_keeps_sections_and_marks_only_strictly_over_budget(self):
        self.assertEqual(chunk_body('## A\n甲\n## B\n乙', 6), [
            {'index': 0, 'text': '## A\n甲\n', 'char_count': 7, 'oversized': True},
            {'index': 1, 'text': '## B\n乙', 'char_count': 6, 'oversized': False},
        ])

    def test_preserves_preamble_empty_lines_and_exact_line_endings(self):
        for body, texts in [
            ('', []),
            ('正文\n\n', ['正文\n\n']),
            ('导语\r\n## A\r\n甲\r\n## B', ['导语\r\n', '## A\r\n甲\r\n', '## B']),
            ('## A\n## B', ['## A\n', '## B']),
            ('### A\n##无空格\n## B', ['### A\n##无空格\n', '## B']),
        ]:
            with self.subTest(body=body):
                actual = chunk_body(body, 100)
                self.assertEqual([c['text'] for c in actual], texts)
                self.assertEqual(''.join(c['text'] for c in actual), body)

    def test_fences_protect_headings_until_valid_closing_line(self):
        blocks = [
            '```python\n## 隐藏\n```\n',
            '````md\n```\n## 隐藏\n`````\n',
            '~~~\n```\n## 隐藏\n~~~\n',
            '```\n```python\n## 隐藏\n```\n',
            '   ~~~py\r\n## 隐藏\r\n  ~~~~ \t\r\n',
            '```\n    ```\n## 隐藏\n```\n',
            '~~~\n~~~x\n## 隐藏\n~~~\n',
            '~~~\n## 隐藏一\n~~~\n```\n## 隐藏二\n```\n',
        ]
        for block in blocks:
            with self.subTest(block=block):
                body = '## A\n' + block + '## B\n结束'
                actual = chunk_body(body, 1)
                self.assertEqual([c['text'] for c in actual], ['## A\n' + block, '## B\n结束'])
                self.assertEqual(''.join(c['text'] for c in actual), body)
                self.assertTrue(all(c['oversized'] for c in actual))

    def test_unclosed_fence_keeps_remainder_together(self):
        body = '## A\n```python\n## 隐藏'
        self.assertEqual([c['text'] for c in chunk_body(body, 2)], [body])

    def test_invalid_openers_do_not_hide_next_heading(self):
        for opener in ['``python', '~~x~~', '```py`thon', '    ```']:
            with self.subTest(opener=opener):
                first = opener + '\n'
                self.assertEqual([c['text'] for c in chunk_body(first + '## B', 100)], [first, '## B'])

    def test_rejects_invalid_budget_even_for_empty_body(self):
        for value in (0, -1, True, 1.5, '3', None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                chunk_body('', value)


if __name__ == '__main__':
    unittest.main()
