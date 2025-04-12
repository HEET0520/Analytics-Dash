from langchain_community.embeddings import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Initialize Hugging Face embeddings with token
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"use_auth_token": HF_TOKEN}
)
qdrant_client = QdrantClient(path="./qdrant_data")
COLLECTION_NAME = "docs"

def setup_vector_db(documents):
    """
    Set up a Qdrant vector database with document embeddings.
    Args:
        documents (list): List of document texts to embed.
    Returns:
        QdrantClient: Configured vector database client.
    """
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
    )
    points = [
        models.PointStruct(id=idx, vector=embeddings.embed_query(doc), payload={"text": doc})
        for idx, doc in enumerate(documents)
    ]
    qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
    return qdrant_client

def query_rag(query, client):
    """
    Query the RAG system for relevant document chunks.
    Args:
        query (str): User query.
        client (QdrantClient): Vector database client.
    Returns:
        list: List of relevant text chunks.
    """
    query_vector = embeddings.embed_query(query)
    search_result = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=3
    )
    return [hit.payload["text"] for hit in search_result]