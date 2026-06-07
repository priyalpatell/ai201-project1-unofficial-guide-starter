import os
import chromadb
from chromadb.utils import embedding_functions
from ingest import pre_process, chunk_text_by_words

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
            "text": text,
            "location": metadata["location"],
            "distance": distance,
        }
        for text, metadata, distance in zip(
            results["documents"][0], 
            results["metadatas"][0], 
            results["distances"][0]
        )
    ]
    return chunks

# # --- Updated Sandbox Local Test Run ---
# if __name__ == "__main__":
#     print("--- STARTING LOCAL PIPELINE REVERSE TEST ---")
    
#     # 1. Run the imported preprocessing logic
#     processed_files = pre_process()
#     all_chunks = []
    
#     # 2. Loop over and chunk the files
#     for file_info in processed_files:
#         file_chunks = chunk_text_by_words(
#             location=file_info["location"],
#             filename=file_info["filename"],
#             text=file_info["text"]
#         )
#         all_chunks.extend(file_chunks)
        
#     print(f"Successfully processed files and generated {len(all_chunks)} chunks.")
    
#     # 3. Call your local embed_and_store function
#     if all_chunks:
#         embed_and_store(all_chunks)
#     else:
#         print("Test aborted: No chunks were generated. Check your text files.")
        
#     print("\n--- STARTING RETRIEVAL TEST ---")
# 	# 4. Test the retrieval function with a sample query
#     sample_query1 = "Do the reviews mention the quality of the mongolian wok station?"
#     retrieved_chunks = retrieve(sample_query1)
	
#     if retrieved_chunks:
#         print(f"Retrieved {len(retrieved_chunks)} chunks for the query: '{sample_query1}'")
#         for idx, chunk in enumerate(retrieved_chunks, start=1):
#             print(f"\n--- Chunk {idx} ---")
#             print(f"Text: {chunk['text']}")
#             print(f"Location: {chunk['location']}")
#             print(f"Distance: {chunk['distance']}")
#     else:
#         print("No chunks retrieved. Check your database and query logic.")

#     sample_query2 = "Which location is recommended for international or global food?"
#     retrieved_chunks = retrieve(sample_query2)

#     if retrieved_chunks:
#         print(f"Retrieved {len(retrieved_chunks)} chunks for the query: '{sample_query2}'")
#         for idx, chunk in enumerate(retrieved_chunks, start=1):
#             print(f"\n--- Chunk {idx} ---")
#             print(f"Text: {chunk['text']}")
#             print(f"Location: {chunk['location']}")
#             print(f"Distance: {chunk['distance']}")
#     else:
#         print("No chunks retrieved. Check your database and query logic.")

#     sample_query3 = "What are the top complaints about Cuarto's food quality?"
#     retrieved_chunks = retrieve(sample_query3)

#     if retrieved_chunks:
#         print(f"Retrieved {len(retrieved_chunks)} chunks for the query: '{sample_query3}'")
#         for idx, chunk in enumerate(retrieved_chunks, start=1):
#             print(f"\n--- Chunk {idx} ---")
#             print(f"Text: {chunk['text']}")
#             print(f"Location: {chunk['location']}")
#             print(f"Distance: {chunk['distance']}")
#     else:
#         print("No chunks retrieved. Check your database and query logic.")