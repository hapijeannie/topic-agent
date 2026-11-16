import hashlib
import unittest

from topic_agent.ingestion import parse_markdown


def article(header='title: 测试文章\nslug: test', body='## 小节\n正文\n'):
    return f'---\n{header}\n---\n{body}'


class ParsingTests(unittest.TestCase):
    def parse(self, raw, source='blog', ownership='owned'):
        return parse_markdown(raw, source, ownership)

    def test_preserves_raw_and_code_body(self):
        body = '## 小节\n```yaml\ntitle: 不是文件头\n---\n```\n'
        raw = article(body=body)
        doc = self.parse(raw)
        self.assertEqual(doc.body, body)
        self.assertEqual(doc.raw, raw)
        self.assertEqual(doc.content_hash, hashlib.sha256(raw.encode()).hexdigest())

    def test_yaml_quotes_multiline_and_unknown_fields(self):
        doc = self.parse(article('title: "Agent: 记忆"\nslug: memory\n'
                                 'description: |\n  第一行\n  第二行\n'
                                 'keywords: [AI, 记忆]'))
        self.assertEqual(doc.title, 'Agent: 记忆')
        self.assertEqual(doc.description, '第一行\n第二行\n')
        self.assertEqual(doc.metadata['keywords'], ['AI', '记忆'])

    def test_crlf_body_and_bom_are_supported_without_rewriting_raw(self):
        raw = '\ufeff' + article().replace('\n', '\r\n')
        doc = self.parse(raw)
        self.assertEqual(doc.body, '## 小节\r\n正文\r\n')
        self.assertEqual(doc.raw, raw)

    def test_date_is_serializable_and_status_is_only_a_declaration(self):
        doc = self.parse(article('title: 测试\nslug: test\ndraft: false\npublishedAt: 2026-10-10'))
        self.assertEqual(doc.published_at, '2026-10-10')
        self.assertEqual(doc.declared_status, 'published')
        self.assertEqual(self.parse(article()).declared_status, 'unknown')

    def test_timestamp_keeps_timezone(self):
        doc = self.parse(article('title: 测试\nid: "20260911164207"\n'
                                 'publishedAt: 2026-10-10T10:20:00+08:00'))
        self.assertEqual(doc.published_at, '2026-10-10T10:20:00+08:00')
        self.assertEqual(doc.source_id, '20260911164207')

    def test_unquoted_numeric_fuxi_id_is_supported(self):
        doc = self.parse(article('title: 测试\nid: 20260911164207'))
        self.assertEqual(doc.source_id, '20260911164207')

    def test_source_and_identity_are_separate_from_content_hash(self):
        raw = article()
        first = self.parse(raw)
        other = self.parse(raw, source='fuxi', ownership='reference')
        changed = self.parse(article(body='新正文'))
        self.assertNotEqual(first.source_namespace, other.source_namespace)
        self.assertEqual(first.content_hash, other.content_hash)
        self.assertEqual(first.source_id, changed.source_id)
        self.assertNotEqual(first.content_hash, changed.content_hash)
        self.assertEqual(other.ownership, 'reference')

    def test_rejects_missing_frontmatter_or_closing_delimiter(self):
        for raw in ['# 文章', '---\ntitle: 测试\nslug: test']:
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                self.parse(raw)

    def test_rejects_invalid_metadata_without_guessing(self):
        headers = [
            'slug: test', 'title: ""\nslug: test', 'title: 测试',
            'title: 测试\nslug: [a, b]', 'title: 测试\nslug: true',
            'title: 测试\nslug: test\ndraft: "false"',
            'title: 测试\nslug: test\npublishedAt: 2026-02-30',
            'title: 测试\nslug: test\npublishedAt: tomorrow',
            'title: 测试\nslug: test\ndescription: [a, b]',
            '- title\n- test', 'title: [unterminated',
        ]
        for header in headers:
            with self.subTest(header=header), self.assertRaises(ValueError):
                self.parse(article(header))

    def test_rejects_duplicate_keys_and_unsafe_yaml_tags(self):
        for header in [
            'title: first\ntitle: second\nslug: test',
            'title: !!python/object:builtins.str {}\nslug: test',
        ]:
            with self.subTest(header=header), self.assertRaises(ValueError):
                self.parse(article(header))

    def test_rejects_empty_body_and_invalid_source(self):
        with self.assertRaises(ValueError):
            self.parse(article(body=' \n'))
        with self.assertRaises(ValueError):
            self.parse(article(), source=' ')
        with self.assertRaises(ValueError):
            self.parse(article(), ownership='guess')


if __name__ == '__main__':
    unittest.main()
