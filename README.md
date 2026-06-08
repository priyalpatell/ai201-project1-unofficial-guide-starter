# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section _after_ you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

My system covers student reviews of UC Davis's four dinning commons: Latitude, Tercero, Segundo, and Cuarto. It exposes students' experiences eating at the DCs, including food quality, top complaints, top recommendations, and much more. These reviews talk about the different atmospheres, making it easy to compare and contrast each dining common. This helps you get a clearer look at what it's really like to eat at Latitude, Tercero, Segundo, and Cuarto.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| #   | Source          | Type    | File path (in /docs)         |
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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

Before chunking, I focused on standardizing all the documents data to have the same format of date and then review. For preprocessing, I removed platform clutter lines like "Drag to change", "mass deleted", "Imagery ©", "COMMENTS (", "Community:", "Posted by:", "Score:", "Source:", and divider lines. I also extracted the location from the filename using keywords like latitude and tercero, normalized the different Google and Reddit date headers into a clean "Date: [value]" format by stripping out the extra brackets and user info, and added an empty line between each new review to keep the spacing uniform.

**Chunk size:**
I selected a 35-word (~200 characters) chunk size to effectively handle the dataset's variability, as the reviews consisted of either short fragments or longer text containing multiple distinct comments.

**Overlap:**
An overlap of 10 words (~60 characters) was implemented to prevent sentences from being cut off, ensuring contextual completeness.

**Why these choices fit your documents:**
Originally, I chose a larger chunk size of 400 characters with a 40-character overlap, but the chunks were too big and combined multiple smaller reviews, making it hard to capture the actual meaning. I found that switching to word-based chunking helped preserve individual reviews and reduced cutoffs. This gave me top-k contexts with smaller distances that contained much more relevant information for the queries.

**Final chunk count:**
The final chunk count using word chunking was 460, compared to character chunking which produced 447 chunks.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**
I chose "all-MiniLM-L6-v2" because it is lightweight enough to run directly on my laptop, and it supports English, which matches the language of my documents. Since it is free to use, I didn't have to worry about getting a paid API key or being charged. My chunk size is under the token limit, so no text is lost.

**Production tradeoff reflection:**
If deploying a system for real users, I would keep my context length choices the same because the reviews are already short, so I'd just stick with a model that handles that well. I would still opt for no multilingual support since all the data is in English, and I wouldn't need a domain-specific model because the reviews are just written in everyday language. Where I would change things is switching to an API-hosted model to get lower latency and faster response times, because running everything locally with a huge user base would quickly run into limits with how much data my system can hold and process.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**
To enforce grounding, my system prompt explicitly tells the model to use only the provided review chunks as its knowledge base and directly states that if an answer isn't in those chunks, it must say it doesn't know instead of making something up. I include guides such maintain a completely detached, analytical, and objective tone to reduce responses sounding conversational. Lastly, my prompt explicitly states to not summarize text and only output the cold, hard facts found directly in the contexts.

**How source attribution is surfaced in the response:**
For source attribution, I used incline citations that the model is required to use after every part of context text it uses in its response. This is rule requires the model to print the filename, such as (SEGUNDO_REVIEWS.TXT), right after each data referenced. This allows for each statement to be able to be traced back to its original source for verification. In combination with the grounding, this help prevents the model from synthesizing its own conclusions from the data it is given.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

