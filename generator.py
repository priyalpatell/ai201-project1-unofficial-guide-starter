from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

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
					"You are a helpful, completely neutral assistant providing student sentiment on the dining commons at UC Davis. "
					"Use only the provided retrieved review chunks as your knowledge base. "
					"If the answer isn't contained in the chunks, explicitly state that you don't know instead of making something up. "
					"If the query talks about a specific location, prioritize chunks matching that location context. "
					"Include the specific dining common location in your text answer to make it clear where the feedback is coming from. "
					"Report the retrieved information as direct, objective data points that directly answer the user's question. "
					"STRICT STYLE AND TONAL RULES:\n"
					"1. Maintain a completely detached, analytical, and objective tone. Do not use conversational filler or speculative language like 'it seems', 'it looks like', or 'hopefully'.\n"
					"2. Do not adopt the emotional narrative of the reviews (e.g., do not write 'which was disappointing' or 'sadly'). State what happened as a cold fact (e.g., 'Reviews note instances of station closures').\n"
					"3. Avoid repetitive sentence structures (e.g., 'One review says... another review says...').\n"
					"4. Do not summarize the text, create an 'overall sentiment', or combine multiple reviews into a single conversational narrative.\n"
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