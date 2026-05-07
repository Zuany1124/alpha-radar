from __future__ import annotations

from typing import Protocol

from app.models.evidence_item import EvidenceItem
from app.schemas.evidence import EvidenceRetrievalQuery


class EvidenceSearchIndex(Protocol):
    """Evidence 全文索引接口。"""

    def ensure_index(self) -> None:
        """确保索引存在。"""

    def index_evidence(self, evidence: EvidenceItem) -> None:
        """索引单条 Evidence。"""

    def search(self, query: EvidenceRetrievalQuery) -> list[str]:
        """返回匹配的 Evidence ID。"""


class NullEvidenceSearchIndex:
    """未启用 Elasticsearch 时的空索引。"""

    def ensure_index(self) -> None:
        return None

    def index_evidence(self, evidence: EvidenceItem) -> None:
        return None

    def search(self, query: EvidenceRetrievalQuery) -> list[str]:
        return []


class ElasticsearchEvidenceIndex:
    """Elasticsearch Evidence 全文索引。"""

    def __init__(self, client, index_name: str) -> None:
        self.client = client
        self.index_name = index_name

    def ensure_index(self) -> None:
        """创建 Evidence 索引和字段映射。"""

        if self.client.indices.exists(index=self.index_name):
            return

        self.client.indices.create(
            index=self.index_name,
            settings={"number_of_shards": 1, "number_of_replicas": 0},
            mappings={
                "properties": {
                    "evidence_id": {"type": "keyword"},
                    "title": {"type": "text", "fields": {"keyword": {"type": "keyword"}}},
                    "summary": {"type": "text"},
                    "source_url": {"type": "keyword"},
                    "evidence_type": {"type": "keyword"},
                    "published_at": {"type": "date"},
                    "fetched_at": {"type": "date"},
                    "asset_symbol": {"type": "keyword"},
                    "asset_mint": {"type": "keyword"},
                }
            },
        )

    def index_evidence(self, evidence: EvidenceItem) -> None:
        """把 EvidenceItem 写入 Elasticsearch。"""

        metadata = evidence.evidence_metadata or {}
        self.client.index(
            index=self.index_name,
            id=evidence.id,
            document={
                "evidence_id": evidence.id,
                "title": evidence.title,
                "summary": evidence.summary,
                "source_url": evidence.source_url,
                "evidence_type": evidence.evidence_type,
                "published_at": evidence.published_at,
                "fetched_at": evidence.fetched_at,
                "asset_symbol": metadata.get("asset_symbol"),
                "asset_mint": metadata.get("asset_mint"),
            },
        )

    def search(self, query: EvidenceRetrievalQuery) -> list[str]:
        """执行全文检索并返回 evidence IDs。"""

        filters: list[dict] = []
        if query.asset_symbol:
            filters.append({"term": {"asset_symbol": query.asset_symbol}})
        if query.asset_mint:
            filters.append({"term": {"asset_mint": query.asset_mint}})
        if query.evidence_types:
            filters.append({"terms": {"evidence_type": query.evidence_types}})

        response = self.client.search(
            index=self.index_name,
            size=query.limit,
            query={
                "bool": {
                    "must": [
                        {
                            "multi_match": {
                                "query": query.query,
                                "fields": ["title^3", "summary", "source_url"],
                            }
                        }
                    ],
                    "filter": filters,
                }
            },
        )
        hits = response.get("hits", {}).get("hits", [])
        return [hit.get("_source", {}).get("evidence_id") for hit in hits if hit.get("_source", {}).get("evidence_id")]


def build_elasticsearch_index(url: str, api_key: str, index_name: str) -> EvidenceSearchIndex:
    """根据配置创建 Elasticsearch 索引客户端。"""

    if not url:
        return NullEvidenceSearchIndex()

    from elasticsearch import Elasticsearch

    kwargs = {"hosts": [url]}
    if api_key:
        kwargs["api_key"] = api_key
    return ElasticsearchEvidenceIndex(Elasticsearch(**kwargs), index_name)
