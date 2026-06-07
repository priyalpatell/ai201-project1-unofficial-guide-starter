import os
import re

DOCS_PATH = "./docs"

def pre_process() -> list[dict]:
    structured_files = []
    
    if not os.path.exists(DOCS_PATH):
        return structured_files

    # Keywords to detect the location from the filename
    location_keywords = ["latitude", "tercero", "segundo", "cuarto"]
    
    # Platform clutter lines to completely filter out
    ignore_phrases = [
        "Drag to change", "mass deleted", "Imagery ©", "COMMENTS (",
        "Community:", "Posted by:", "Score:", "Source:", "========", "--------"
    ]

    for filename in os.listdir(DOCS_PATH):
        if not filename.endswith(".txt"):
            continue
            
        # 1. Extract location cleanly from filename
        lower_name = filename.lower()
        location = next((loc for loc in location_keywords if loc in lower_name), "any")
        
        with open(os.path.join(DOCS_PATH, filename), "r", encoding="utf-8") as f:
            lines = f.readlines()

        # 2. Filter lines and manage spacing between reviews
        clean_lines = []
        for line in lines:
            line_str = line.strip()
            
            # Skip empty lines or lines containing platform clutter
            if not line_str or any(phrase in line_str for phrase in ignore_phrases):
                continue
                
            is_new_review = False

            # Normalize Google/Guru date format '[Date: 8 months ago]' to 'Date: 8 months ago'
            if line_str.startswith("[Date:") and line_str.endswith("]"):
                line_str = line_str.replace("[Date:", "Date:").replace("]", "")
                is_new_review = True
                
            # Normalize Reddit user/date headers to 'Date: Aug 14, 2024'
            elif line_str.startswith("[u/") and "]" in line_str:
                brackets = re.findall(r'\[([^\]]+)\]', line_str)
                if len(brackets) >= 3:
                    line_str = f"Date: {brackets[2].strip()}"
                    is_new_review = True
            
            # If this line is the start of a new review (and not the very first line of the file),
            # append an empty string to force an extra space/newline before it.
            if is_new_review and clean_lines:
                clean_lines.append("")

            clean_lines.append(line_str)

        # 3. Combine remaining text into a single block for this file
        if clean_lines:
            combined_text = "\n".join(clean_lines)
            structured_files.append({
                "location": location,
                "filename": filename,
                "text": combined_text
            })

    return structured_files

def chunk_text(location: str, filename: str, text: str) -> list[dict]:
    """
    Splits a single file's text block into 400-character chunks with 
    a 40-character overlap. Generates a unique ID based on platform, 
    location, and count.
    """
    chunks_array = []
    lower_filename = filename.lower()
    
    # Simplified platform check based on your guarantee
    if "google" in lower_filename:
        source_platform = "google"
    elif "reddit" in lower_filename:
        source_platform = "reddit"
    else:
        source_platform = "guru"

    chunk_size = 340
    overlap = 40
    start = 0
    counter = 1
    
    # Fallback if the entire text block fits within one chunk
    if len(text) <= chunk_size:
        chunk_id = f"{source_platform}_{location}_chunk_{counter}"
        chunks_array.append({
            "text": text,
            "location": location,
            "chunk_id": chunk_id
        })
        return chunks_array

    # Sliding window extraction loop
    while start < len(text):
        end = start + chunk_size
        chunked_text = text[start:end]
        
        chunk_id = f"{source_platform}_{location}_chunk_{counter}"
        
        chunks_array.append({
            "text": chunked_text,
            "location": location,
            "chunk_id": chunk_id
        })
        
        counter += 1
        start += (chunk_size - overlap)
        
        # Stop sliding if the remaining text segment falls below the overlap window
        if start >= len(text) - overlap:
            break

    return chunks_array

# if __name__ == "__main__":
#     processed_files = pre_process()
#     global_total_chunks = 0
#     global_total_chars = 0
    
#     if not processed_files:
#         print("No files found or processed. Please verify your './docs' path.")
    
#     for file_info in processed_files:
#         fname = file_info["filename"]
#         loc = file_info["location"]
        
#         # Generate chunks specifically for this file
#         file_chunks = chunk_text(
#             location=loc,
#             filename=fname,
#             text=file_info["text"]
#         )
        
#         num_file_chunks = len(file_chunks)
#         file_lengths = [len(c["text"]) for c in file_chunks]
#         avg_file_size = sum(file_lengths) / num_file_chunks if num_file_chunks > 0 else 0
        
#         # Accumulate metrics for global totals
#         global_total_chunks += num_file_chunks
#         global_total_chars += sum(file_lengths)
        
#         # Print breakdown details per file
#         print(f"=========================================")
#         print(f"FILE: {fname} ({loc.upper()})")
#         print(f"-----------------------------------------")
#         print(f"Total Chunks: {num_file_chunks}")
#         print(f"Average Chunk Size: {avg_file_size:.2f} characters")
#         for chunk in file_chunks:
#             print(f"  -> ID: {chunk['chunk_id']} | Characters: {len(chunk['text'])}")
#         print(f"=========================================\n")
        
# 		# Print the text content of up to the first two chunks
#         print(f"\nSample Content (First 2 Chunks):")
#         for i, chunk in enumerate(file_chunks[:2]):
#             print(f"\n--- [ {chunk['chunk_id']} Text ] ---")
#             print(chunk["text"])
#             print(f"-----------------------------------")
            
#         print(f"========================================================================\n")

#     # Global summary printout
#     if global_total_chunks > 0:
#         global_avg = global_total_chars / global_total_chunks
#         print(f"##### GLOBAL PIPELINE SUMMARY #####")
#         print(f"Total Combined Chunks: {global_total_chunks}")
#         print(f"Overall Average Chunk Size: {global_avg:.2f} characters")
#         print(f"###################################")