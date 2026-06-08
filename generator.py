from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL
# from ingest import pre_process, chunk_text_by_words
# from retriever import embed_and_store, retrieve

_client = Groq(api_key=GROQ_API_KEY)

def generate_response(query: str, retrieved_chunks: list[dict]) -> str:
    if not retrieved_chunks:
        return (
            "I couldn't find any relevant student reviews regarding that topic. "
            "Try rephrasing your question — or check that your ingestion pipeline is working."
        )
    
    # Format the retrieved chunks with both location and the appended filename source
    formatted_chunks = []
    for c in retrieved_chunks:
        chunk_id = c.get("id", "UNKNOWN_SOURCE")
        base_name = chunk_id.rsplit("_", 1)[0].upper() if "_" in chunk_id else chunk_id.upper()
        filename_source = f"{base_name}.TXT"
        
        # Explicitly tag the file separately from the location metadata
        formatted_chunks.append(
            f"FILE_NAME: {filename_source}\n"
            f"LOCATION: {c['location'].upper()}\n"
            f"REVIEW_TEXT: {c['text']}"
        )

    response = _client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant providing student sentiment on the dining commons at UC Davis. "
                    "Use only the provided retrieved review chunks as your knowledge base. "
                    "If the answer isn't contained in the chunks, explicitly state that you don't know instead of making something up. "
                    "If the query talks about a specific location, prioritize chunks matching that location context. "
                    "Include the specific dining common location in your text answer to make it clear where the feedback is coming from. "
                    "Synthesize the retrieved information into a concise, coherent response that directly answers the user's question. "
                    "Avoid repetitive sentence structures (e.g., 'One review says... another review says...'). "
                    "Do not summarize the text, create an 'overall sentiment', or combine multiple reviews into a single narrative. "
                    "Important citation requirement:\n"
                    "You must include explicit inline citations in parentheses after each piece of information you use. "
                    "Your citation must be the exact string following 'FILE_NAME:' not the location. "
                    "For example, if the text is from FILE_NAME: SEGUNDO_REVIEWS.TXT, you must cite it exactly as (SEGUNDO_REVIEWS.TXT). "
                    "Do not use the location name as the citation string."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {query}\n\n"
                    "Retrieved review chunks:\n" +
                    "\n\n".join(formatted_chunks)
                ),
            },
        ],
    )
    return response.choices[0].message.content

# if __name__ == "__main__":
#     print("--- STARTING END-TO-END PIPELINE VALIDATION TEST ---")
    
#     # 1. Pre-process the raw review documents
#     print("[1/4] Pre-processing files...")
#     processed_files = pre_process()
#     all_chunks = []
    
#     # 2. Convert files into complete word-count chunks
#     print("[2/4] Slicing text into word chunks...")
#     for file_info in processed_files:
#         file_chunks = chunk_text_by_words(
#             location=file_info["location"],
#             filename=file_info["filename"],
#             text=file_info["text"]
#         )
#         all_chunks.extend(file_chunks)
        
#     print(f"-> Generated {len(all_chunks)} word chunks.")
    
#     # 3. Store the new chunks in the Vector DB
#     # Note: Make sure to drop your old database first if you want a clean reset!
#     if all_chunks:
#         print("[3/4] Indexing chunks inside vector store collection...")
#         embed_and_store(all_chunks)
#     else:
#         print("Aborting Test: No text chunks were successfully generated.")
#         exit()
        
#     print("\n--- DATABASE SETUP VERIFIED - PROCEEDING TO LLM QUERY ---")
    
#     # 4. Define a comprehensive test query
#     test_query = "Do the reviews mention the quality of the mongolian wok station?"
#     print(f"User Query: '{test_query}'\n")
    
#     # 5. Fetch matching text slices along with their associated IDs, distances, and metadata
#     print("Retrieving relevant matching contexts from ChromaDB...")
#     matched_contexts = retrieve(test_query)
    
#     # 6. Pass everything directly into your response generator function
#     print("Submitting query and context to LLM for final answer generation...\n")
#     final_output = generate_response(query=test_query, retrieved_chunks=matched_contexts)
    
#     # 7. Print the final answer output to verify proper execution and citation formatting
#     print("=" * 70)
#     print("FINAL BOT RESPONSE:")
#     print("=" * 70)
#     print(final_output)
#     print("=" * 70)