"""只读解析 Markdown，不生成摘要、不写库、不调用模型。"""

from dataclasses import dataclass
from datetime import date, datetime
import hashlib
import json
import re

import yaml


class MetadataLoader(yaml.SafeLoader):
    """拒绝重复键，避免标题等字段被静默覆盖。"""

    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in result:
                raise ValueError('元数据键必须是唯一的字符串')
            result[key] = self.construct_object(value_node, deep=deep)
        return result


@dataclass(frozen=True)
class Document:
    source_namespace: str
    source_id: str
    ownership: str
    title: str
    description: str | None
    raw: str
    body: str
    metadata: dict
    declared_status: str
    published_at: str | None
    content_hash: str


def _json_value(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise ValueError('元数据只支持 JSON 兼容值和日期')


def parse_markdown(raw: str, source_namespace: str, ownership: str) -> Document:
    if not source_namespace.strip() or ownership not in {'owned', 'reference'}:
        raise ValueError('必须提供来源集合和 owned／reference 归属')

    # 保留原始字符串，只在识别开头标记时容忍 UTF-8 BOM。
    match = re.match(r'\A\ufeff?---[ \t]*\r?\n(.*?)^---[ \t]*(?:\r?\n|\Z)',
                     raw, re.MULTILINE | re.DOTALL)
    if not match:
        raise ValueError('缺少完整的 Frontmatter 起止标记')
    header = match.group(1)
    try:
        # 首版不支持别名，避免递归对象和隐式复用让元数据难以校验。
        if any(isinstance(token, yaml.AliasToken) for token in yaml.scan(header)):
            raise ValueError('元数据暂不支持 YAML 别名')
        metadata = yaml.load(header, Loader=MetadataLoader)
        if not isinstance(metadata, dict):
            raise ValueError('Frontmatter 必须是字段映射')
        metadata = json.loads(json.dumps(metadata, default=_json_value, allow_nan=False))
    except (yaml.YAMLError, TypeError, ValueError) as exc:
        raise ValueError('Frontmatter 格式或字段值无效') from exc

    title = metadata.get('title')
    source_id = metadata.get('slug', metadata.get('id'))
    if not isinstance(title, str) or not title.strip():
        raise ValueError('缺少非空 title')
    if type(source_id) not in (str, int) or not str(source_id).strip():
        raise ValueError('需要非空 slug 或 id 作为来源标识')
    description = metadata.get('description')
    if description is not None and not isinstance(description, str):
        raise ValueError('description 必须是文本')

    declared_status = 'unknown'
    if 'draft' in metadata:
        if type(metadata['draft']) is not bool:
            raise ValueError('draft 必须是布尔值 true 或 false')
        declared_status = 'draft' if metadata['draft'] else 'published'

    published_at = metadata.get('publishedAt')
    if published_at is not None:
        if not isinstance(published_at, str):
            raise ValueError('publishedAt 必须是 ISO 日期或时间')
        try:
            if re.fullmatch(r'\d{4}-\d{2}-\d{2}', published_at):
                date.fromisoformat(published_at)
            elif re.match(r'^\d{4}-\d{2}-\d{2}T', published_at):
                datetime.fromisoformat(published_at)
            else:
                raise ValueError('日期格式不支持')
        except ValueError as exc:
            raise ValueError('publishedAt 不是有效的 ISO 日期或时间') from exc

    body = raw[match.end():]
    if not body.strip():
        raise ValueError('正文不能为空')
    return Document(
        source_namespace=source_namespace.strip(), source_id=str(source_id).strip(),
        ownership=ownership, title=title.strip(), description=description,
        raw=raw, body=body, metadata=metadata, declared_status=declared_status,
        published_at=published_at,
        # 对原始文本求哈希，保守识别任何变化，包括文件头和换行。
        content_hash=hashlib.sha256(raw.encode('utf-8')).hexdigest(),
    )
