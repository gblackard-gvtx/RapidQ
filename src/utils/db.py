from qdrant_client import QdrantClient

client = QdrantClient(
    url="https://localhost:6333",
    api_key="your_secret_api_key_here",
)