from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if not HF_TOKEN:
    raise ValueError("HF_TOKEN not set in environment. Get one from https://huggingface.co/settings/tokens")

# Initialize Hugging Face embeddings with token and optimization for CPU
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={
        "token": HF_TOKEN,
        "device": "cpu"  # Explicitly set to CPU
    },
    encode_kwargs={"batch_size": 8}  # Smaller batch size for 8GB RAM
)

# Use local file storage for Qdrant to save memory
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
    # Process in smaller batches to save memory
    qdrant_client.recreate_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE)
    )
    
    # Process documents in smaller batches to save memory
    batch_size = 5
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        points = [
            models.PointStruct(id=i+idx, vector=embeddings.embed_query(doc), payload={"text": doc})
            for idx, doc in enumerate(batch_docs)
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
