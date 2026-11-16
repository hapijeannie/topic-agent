"""只读预览顶层 Markdown 文件；不写库、不输出原文。"""

import argparse
import json
from pathlib import Path

from .chunking import chunk_body
from .ingestion import parse_markdown


def preview_directory(directory: Path, source: str, ownership: str, max_chars: int = 1000) -> dict:
    if type(max_chars) is not int or max_chars <= 0:
        return {'error': 'max_chars 必须是正整数'}
    if not directory.is_dir():
        return {'error': '输入路径不是可读取的目录'}
    try:
        files = sorted(p for p in directory.iterdir() if p.suffix.lower() == '.md' and p.is_file())
    except OSError:
        return {'error': '无法读取目录'}
    if not files:
        return {'error': '目录顶层没有 Markdown 文件'}
    rows = []
    seen = {}
    counts = dict.fromkeys(('ready', 'duplicate', 'conflict', 'error'), 0)
    for path in files:
        try:
            # read_bytes 避免通用换行转换悄悄改变原文和指纹。
            doc = parse_markdown(path.read_bytes().decode('utf-8'), source, ownership)
            chunks = chunk_body(doc.body, max_chars)
            identity = (doc.source_namespace, doc.source_id)
            previous = seen.get(identity)
            status = 'ready'
            if previous is not None:
                status = 'duplicate' if previous == doc.content_hash else 'conflict'
            else:
                seen[identity] = doc.content_hash
            row = {
                'file': path.name, 'status': status,
                'source': doc.source_namespace, 'source_id': doc.source_id,
                'ownership': doc.ownership, 'title': doc.title,
                'description': doc.description, 'declared_status': doc.declared_status,
                'published_at': doc.published_at, 'body_chars': len(doc.body),
                'content_hash': doc.content_hash,
                'chunk_count': len(chunks),
                'oversized_count': sum(chunk['oversized'] for chunk in chunks),
                'chunks': [
                    {key: chunk[key] for key in ('index', 'char_count', 'oversized')}
                    for chunk in chunks
                ],
            }
            if status == 'conflict':
                row['error'] = '同批次来源标识相同但内容不同，需要人工确认版本'
        except (OSError, UnicodeError, ValueError) as exc:
            row = {'file': path.name, 'status': 'error', 'error': str(exc)}
        counts[row['status']] += 1
        rows.append(row)
    return {'mode': 'read_only_preview', 'counts': counts, 'documents': rows}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory', type=Path)
    parser.add_argument('--source', required=True, help='稳定的来源集合名，例如 blog')
    parser.add_argument('--ownership', required=True, choices=['owned', 'reference'])
    parser.add_argument('--max-chars', type=int, default=1000,
                        help='分块字符预算，默认 1000；超长只标记，不截断')
    args = parser.parse_args()
    if args.max_chars <= 0:
        parser.error('--max-chars 必须是正整数')
    report = preview_directory(args.directory, args.source, args.ownership, args.max_chars)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return int('error' in report or bool(report['counts']['error'] or report['counts']['conflict']))


if __name__ == '__main__':
    raise SystemExit(main())
