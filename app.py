import gradio as gr

from generator import generate_response
from ingest import chunk_text_by_words, pre_process
from retriever import embed_and_store, get_collection, retrieve

def run_ingestion():
    print("Checking vector database status...")
    collection = get_collection()

    # Skip if data is already stored
    if collection.count() > 0:
        print(f"Database already populated ({collection.count()} chunks). Skipping ingestion.")
        return

    print("Database empty. Starting text pre-processing and chunking...")
    cleaned_text = pre_process()
    all_chunks = chunk_text_by_words(cleaned_text)

    if all_chunks:
        print(f"Embedding and storing {len(all_chunks)} chunks...")
        embed_and_store(all_chunks)
        print("Ingestion complete.")
    else:
        print("Warning: No chunks were generated during ingestion.")

def chat(message, tmp_chat_history):
    if not message.strip():
        return ""
    retrieved = retrieve(message)
    return generate_response(message, retrieved)

with gr.Blocks(title="UCD Dining Commons Bot") as demo:

    gr.HTML("""
        <div style="text-align:center; padding:1rem 0;">
            <h1 style="font-size:2rem; font-weight:800; color:#002855; margin:0;">
                UCD Dining Commons Bot
            </h1>
            <p style="color:#5c768d; font-size:1rem; margin:0.3rem 0 0;">
                Real student reviews and insights from Reddit, Restaurant Guru, and Google.
            </p>
        </div>
    """)

    with gr.Row():
        # Chat column
        with gr.Column(scale=3):
            gr.ChatInterface(
                fn=chat,
                chatbot=gr.Chatbot(height=400),
                textbox=gr.Textbox(
                    placeholder="Ask about Latitude, Tercero, Segundo, or Cuarto...",
                    container=False,
                ),
                examples=[
                    "Which location is recommended for international food?",
                    "What is the quality of the mongolian wok station?",
                    "What are the top complaints about Cuarto's food quality?",
                    "Are there any mentions of students getting sick after eating at one the dining commons?",
                    "How does the atmosphere at Segundo compared to Tercero?"
                ],
                cache_examples=False,
            )
		
        # Info column
        with gr.Column(scale=1, min_width=180):
            gr.HTML("""
                <div style="font-family: system-ui, sans-serif; padding: 0.5rem 0;">
                    <p style="font-size: 0.75rem; font-weight: 700; color: #002855; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.75rem;">
                        DC Locations
                    </p>
                    <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
                        <a href="https://maps.google.com/?q=Latitude+Dining+Commons+UC+Davis" target="_blank" style="text-decoration: none;">
                            <span style="background: #002855; color: white; padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer;">Latitude</span>
                        </a>
                        <a href="https://maps.google.com/?q=Tercero+Dining+Commons+UC+Davis" target="_blank" style="text-decoration: none;">
                            <span style="background: #002855; color: white; padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer;">Tercero</span>
                        </a>
                        <a href="https://maps.google.com/?q=Segundo+Dining+Commons+UC+Davis" target="_blank" style="text-decoration: none;">
                            <span style="background: #002855; color: white; padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer;">Segundo</span>
                        </a>
                        <a href="https://maps.google.com/?q=Cuarto+Dining+Commons+UC+Davis" target="_blank" style="text-decoration: none;">
                            <span style="background: #002855; color: white; padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600; cursor: pointer;">Cuarto</span>
                        </a>
                    </div>
                </div>
            """)
if __name__ == "__main__":
    run_ingestion()
    print("\n[SUCCESS] UCD Dining Commons Bot is ready! Launching interface...")
    
    # Fixed: Passed the theme parameters inside launch() instead
    demo.launch(theme=gr.themes.Soft(primary_hue="blue", secondary_hue="amber"))