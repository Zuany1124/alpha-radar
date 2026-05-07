import json
import logging
from pathlib import Path

from fastapi import HTTPException, status

from app.models.evidence_item import EvidenceItem
from app.repositories.evidence_repository import EvidenceRepository
from app.schemas.evidence import EvidenceIngestDocument, EvidenceRetrievalQuery, EvidenceRetrievalResult
from app.services.embedding_service import DeterministicEvidenceEmbedder, EvidenceEmbedder, OpenAIEvidenceEmbedder
from app.services.search_index import EvidenceSearchIndex, NullEvidenceSearchIndex, build_elasticsearch_index

logger = logging.getLogger(__name__)


class EvidenceService:
    """EvidenceItem 资源和检索服务。"""

    def __init__(
        self,
        evidence: EvidenceRepository,
        embedder: EvidenceEmbedder | None = None,
        search_index: EvidenceSearchIndex | None = None,
    ) -> None:
        self.evidence = evidence
        self.embedder = embedder or DeterministicEvidenceEmbedder()
        self.search_index = search_index or NullEvidenceSearchIndex()

    def list_evidence(
        self,
        limit: int,
        offset: int,
        evidence_type: str | None = None,
    ) -> list[EvidenceItem]:
        """分页查询证据资源。"""

        return self.evidence.list(limit=limit, offset=offset, evidence_type=evidence_type)

    def get_evidence(self, evidence_id: str) -> EvidenceItem:
        """查询单条证据，不存在时返回 404。"""

        evidence = self.evidence.get(evidence_id)
        if evidence is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evidence not found")
        return evidence

    def ingest_documents(self, documents: list[EvidenceIngestDocument]) -> list[EvidenceItem]:
        """导入 Evidence 文档并同步全文索引。"""

        try:
            self.search_index.ensure_index()
        except Exception:
            logger.exception("Evidence search index unavailable; continuing with database storage")
            self.search_index = NullEvidenceSearchIndex()
        items: list[EvidenceItem] = []
        for document in documents:
            embedding = self.embedder.embed(self._document_text(document))
            evidence = self.evidence.upsert_document(document, embedding=embedding)
            items.append(evidence)

        self.evidence.db.commit()
        for item in items:
            try:
                self.search_index.index_evidence(item)
            except Exception:
                logger.exception("Failed to index evidence %s", item.id)
        return items

    def ingest_fixture_file(self, fixture_path: str | Path) -> list[EvidenceItem]:
        """从 fixture JSON 文件导入 Evidence 文档。"""

        path = Path(fixture_path)
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        documents = [EvidenceIngestDocument.model_validate(item) for item in payload.get("documents", [])]
        return self.ingest_documents(documents)

    def retrieve_evidence(self, query: EvidenceRetrievalQuery) -> list[EvidenceRetrievalResult]:
        """混合检索 Evidence：全文索引优先，数据库关键词和向量 fallback 补充。"""

        ordered: dict[str, EvidenceRetrievalResult] = {}
        try:
            search_ids = self.search_index.search(query)
        except Exception:
            logger.exception("Evidence search index unavailable; using database fallback")
            search_ids = []

        for evidence_id in search_ids:
            evidence = self.evidence.get(evidence_id)
            if evidence is not None:
                ordered[evidence.id] = EvidenceRetrievalResult(
                    evidence=evidence, score=1.0, match_source="elasticsearch"
                )

        query_embedding = self.embedder.embed(query.query)
        for item in self.evidence.search_keyword(query):
            existing = ordered.get(item.id)
            ordered[item.id] = EvidenceRetrievalResult(
                evidence=item,
                score=max(existing.score if existing else 0, 0.8),
                match_source="hybrid" if existing else "keyword",
            )

        for item in self.evidence.search_vector(query, query_embedding):
            existing = ordered.get(item.id)
            ordered[item.id] = EvidenceRetrievalResult(
                evidence=item,
                score=max(existing.score if existing else 0, 0.6),
                match_source="hybrid" if existing else "vector",
            )

        return sorted(ordered.values(), key=lambda item: item.score, reverse=True)[: query.limit]

    @staticmethod
    def _document_text(document: EvidenceIngestDocument) -> str:
        return " ".join(
            part
            for part in [
                document.title,
                document.summary or "",
                document.source_url or "",
                " ".join(str(value) for value in document.evidence_metadata.values()),
            ]
            if part
        )


def build_evidence_service(settings, repository: EvidenceRepository) -> EvidenceService:
    """根据配置创建 EvidenceService。"""

    embedder = OpenAIEvidenceEmbedder(
        api_key=getattr(settings, "openai_api_key", ""),
        model=getattr(settings, "default_embedding_model", "text-embedding-3-small"),
        dimensions=getattr(settings, "embedding_dimensions", None),
    )
    search_index = build_elasticsearch_index(
        url=getattr(settings, "elasticsearch_url", ""),
        api_key=getattr(settings, "elasticsearch_api_key", ""),
        index_name=getattr(settings, "elasticsearch_evidence_index", "alpharadar-evidence"),
    )
    return EvidenceService(repository, embedder=embedder, search_index=search_index)
