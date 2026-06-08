import os
import chromadb
from chromadb.utils import embedding_functions

# Import your centralized configurations directly
from config import EMBEDDING_MODEL, CHROMA_COLLECTION, CHROMA_PATH, N_RESULTS

# 1. Instantiate the native preset embedding function using config variables
PRESET_EMBEDDING_FUNCTION = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=EMBEDDING_MODEL
)

# 2. Establish the client and register the model preset directly to the collection
CLIENT = chromadb.PersistentClient(path=CHROMA_PATH)
COLLECTION = CLIENT.get_or_create_collection(
    name=CHROMA_COLLECTION,
    metadata={"hnsw:space": "cosine"},
    embedding_function=PRESET_EMBEDDING_FUNCTION
)

def get_collection():
    """Return the ChromaDB collection. Used by app.py during ingestion."""
    return COLLECTION

def embed_and_store(chunks_array: list[dict]) -> None:
    """
    Stores chunks in the vector database. Because the embedding model is preset, 
    we pass the raw text documents directly and Chroma handles the math automatically.
    """
    if not chunks_array:
        print("No chunks provided to store.")
        return

    documents = [chunk["text"] for chunk in chunks_array]
    metadatas = [{"location": chunk["location"]} for chunk in chunks_array]
    ids = [chunk["chunk_id"] for chunk in chunks_array]

    print(f"Native model preset embedding and writing {len(documents)} records...")
    
    COLLECTION.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"\n--- DATABASE STORAGE VERIFICATION ---")
    print(f"Total chunks stored in the database: {COLLECTION.count()}")
    print(f"-------------------------------------")

def retrieve(query, n_results=N_RESULTS) -> list[dict]:
    """
    Queries the collection using a raw text query string and maps the
    parallel result arrays directly into an inline list comprehension.
    """
    if COLLECTION.count() == 0:
        return []

    results = COLLECTION.query(
        query_texts=[query],
        n_results=n_results,
        include=["documents", "metadatas", "distances"],
    )

    chunks = [
        {
            "id": chunk_id,
            "text": text,
            "location": metadata["location"],
            "distance": distance,
        }
        for chunk_id, text, metadata, distance in zip(
            results["ids"][0],
            results["documents"][0], 
            results["metadatas"][0], 
            results["distances"][0]
        )
    ]
    return chunks