```
+---+----------------------+----------------------+----------------------+----------------------+----------------------+
| # | Question             | Expected Answer      | System Response      | Retrieval Quality    | Response Accuracy    |
|   |                      |                      | (Summarized)         |                      |                      |
+---+----------------------+----------------------+----------------------+----------------------+----------------------+
| 1 | Which dining hall is | Latitude provides    | Latitude is          | Relevant             | Accurate             |
|   | recommended for      | the most             | recommended for      |                      |                      |
|   | international food?  | international        | international food   |                      |                      |
|   |                      | options.             | as it has options    |                      |                      |
|   |                      |                      | from various         |                      |                      |
|   |                      |                      | continents including |                      |                      |
|   |                      |                      | Asia, Africa,        |                      |                      |
|   |                      |                      | Europe, the Middle   |                      |                      |
|   |                      |                      | East, and South      |                      |                      |
|   |                      |                      | America              |                      |                      |
|   |                      |                      | (RESTAURANT_GURU_    |                      |                      |
|   |                      |                      | LATITUDE.TXT).       |                      |                      |
+---+----------------------+----------------------+----------------------+----------------------+----------------------+
| 2 | What are the top     | See if complaints    | At Cuarto, one       | Relevant             | Partially Accurate   |
|   | complaints about     | are correctly        | review notes that    |                      |                      |
|   | Cuarto's food        | identified and       | the food quality is  |                      |                      |
|   | quality?             | summarized.          | generally good       |                      |                      |
|   |                      |                      | (RESTAURANT_GURU_    |                      |                      |
|   |                      |                      | CUARTO.TXT).         |                      |                      |
|   |                      |                      | However, reviews     |                      |                      |
|   |                      |                      | from other locations |                      |                      |
|   |                      |                      | mention that         |                      |                      |
|   |                      |                      | Cuarto's food        |                      |                      |
|   |                      |                      | quality is perceived |                      |                      |
|   |                      |                      | as being similar to  |                      |                      |
|   |                      |                      | other dining         |                      |                      |
|   |                      |                      | commons, with one    |                      |                      |
|   |                      |                      | review stating that  |                      |                      |
|   |                      |                      | the food is "dog     |                      |                      |
|   |                      |                      | water" according to  |                      |                      |
|   |                      |                      | housemates and       |                      |                      |
|   |                      |                      | friends              |                      |                      |
|   |                      |                      | (REDDIT-THREAD-      |                      |                      |
|   |                      |                      | WFFTJW.TXT). Another |                      |                      |
|   |                      |                      | review mentions that |                      |                      |
|   |                      |                      | the food quality is  |                      |                      |
|   |                      |                      | usually the same     |                      |                      |
|   |                      |                      | between all the      |                      |                      |
|   |                      |                      | dining halls,        |                      |                      |
|   |                      |                      | including Cuarto     |                      |                      |
|   |                      |                      | (REDDIT-THREAD-      |                      |                      |
|   |                      |                      | WFFTJW.TXT). There   |                      |                      |
|   |                      |                      | is no additional     |                      |                      |
|   |                      |                      | information          |                      |                      |
|   |                      |                      | available about      |                      |                      |
|   |                      |                      | specific complaints  |                      |                      |
|   |                      |                      | regarding Cuarto's   |                      |                      |
|   |                      |                      | food quality.        |                      |                      |
+---+----------------------+----------------------+----------------------+----------------------+----------------------+
| 3 | Do the reviews       | See if reviews only  | The reviews do not   | Off-target           | Inaccurate           |
|   | mention the quality  | come from Segundo    | mention the quality  |                      |                      |
|   | of the wok station?  | and Tercero.         | of the wok station   |                      |                      |
|   |                      |                      | (REDDIT-THREAD-      |                      |                      |
|   |                      |                      | 1ES4792.TXT,         |                      |                      |
|   |                      |                      | GOOGLE_REVIEWS_      |                      |                      |
|   |                      |                      | SEGUNDO.TXT,         |                      |                      |
|   |                      |                      | GOOGLE_REVIEWS_      |                      |                      |
|   |                      |                      | LATITUDE.TXT).       |                      |                      |
+---+----------------------+----------------------+----------------------+----------------------+----------------------+
| 4 | Are there any        | Check if answer      | There is a mention   | Partially            | Partially            |
|   | mentions of students | returned is          | of a student feeling | Relevant             | Inaccurate           |
|   | getting sick after   | relevant.            | unwell after         |                      |                      |
|   | eating at one of the |                      | encountering the     |                      |                      |
|   | dining commons?      |                      | food at Tercero,     |                      |                      |
|   |                      |                      | specifically         |                      |                      |
|   |                      |                      | stating "I think I   |                      |                      |
|   |                      |                      | will vomit after     |                      |                      |
|   |                      |                      | smelling that odor"  |                      |                      |
|   |                      |                      | (GOOGLE_REVIEWS_     |                      |                      |
|   |                      |                      | TERCERO.TXT).        |                      |                      |
|   |                      |                      | Additionally, a      |                      |                      |
|   |                      |                      | review from Tercero  |                      |                      |
|   |                      |                      | mentions "uncooked"  |                      |                      |
|   |                      |                      | food (RESTAURANT_    |                      |                      |
|   |                      |                      | GURU_TERCERO.TXT).   |                      |                      |
|   |                      |                      | No direct mentions   |                      |                      |
|   |                      |                      | of students getting  |                      |                      |
|   |                      |                      | sick after eating    |                      |                      |
|   |                      |                      | are found in the     |                      |                      |
|   |                      |                      | reviews for Segundo  |                      |                      |
|   |                      |                      | (GOOGLE_REVIEWS_     |                      |                      |
|   |                      |                      | SEGUNDO.TXT) or the  |                      |                      |
|   |                      |                      | general reviews      |                      |                      |
|   |                      |                      | (REDDIT-THREAD-      |                      |                      |
|   |                      |                      | WFFTJW.TXT).         |                      |                      |
+---+----------------------+----------------------+----------------------+----------------------+----------------------+
| 5 | How does the         | See if relevant      | At Segundo, the food | Relevant             | Accurate             |
|   | atmosphere at        | answer is returned.  | tastes better        |                      |                      |
|   | Segundo compare to   |                      | compared to Tercero  |                      |                      |
|   | Tercero?             |                      | (GOOGLE_REVIEWS_     |                      |                      |
|   |                      |                      | SEGUNDO.TXT).        |                      |                      |
|   |                      |                      | However, Tercero has |                      |                      |
|   |                      |                      | a greater variety of |                      |                      |
|   |                      |                      | caffeine options     |                      |                      |
|   |                      |                      | (GOOGLE_REVIEWS_     |                      |                      |
|   |                      |                      | SEGUNDO.TXT). In     |                      |                      |
|   |                      |                      | terms of specific    |                      |                      |
|   |                      |                      | menu items, Segundo  |                      |                      |
|   |                      |                      | offers a tofu        |                      |                      |
|   |                      |                      | scramble that        |                      |                      |
|   |                      |                      | Tercero does not     |                      |                      |
|   |                      |                      | (REDDIT-THREAD-      |                      |                      |
|   |                      |                      | WFFTJW.TXT), while   |                      |                      |
|   |                      |                      | Tercero has more     |                      |                      |
|   |                      |                      | cooked vegetables at |                      |                      |
|   |                      |                      | Bistro and a better  |                      |                      |
|   |                      |                      | salad option         |                      |                      |
|   |                      |                      | (REDDIT-THREAD-      |                      |                      |
|   |                      |                      | WFFTJW.TXT). During  |                      |                      |
|   |                      |                      | dead hours           |                      |                      |
|   |                      |                      | (2-5ish), Tercero    |                      |                      |
|   |                      |                      | and Cuarto are       |                      |                      |
|   |                      |                      | considered better    |                      |                      |
|   |                      |                      | dining halls, as     |                      |                      |
|   |                      |                      | Segundo typically    |                      |                      |
|   |                      |                      | only offers pizza    |                      |                      |
|   |                      |                      | during these hours   |                      |                      |
|   |                      |                      | (REDDIT-THREAD-      |                      |                      |
|   |                      |                      | WFFTJW.TXT). Cuarto  |                      |                      |
|   |                      |                      | is considered nicer  |                      |                      |
|   |                      |                      | than Tercero, but    |                      |                      |
|   |                      |                      | has fewer options    |                      |                      |
|   |                      |                      | than Segundo         |                      |                      |
|   |                      |                      | (GOOGLE_REVIEWS_     |                      |                      |
|   |                      |                      | CUARTO.TXT,          |                      |                      |
|   |                      |                      | RESTAURANT_GURU_     |                      |                      |
|   |                      |                      | CUARTO.TXT).         |                      |                      |
+---+----------------------+----------------------+----------------------+----------------------+----------------------+
```

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**
Do the reviews mention the quality of the wok station?

