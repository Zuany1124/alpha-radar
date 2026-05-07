from datetime import datetime, timezone
import json
from pathlib import Path

from sqlalchemy.orm import Session

from app.repositories.evidence_repository import EvidenceRepository
from app.services.evidence_service import EvidenceService
from app.services.search_index import ElasticsearchEvidenceIndex
from app.schemas.evidence import EvidenceIngestDocument, EvidenceRetrievalQuery


class FakeEmbedder:
    def embed(self, text: str) -> list[float]:
        return [float(len(text)), 1.0, 0.5]


class RecordingSearchIndex:
    def __init__(self) -> None:
        self.indexed: list[dict] = []
        self.search_ids: list[str] = []

    def ensure_index(self) -> None:
        return None

    def index_evidence(self, evidence) -> None:
        self.indexed.append(
            {
                "id": evidence.id,
                "title": evidence.title,
                "summary": evidence.summary,
                "evidence_type": evidence.evidence_type,
            }
        )

    def search(self, query: EvidenceRetrievalQuery) -> list[str]:
        self.search_ids.append(query.query)
        return []


def test_ingest_documents_persists_embedding_and_indexes_payload(db_session: Session) -> None:
    search_index = RecordingSearchIndex()
    service = EvidenceService(
        EvidenceRepository(db_session),
        embedder=FakeEmbedder(),
        search_index=search_index,
    )

    items = service.ingest_documents(
        [
            EvidenceIngestDocument(
                evidence_type="project_doc",
                title="ALPHA project docs",
                source_url="https://example.com/alpha",
                published_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
                summary="ALPHA announced a Solana liquidity program.",
                evidence_metadata={"asset_symbol": "ALPHA", "asset_mint": "MintAlpha"},
            )
        ]
    )

    assert len(items) == 1
    assert items[0].embedding == [104.0, 1.0, 0.5]
    assert items[0].fetched_at is not None
    assert search_index.indexed == [
        {
            "id": items[0].id,
            "title": "ALPHA project docs",
            "summary": "ALPHA announced a Solana liquidity program.",
            "evidence_type": "project_doc",
        }
    ]


def test_ingest_documents_reuses_existing_source_url(db_session: Session) -> None:
    service = EvidenceService(EvidenceRepository(db_session), embedder=FakeEmbedder())
    document = EvidenceIngestDocument(
        evidence_type="news",
        title="ALPHA news",
        source_url="https://example.com/news",
        summary="First version.",
    )

    first = service.ingest_documents([document])[0]
    second = service.ingest_documents(
        [document.model_copy(update={"summary": "Updated version."})]
    )[0]

    assert second.id == first.id
    assert second.summary == "Updated version."
    assert db_session.query(type(first)).count() == 1


def test_ingest_fixture_file_loads_documents(db_session: Session, tmp_path: Path) -> None:
    fixture_path = tmp_path / "evidence_fixture.json"
    fixture_path.write_text(
        json.dumps(
            {
                "documents": [
                    {
                        "evidence_type": "news",
                        "title": "ALPHA announcement",
                        "source_url": "https://example.com/announcement",
                        "summary": "ALPHA announced new Solana incentives.",
                        "evidence_metadata": {"asset_symbol": "ALPHA"},
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    service = EvidenceService(EvidenceRepository(db_session), embedder=FakeEmbedder())

    items = service.ingest_fixture_file(fixture_path)

    assert len(items) == 1
    assert items[0].title == "ALPHA announcement"
    assert items[0].evidence_metadata == {"asset_symbol": "ALPHA"}


def test_retrieve_evidence_uses_elasticsearch_then_keyword_fallback(db_session: Session) -> None:
    search_index = RecordingSearchIndex()
    service = EvidenceService(
        EvidenceRepository(db_session),
        embedder=FakeEmbedder(),
        search_index=search_index,
    )
    alpha, stale = service.ingest_documents(
        [
            EvidenceIngestDocument(
                evidence_type="news",
                title="ALPHA liquidity update",
                summary="ALPHA liquidity and volume increased.",
                evidence_metadata={"asset_symbol": "ALPHA"},
            ),
            EvidenceIngestDocument(
                evidence_type="news",
                title="Unrelated market note",
                summary="No relevant project details.",
                evidence_metadata={"asset_symbol": "OTHER"},
            ),
        ]
    )

    results = service.retrieve_evidence(
        EvidenceRetrievalQuery(query="ALPHA liquidity", asset_symbol="ALPHA", limit=5)
    )

    assert search_index.search_ids == ["ALPHA liquidity"]
    assert [result.evidence.id for result in results] == [alpha.id]
    assert stale.id not in [result.evidence.id for result in results]
    assert results[0].match_source in {"keyword", "hybrid"}


def test_elasticsearch_adapter_builds_multimatch_query_with_filters() -> None:
    class FakeIndices:
        def __init__(self) -> None:
            self.created = None

        def exists(self, index: str) -> bool:
            return False

        def create(self, index: str, settings: dict, mappings: dict) -> None:
            self.created = {"index": index, "settings": settings, "mappings": mappings}

    class FakeClient:
        def __init__(self) -> None:
            self.indices = FakeIndices()
            self.search_call = None

        def index(self, index: str, id: str, document: dict) -> None:
            return None

        def search(self, index: str, size: int, query: dict) -> dict:
            self.search_call = {"index": index, "size": size, "query": query}
            return {"hits": {"hits": [{"_source": {"evidence_id": "ev-1"}}]}}

    client = FakeClient()
    adapter = ElasticsearchEvidenceIndex(client=client, index_name="evidence-test")

    adapter.ensure_index()
    ids = adapter.search(
        EvidenceRetrievalQuery(
            query="ALPHA liquidity",
            asset_symbol="ALPHA",
            evidence_types=["news"],
            limit=3,
        )
    )

    assert client.indices.created["index"] == "evidence-test"
    assert ids == ["ev-1"]
    assert client.search_call["size"] == 3
    filters = client.search_call["query"]["bool"]["filter"]
    assert {"term": {"asset_symbol": "ALPHA"}} in filters
    assert {"terms": {"evidence_type": ["news"]}} in filters
    assert client.search_call["query"]["bool"]["must"][0]["multi_match"]["query"] == "ALPHA liquidity"
