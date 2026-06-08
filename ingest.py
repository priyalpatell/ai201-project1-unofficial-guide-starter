import os
import re

from config import DOCS_PATH

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

def chunk_text_by_characters(location: str, filename: str, text: str) -> list[dict]:
    """
    Splits a single file's text block into 400-character chunks with 
    a 40-character overlap. Generates a unique ID based on platform, 
    location, and count.
    """
    chunks_array = []
    clean_filename = os.path.splitext(filename)[0].replace(" ", "_")

    chunk_size = 200
    overlap = 60
    start = 0
    counter = 1
    
    # Fallback if the entire text block fits within one chunk
    if len(text) <= chunk_size:
        chunk_id = f"{clean_filename}_chunk_{counter}"
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
        
        chunk_id = f"{clean_filename}_chunk_{counter}"
        
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

def chunk_text_by_words(location: str, filename: str, text: str) -> list[dict]:
    chunks_array = []
    clean_filename = os.path.splitext(filename)[0].replace(" ", "_")
    
    # Split the massive text wall into an array of full words
    words = text.split()
    
    # 200 characters is roughly 35 words. 60 characters of overlap is roughly 10 words.
    chunk_size_words = 35  
    overlap_words = 10     
    
    start = 0
    counter = 1
    
    if len(words) <= chunk_size_words:
        chunk_id = f"{clean_filename}_{counter}"
        chunks_array.append({
            "text": " ".join(words),
            "location": location,
            "chunk_id": chunk_id
        })
        return chunks_array

    while start < len(words):
        end = start + chunk_size_words
        chunked_words = words[start:end]
        
        # Join the words back into a perfectly clean text string
        chunked_text = " ".join(chunked_words)
        
        chunk_id = f"{clean_filename}_{counter}"
        chunks_array.append({
            "text": chunked_text,
            "location": location,
            "chunk_id": chunk_id
        })
        
        counter += 1
        start += (chunk_size_words - overlap_words)
        
        if start >= len(words) - overlap_words:
            # Grab any remaining trailing words so nothing is left behind
            if start < len(words):
                chunked_text = " ".join(words[start:])
                chunks_array.append({
                    "text": chunked_text,
                    "location": location,
                    "chunk_id": f"{clean_filename}_{counter}"
                })
            break

    return chunks_array