**What the system returned:**
The reviews do not specifically mention the quality of the wok station (REDDIT-THREAD-1ES4792.TXT, GOOGLE_REVIEWS_SEGUNDO.TXT, GOOGLE_REVIEWS_LATITUDE.TXT).

**Root cause (tied to a specific pipeline stage):**
The failure occurred during the retrieval stage because the embedding model failed to capture the semantic connection between the query's specific term ("wok station") and how students actually described it in the reviews. Because the distance matching relied on general text similarities, it overlooked relevant chunks that likely used different phrasing or surrounding context to describe that station.

**What you would change to fix it:**
I first tried rephrasing the question because the wok station is also frequently referred to as the Mongolian wok station in the reviews. After I made this change, I noticed that adding the keyword "Mongolian" changed the embedding enough that the retrieval stage was able to discover the relevant contexts. With those correct chunks provided, the LLM was finally able to return a response that was relevant and partially accurate, drawing from multiple review comments and sources. This clearly shows how the pipeline's effectiveness is directly affected by query quality and specificity.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**
Because I had already mapped out my preprocessing requirements and chunking strategy in detail, I was able to easily prompt the AI to build those exact functions. This also made things much easier when I was writing my test questions. I could just go back to each section and mentally check if my planned chunk size and overlap would actually help answer each specific question while still handling the varying sizes of the reviews.

**One way your implementation diverged from the spec, and why:**
The spec constrained me to pick a specific chunk size and overlap. During implementation, I noticed the context matching in my retrieval function was returning a lot of inaccurate or off-target results. To diagnose the issue, I printed out the chunks to see how the information was getting split up and asked AI if switching from character splitting to word-count splitting would help. After implementing this word-based approach, it proved to be much more effective, returning context chunks with smaller vector distances and significantly more relevant information for the queries.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- _What I gave the AI:_
  I gave Gemini the Chunking Strategy section from my planning.md file and asked it to implement the pre_process() function.
- _What it produced:_
  It returned a function that correctly removed irrelevant characters and blank lines.
- _What I changed or overrode:_
  However, the final output format was incorrect; instead of formatting all the reviews into a single continuous string, it returned a list with each review as a separate entry. I re-prompted the AI with a concrete example of the exact output format I wanted, and it successfully fixed the error.

**Instance 2**

- _What I gave the AI:_
  I gave Gemini the original list of system rules I had drafted in the AI tool plan section of planning.md. I also provided an output I received from one of my queries and explained that the system needed to stop summarizing and synthesizing the contexts, and instead return direct facts with citations.
- _What it produced:_
  It returned a modified rule list that stated more explicitly how the model should format its response.
- _What I changed or overrode:_
  I implemented these new rules and re-ran the query to test if the response was more grounded. I repeated this iterative process until I ended up with a final system rule list that consistently produced grounded responses.
