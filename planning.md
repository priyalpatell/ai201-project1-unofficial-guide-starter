# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

This system uses student reviews to expose the reality of eating at the UC Davis dining commons: Latitude, Tercero, Segundo, and Cuarto. While the UC Davis websites only post menus, this system extracts what students actually experience: how the food tastes, whether popular stations run out of food, the vibe of each dinning commons, and how student sentiment changes across the quarter.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| #   | Source          | Type    | URL or file path             |
| --- | --------------- | ------- | ---------------------------- |
| 1   | google          | reviews | google_reviews_cuarto.txt    |
| 2   | google          | reviews | google_reviews_tercero.txt   |
| 3   | google          | reviews | google_reviews_segundo.txt   |
| 4   | google          | reviews | google_reviews_latitude.txt  |
| 5   | restaurant guru | reviews | restaurant_guru_cuarto.txt   |
| 6   | restaurant guru | reviews | restaurant_guru_tercero.txt  |
| 7   | restaurant guru | reviews | restaurant_guru_segundo.txt  |
| 8   | restaurant guru | reviews | restaurant_guru_latitude.txt |
| 9   | subreddit       | reviews | reddit-thread-1es4792.txt    |
| 10  | subreddit       | reviews | reddit-thread-wfftjw.txt     |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

For each review, I scraped only the review text and date to keep the metadata consistent across all data sources. Any additional preprocessing is done purely to ensure uniform formatting, regardless of where the data came from. Preserving the exact semantics of each review is critical for the system to generate high-quality chunks. If I used a fixed chunk size with an overlap, it might work well enough for short phrase-based reviews. However, longer paragraph-sized reviews often cover multiple sub-topics that could easily get cut in half, destroying their semantic meaning. For example, some reviews discuss multiple dining commons at once, while others focus entirely on just one. To account for these varying lengths and keep the context intact, I choose to use 400 chunk size and 40 overlap.

First, I will run all the data through pre_process(), which parses each file by inspecting the file name to extract the dining common location metadata ("latitude", "tercero", "segundo", "cuarto", or "any"). It then splits the text by date headers and removes system tags, line dividers, and empty lines. It also removes extra metadata provided in Reddit post headers and filters out specific non-comment-related text (such as "This post was mass deleted", "Drag to change, click to remove", and "Imagery ©"). For each valid review, it appends the date string and comment text to a text body and returns a list of structured dictionaries holding the location, filename, and text body.

Then, I will implement chunk_text() which will take text body and split it into 400 character chunks with 40 character overlap from the previous chunk. It will store chunks alongside location metadata.

**Chunk size:**
400 characters which is around 60-80 words

**Overlap:**
40 characters which is around 6-8 words

**Reasoning:**
Because reviews can range from short phrases to around one paragraph in size, this size limit ensures key semantic comments remain chunked together, while including partial surrounding information to reduce incomplete thoughts.

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
I want to use a lightweight embedding model because datasets are not larger than 200 lines and are in english. Thus, I choose to use all-MiniLM-L6-v2 via sentence-transformers.

**Top-k:**
Because student opinions very drastically per comments, I will need to select a larger number of embeddings. I will choose 5 embeddings to capture more opinions.

**Production tradeoff reflection:**
If deploying for real users, I would choose a model whose context length fits my specific text size or supports multiple languages if the documentation requires it. I would also accept higher latency in exchange for a model fine-tuned on a dataset similar to mine for better accuracy.

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| #   | Question                                                                                 | Expected answer                                            |
| --- | ---------------------------------------------------------------------------------------- | ---------------------------------------------------------- |
| 1   | Which dinning hall is recommended for international food?                                | Latitude provides the most international options.          |
| 2   | What are the top complaints about Cuarto's food quality?                                 | See if complaints are correctly identified and summarized. |
| 3   | Do the reviews mention the quality of the wok station?                                   | See if reviews only come from Segundo and Tercero.         |
| 4   | Are there any mentions of students getting sick after eating at one the dinning commons? | Check if answer returned is relevant.                      |
| 5   | How does the atmosphere at Segundo compared to Tercero?                                  | See if relevant answer is returned.                        |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Chunks splitting key information such as dates or linked ideas in a review. This could result incomplete context and harder to find relevent information for a query.

2. The documents are inconsistent with reddits threads being applicable to all dinning commons, while google and restaurant guru reviews being specific to a dinning common. This could impact the response quality and possible provide inconsistent information.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

```
========================================================================================================================
                                           CAMPUS DINING COMMONS RAG PIPELINE
========================================================================================================================

 +-----------------------+     +-----------------------+     +-----------------------+     +-----------------------+     +-----------------------+
 |  STAGE 1: INGESTION   |     |   STAGE 2: CHUNKING   |     |  STAGE 3: VECTOR DB   |     |  STAGE 4: RETRIEVAL   |     |  STAGE 5: GENERATION  |
 |                       |     |                       |     |                       |     |                       |     |                       |
 |  Source Files:        | --> |  Fixed-Size Splitter  | --> |  all-MiniLM-L6-v2     | --> |  Semantic Search      | --> |  Llama 3.3 70B        |
 |  Google, Reddit, &    |     |  400 Chars / 40 Ovlp  |     |  ChromaDB Storage     |     |  Top-k = 5 Chunks     |     |  Versatile LLM        |
 |  Restaurant Guru      |     |                       |     |                       |     |                       |     |                       |
 |  Reviews              |     |                       |     |                       |     |                       |     |                       |
 +-----------------------+     +-----------------------+     +-----------------------+     +-----------------------+     +-----------------------+

========================================================================================================================
```

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**
I will give Gemini my chunking strategy section and ask it to implement pre_process() and chunk_text(). For additional input, I will give it three examples of each type of review—one from Reddit, Restaurant Guru, and Google; this way it can see how the input structure differs and can create a universal pre_process() function to handle these cases. I expect ~400 character long chunks to be produced; I will verify by calculating the average chunk size and also printing these chunks out to see how my chunking strategy performed.

**Milestone 4 — Embedding and retrieval:**
I will give Gemini my architecture spec and my retrieval approach strategy. I will ask it to implement embed_and_store(), which takes in a list of chunks and stores them in the vector database along with the location metadata and chunk ID. To verify, I will have it print the total chunks stored in the database. For retrieval, I will have it implement retrieve(), which takes in a query and the $k$ constant and returns the top $k$ results. I will add print statements to verify that the top $k$ results are being returned.

**Milestone 5 — Generation and interface:**
I will give Gemini my architecture spec and specific instructions for the system vs. the user. For the system, I will tell it its role is to provide student sentiment on the dining commons at UC Davis, use only the retrieved rules, only answer if the answer is in the retrieved chunks, judge relevance if a specific dining common is mentioned in the query, and include the dining common (location) if known. For the user, I will pass in the query and the retrieved chunks. To verify, I will check how relevant the response is to the question or if it contains the specific information the query was centered around.

For the interface, I will give it my architecture spec and instruct it to create app.py. For app.py, it will implement the full architecture pipeline by calling the existing functions it created and make chat() a chat handler that will call retrieve() and generate responses. I will ask it to create a Gradio UI with a chat interface, textbox, and example questions. For the styling, I will have it match UC Davis school colors.
