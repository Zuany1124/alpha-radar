from __future__ import annotations

import hashlib


class EvidenceEmbedder:
    """Evidence embedding provider。"""

    def embed(self, text: str) -> list[float]:
        """生成 embedding 向量。"""

        raise NotImplementedError


class DeterministicEvidenceEmbedder(EvidenceEmbedder):
    """测试和无 key 本地环境使用的确定性 embedding。"""

    def __init__(self, dimensions: int = 16) -> None:
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        """基于文本 hash 生成稳定向量。"""

        digest = hashlib.sha256(text.encode("utf-8")).digest()
        values: list[float] = []
        for index in range(self.dimensions):
            values.append(round(digest[index % len(digest)] / 255, 6))
        return values


class OpenAIEvidenceEmbedder(EvidenceEmbedder):
    """OpenAI Evidence embedding provider。"""

    def __init__(self, api_key: str, model: str, dimensions: int | None = None) -> None:
        self.api_key = api_key
        self.model = model
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        """调用 OpenAI embeddings API。"""

        if not self.api_key:
            return DeterministicEvidenceEmbedder().embed(text)

        from openai import OpenAI

        client = OpenAI(api_key=self.api_key)
        kwargs = {"model": self.model, "input": text}
        if self.dimensions:
            kwargs["dimensions"] = self.dimensions
        response = client.embeddings.create(**kwargs)
        return list(response.data[0].embedding)
