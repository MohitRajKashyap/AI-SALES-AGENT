import json
import uuid
from typing import List, Optional
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, Filter,
    FieldCondition, MatchValue, SearchRequest
)
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

VECTOR_DIM = 1536  # text-embedding-3-small


class VectorService:
    def __init__(self):
        self.client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY,
        )
        self.openai = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def ensure_collections(self):
        for collection in [
            settings.QDRANT_COLLECTION_COMPANIES,
            settings.QDRANT_COLLECTION_LEADS,
            settings.QDRANT_COLLECTION_EMAILS,
        ]:
            try:
                await self.client.get_collection(collection)
            except Exception:
                await self.client.create_collection(
                    collection_name=collection,
                    vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE),
                )
                logger.info(f"Created collection: {collection}")

    async def embed(self, text: str) -> List[float]:
        response = await self.openai.embeddings.create(
            model="text-embedding-3-small",
            input=text[:8000],
        )
        return response.data[0].embedding

    async def upsert_company(self, company_id: str, company_data: dict, workspace_id: str) -> str:
        text = f"{company_data.get('company_name', '')} {company_data.get('industry', '')} {' '.join(company_data.get('services', []))}"
        vector = await self.embed(text)
        point_id = str(uuid.uuid4())

        await self.client.upsert(
            collection_name=settings.QDRANT_COLLECTION_COMPANIES,
            points=[PointStruct(
                id=point_id,
                vector=vector,
                payload={**company_data, "db_id": company_id, "workspace_id": workspace_id}
            )]
        )
        return point_id

    async def upsert_lead(self, lead_id: str, lead_data: dict, workspace_id: str) -> str:
        text = f"{lead_data.get('company_name', '')} {lead_data.get('industry', '')} {lead_data.get('job_title', '')}"
        vector = await self.embed(text)
        point_id = str(uuid.uuid4())

        await self.client.upsert(
            collection_name=settings.QDRANT_COLLECTION_LEADS,
            points=[PointStruct(
                id=point_id,
                vector=vector,
                payload={**lead_data, "db_id": lead_id, "workspace_id": workspace_id}
            )]
        )
        return point_id

    async def upsert_email(self, email_id: str, subject: str, body: str, workspace_id: str) -> str:
        text = f"{subject} {body[:500]}"
        vector = await self.embed(text)
        point_id = str(uuid.uuid4())

        await self.client.upsert(
            collection_name=settings.QDRANT_COLLECTION_EMAILS,
            points=[PointStruct(
                id=point_id,
                vector=vector,
                payload={"db_id": email_id, "subject": subject, "workspace_id": workspace_id}
            )]
        )
        return point_id

    async def search(self, collection: str, query: str, workspace_id: str, limit: int = 5) -> list:
        vector = await self.embed(query)
        results = await self.client.search(
            collection_name=collection,
            query_vector=vector,
            limit=limit,
            query_filter=Filter(
                must=[FieldCondition(key="workspace_id", match=MatchValue(value=workspace_id))]
            ),
            with_payload=True,
        )
        return [
            {"id": str(r.id), "score": r.score, "payload": r.payload}
            for r in results
        ]
