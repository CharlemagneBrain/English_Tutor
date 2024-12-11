import asyncio
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from typing import List, Tuple
from func_tools import async_convert_to_text, load_tokenizer, load_transformers, split_pages_into_chunks, vectorize

def create_qdrant_index():
    client = QdrantClient(
        url="https://4c7d05ec-2ebc-4f6a-ba50-5e5e2f1bc0d9.us-east4-0.gcp.cloud.qdrant.io:6333", 
        api_key="5LCkUwYEtUjwmt4uXoGUky4rVT8Yn2tJ_cJFkFBLwcDN67uScTzykQ",
    )
    client.recreate_collection(
        collection_name="toefl_tutor",
        vectors_config=rest.VectorParams(size=384, distance=rest.Distance.COSINE)
    )

async def ingest_files_to_qdrant():

    client = QdrantClient(
        url="https://4c7d05ec-2ebc-4f6a-ba50-5e5e2f1bc0d9.us-east4-0.gcp.cloud.qdrant.io:6333", 
        api_key="5LCkUwYEtUjwmt4uXoGUky4rVT8Yn2tJ_cJFkFBLwcDN67uScTzykQ",
    )

    tokenizer = load_tokenizer()
    transformer = load_transformers(model_name="all-MiniLM-L6-v2", cache_folder="models_cache")

    file_paths = [
        os.path.join("ressources", file)
        for file in os.listdir("ressources")
        if file.endswith((".pdf", ".docx"))
    ]
    texts = await async_convert_to_text(file_paths)
    chunks = split_pages_into_chunks(texts, 256, tokenizer)
    embeddings = vectorize(chunks, transformer)

    for idx, (chunk, embedding) in enumerate(embeddings):
        client.upsert(
            collection_name="toefl_tutor",
            points=[
                rest.PointStruct(
                    id=idx,
                    vector=embedding.tolist(),
                    payload={"text": chunk}
                )
            ]
        )

if __name__ == "__main__":
    create_qdrant_index()
    asyncio.run(ingest_files_to_qdrant())
