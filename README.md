# ⚡ AgentRAG — Autonomous Document Question Answering System

A complete, intelligent system that lets you upload any document (PDF, CSV, TXT, JSON) and ask questions about it in plain English. The system reads your document, understands it, finds the most relevant parts, and gives you a clear, accurate answer — like having a very smart assistant who has read your entire document.

---

## 📖 Table of Contents

1. [What Problem Does This Solve?](#what-problem-does-this-solve)
2. [How It Works — The Big Picture](#how-it-works--the-big-picture)
3. [Key Concepts Explained Simply](#key-concepts-explained-simply)
   - [RAG — Retrieval Augmented Generation](#rag--retrieval-augmented-generation)
   - [Parent-Child RAG](#parent-child-rag)
   - [Table-Aware Processing](#table-aware-processing)
   - [Embeddings and Vector Search](#embeddings-and-vector-search)
   - [Grade Labels](#grade-labels)
   - [Grounding Check](#grounding-check)
   - [Score Guide](#score-guide)
4. [Dashboard Metrics Explained](#dashboard-metrics-explained)
   - [Child Vectors](#child-vectors)
   - [Parent Chunks](#parent-chunks)
   - [Table Chunks](#table-chunks)
   - [Queries Run](#queries-run)
   - [Auto-Retries](#auto-retries)
5. [The Full Pipeline — Step by Step](#the-full-pipeline--step-by-step)
6. [Every Feature Explained](#every-feature-explained)
   - [Safety Guardrails](#safety-guardrails)
   - [Query Type Detection](#query-type-detection)
   - [Query Rewriting](#query-rewriting)
   - [Hybrid Retrieval — Dense + BM25](#hybrid-retrieval--dense--bm25)
   - [Cross-Encoder Reranking](#cross-encoder-reranking)
   - [Smart Context Compression](#smart-context-compression)
   - [Answer Generation](#answer-generation)
   - [Self-Reflection](#self-reflection)
   - [Hallucination Scoring](#hallucination-scoring)
   - [Conversation Memory](#conversation-memory)
   - [Multi-hop Retrieval](#multi-hop-retrieval)
   - [Agent Reasoning](#agent-reasoning)
7. [Settings Reference](#settings-reference)
8. [Understanding Your Results](#understanding-your-results)
9. [Quick Start Guide](#quick-start-guide)
10. [Technology Stack](#technology-stack)

---

## What Problem Does This Solve?

Imagine you have a 200-page PDF report. You want to find one specific number — like an employee's salary breakdown, or the date a contract was signed. You could read the whole thing, use Ctrl+F and hope you search the right word, or use a simple AI chatbot that might just make up an answer.

AgentRAG solves this properly. It reads your entire document, breaks it into organized pieces, stores them intelligently, and when you ask a question, it finds the most relevant pieces and uses an AI to write you a clear, accurate answer — with the exact pages it used as sources, and a score telling you how much to trust the answer.

The key difference from a regular AI chatbot: a regular chatbot answers from memory (its training data, which may be wrong or outdated). AgentRAG answers exclusively from *your document*, and it tells you where in your document it found the answer.

---

## How It Works — The Big Picture

Here is the journey from your document to your answer:

```
Your Document (PDF/CSV/TXT)
        ↓
   [1] Read & Extract Text
        ↓
   [2] Split Into Chunks (Parent + Child pieces)
        ↓
   [3] Convert Chunks to Numbers (Embeddings)
        ↓
   [4] Store in Vector Database (ChromaDB)
        ↓
   You Ask a Question
        ↓
   [5] Safety Check
        ↓
   [6] Detect Question Type
        ↓
   [7] Rewrite Question for Better Search
        ↓
   [8] Find Most Relevant Chunks (Retrieval)
        ↓
   [9] Re-rank by Relevance
        ↓
   [10] Compress Context
        ↓
   [11] Generate Answer (Groq LLM)
        ↓
   [12] Self-Check the Answer
        ↓
   [13] Score Answer Trustworthiness
        ↓
   You Get a Clear, Sourced Answer
```

---

## Key Concepts Explained Simply

### RAG — Retrieval Augmented Generation

**Simple definition:** RAG is a technique where an AI answers questions using information retrieved from a specific document, rather than from its general training knowledge.

Think of it like an open-book exam versus a closed-book exam. A regular AI chatbot takes a closed-book exam — it answers from memory. RAG gives the AI the textbook to look at before answering.

The word "Augmented" means "added to" or "enhanced." The AI's generation (writing) of an answer is augmented (enhanced) by retrieval (looking up the right pages first).

**Why does this matter?** Without RAG, an AI might confidently give you wrong answers because it is guessing from training data. With RAG, the AI can only answer from what is actually in your document, making the answer far more accurate and trustworthy.

---

### Parent-Child RAG

**Simple definition:** A smarter way of splitting documents where large sections (parents) are kept whole for context, but small pieces (children) are used for searching.

**The problem it solves:** If you split a document into tiny pieces for searching, you lose context. If you search for "annual bonus," a tiny chunk might just say "annual bonus: ₹50,000" without explaining *what job role, what department, what year* that bonus belongs to. The answer is technically there but lacks meaning.

**How it works:**

- **Parent chunk** — A large section of text (around 1800 characters). This is the complete context: a full paragraph, a complete table, or a full topic section. Parents are what the AI reads when writing your answer.
- **Child chunk** — A small piece extracted from the parent (around 400 characters). Children are what the system searches through to find relevant content quickly.

When you ask a question:

1. The system searches through all the small child chunks to find the most relevant ones
2. It then looks up which parent each child belongs to
3. It gives the AI the full parent context — not just the small matched piece

This way, search is precise (small pieces), but the answer has full context (large pieces).

**Analogy:** Imagine a library index card (child) that says "Chapter 5, page 47 — salary details." You use the index card to find the right page, then you read the whole page (parent), not just the index card entry.

---

### Table-Aware Processing

**Simple definition:** The system detects tables in your document and treats them differently from regular text — never splitting, compressing, or summarizing them.

**Why tables are special:** Tables contain structured data where every row and column relationship matters. If you split a salary table halfway, you might get the employee names in one chunk and the salary figures in another, making the data meaningless. Regular text-splitting algorithms do not understand table structure.

**What the system does:**

- When reading a PDF, it uses a specialized library (`pdfplumber`) to detect and extract tables as formatted Markdown tables
- Table chunks are stored as complete, intact units — they are never split into smaller pieces
- When you ask a question about numbers, amounts, or structured data, the system gives extra priority (a score boost of +0.15) to table chunks
- Tables are never compressed or summarized — they are passed to the AI exactly as they appear in your document

**Example:** If your PDF has an employee salary annexure table with columns for Basic Pay, HRA, PF, and Net Salary, the entire table is stored as one chunk. When you ask "What is the gross salary?", the system retrieves the complete table and the AI can read every component correctly.

---

### Embeddings and Vector Search

**Simple definition:** Embeddings convert text into lists of numbers so that a computer can measure how similar two pieces of text are in meaning.

**The problem:** Computers cannot directly understand language. They cannot know that "pay" and "salary" mean the same thing, or that "CEO" and "Chief Executive Officer" are the same role. Simple keyword search (like Ctrl+F) would miss these connections.

**How embeddings work:**

An embedding model (this system uses `all-MiniLM-L6-v2` by default) reads text and converts it into a list of 384 numbers — called a vector. Every piece of text gets its own unique list of numbers. The key property: text that means similar things gets similar numbers.

For example:

- "monthly salary" → [0.12, 0.87, 0.34, ...]
- "monthly pay" → [0.11, 0.86, 0.35, ...] (very close numbers)
- "favourite pizza" → [0.91, 0.03, 0.72, ...] (very different numbers)

**Cosine similarity** is the mathematical measure of how close two vectors are. A score of 1.0 means identical, 0.0 means completely unrelated.

**Vector database (ChromaDB):** All chunk embeddings are stored in ChromaDB. When you ask a question, your question is also converted to a vector, and ChromaDB finds the stored chunks whose vectors are closest — meaning most similar in meaning — to your question. This is called "semantic search" (meaning-based search) as opposed to keyword search.

---

### Grade Labels

**Simple definition:** A four-tier quality rating system (Excellent / Good / Better / Bad) that tells you how much to trust each answer.

The system automatically calculates a score (0–100%) measuring how closely the answer is connected to your actual document. It then assigns a human-readable grade:

| Grade                 | Score Range   | What It Means                                                                                        |
| --------------------- | ------------- | ---------------------------------------------------------------------------------------------------- |
| 🟢**Excellent** | 70% and above | Highly grounded. Almost all information came directly from your document. You can trust this answer. |
| 🔵**Good**      | 50% – 69%    | Mostly accurate. Main facts came from your document. Minor details may have small gaps.              |
| 🟡**Better**    | 30% – 49%    | Partially supported. Check key numbers and facts against the original document to be sure.           |
| 🔴**Bad**       | Below 30%     | Low document support. Try rephrasing your question or re-upload the correct file.                    |

These grades appear on every answer so you always know how much to rely on the response.

---

### Grounding Check

**Simple definition:** An automatic process that checks whether each sentence in the AI's answer is actually supported by the retrieved document sections.

"Grounding" means: is the answer grounded in (connected to and supported by) your document?

**How it works:**

1. The system takes the AI's generated answer and splits it into individual sentences
2. Each sentence is converted to an embedding (a list of numbers representing its meaning)
3. Each sentence's embedding is compared against the embeddings of the retrieved document chunks
4. Sentences that match closely to the document score high; sentences that don't match score low
5. The average across all sentences gives the overall grounding score

**What the labels mean:**

- **GROUNDED** — Average similarity above 60%. The answer closely matches your document.
- **PARTIAL** — Average similarity 40–60%. Most of the answer is from your document, but some parts may be inferred.
- **HALLUCINATED** — Average similarity below 40%. The answer has low connection to your document. Be cautious.

The system also identifies specific sentences that scored low, so you can see exactly which parts of the answer to verify.

---

### Score Guide

**Simple definition:** A reference panel displayed in the interface that explains what every score and grade means, so you never have to guess.

The Score Guide is a visual reference box (displayed permanently above the chat) that shows all four grades, their percentage ranges, and plain-English explanations. It serves as a constant reminder of what "70% grounded" actually means in practice.

This is particularly useful when sharing results with non-technical colleagues — they can look at the grade badge on an answer and immediately understand the quality level without needing to know anything about AI or vector similarity.

---

## Dashboard Metrics Explained

At the top of the main screen, you see five numbers. Here is what each one means:

### Child Vectors

**What it is:** The total number of small text pieces (child chunks) stored in the vector database.

**Why it matters:** This tells you the size of your searchable knowledge base. More vectors generally means more complete coverage of your document. A PDF with 50 pages might produce 500–2000 child vectors depending on how much text and how many tables it contains.

**In simple terms:** Think of these as individual index cards in a library card catalog. Each card represents a small, searchable piece of your document. When you ask a question, the system flips through all these cards to find the most relevant ones.

---

### Parent Chunks

**What it is:** The total number of large text sections (parent chunks) stored in memory.

**Why it matters:** Parents are what the AI actually reads when writing your answer. This number tells you how many complete, context-rich sections exist in your knowledge base.

**Relationship to child vectors:** There are always more child vectors than parent chunks. One parent might have 5–10 child chunks extracted from it.

**In simple terms:** If child vectors are index cards, parent chunks are the actual book pages those cards point to. The search finds the index card, the AI reads the full page.

---

### Table Chunks

**What it is:** The number of parent chunks that contain table data (as opposed to regular paragraph text).

**Why it matters:** This tells you how many structured data tables were successfully detected and preserved from your document. If you uploaded a financial report with 10 salary tables and this shows 0, something may have gone wrong in extraction — the tables may not have been formatted in a detectable way.

**In simple terms:** This is a count of how many complete, intact spreadsheet-like sections are stored. When you ask questions about numbers, amounts, or structured data, these chunks get priority.

---

### Queries Run

**What it is:** A simple counter of how many questions you have asked in total during this session.

**Why it matters:** Helps you track usage, especially if you are sharing the tool with a team and want to monitor activity.

**In simple terms:** The number of times you have pressed Enter to ask a question.

---

### Auto-Retries

**What it is:** The number of times the system automatically re-searched with a modified query because the initial search results were not good enough.

**Why it matters:** This is a sign of the system's intelligence. If the first search returns results with very low similarity scores (meaning nothing was really relevant), the system automatically tries alternative phrasings of your question rather than giving you a bad answer. A non-zero retry count means the system is working hard to find good answers even for difficult questions.

**In simple terms:** If you asked "what is the CTC?" and the first search came back empty, the system might automatically also search for "what is the total salary package?" and "what is the annual compensation?" — each of those re-searches counts as one auto-retry.

---

## The Full Pipeline — Step by Step

Every time you ask a question, your query goes through up to 10 processing stages. Here is what each one does:

### Stage 1 — 🛡️ Guard (Guardrails)

Your question is checked for safety before anything else happens.

Three checks run in sequence:

1. **Prompt injection detection** — Looks for phrases like "ignore all previous instructions" or "jailbreak mode." These are attempts to trick the AI into ignoring its rules. If detected, the query is blocked immediately.
2. **Toxicity scoring** — A small AI model rates the toxicity of your query on a scale of 0.0 to 1.0. A score above 0.75 causes the query to be blocked with an explanation.
3. **Safety result** — If both checks pass, the query is marked safe and moves forward. If not, you see a clear explanation of why it was blocked.

This stage protects both you and the system from misuse.

---

### Stage 2 — 🔍 Detect (Query Type Detection)

The system reads your question and classifies what type of answer you are looking for.

The five query types are:

- **Tabular** — You want numbers, amounts, or structured data. Triggered by words like "salary," "CTC," "breakdown," "amount," "₹," "table." When this type is detected, table chunks get a search priority boost, and compression is automatically skipped so no numbers are lost.
- **List** — You want a complete enumeration of items. Triggered by words like "list all," "what are," "give me all," "types of."
- **Comparison** — You want to compare two or more things side by side. Triggered by words like "vs," "difference between," "compare."
- **Factual** — You want a specific, precise fact. Triggered by question words like "who," "what," "when," "where," "which."
- **Narrative** — You want a detailed explanation or description. Triggered when no other pattern matches.

Knowing the query type helps every subsequent stage optimize its behavior.

---

### Stage 3 — ✏️ Rewrite (Query Rewriting)

Your original question is rewritten by a small, fast AI model to be better suited for document retrieval.

**Why is this needed?** The way people naturally ask questions is often not the best way to search a database. For example, "what's my pay?" might be better searched as "employee salary compensation package annual CTC breakdown."

The rewrite adds relevant technical terms, expands abbreviations, and makes the question more specific — without changing what you are asking. The original question is still used to understand your intent; the rewritten version is what gets sent to the search engine.

---

### Stage 4 — 📡 Retrieve (Hybrid Retrieval)

The system searches for the most relevant document chunks using two methods at once, then combines the results.

**Method 1 — Dense Search (Semantic):**
Your rewritten question is converted to an embedding (a list of numbers). ChromaDB finds chunks whose embeddings are closest to your question's embedding. This finds chunks that *mean* the same thing as your question, even if they use different words.

**Method 2 — BM25 (Keyword Search):**
BM25 is a classic information retrieval algorithm that counts keyword frequency and rarity. It finds chunks that contain the exact words from your question. This is good at finding specific terms, names, and numbers that semantic search might miss.

**Fusion (Combining Both):**
The results from both methods are merged using a weighted combination. The `α` (alpha) setting controls the balance: alpha = 0.65 means 65% weight to dense search and 35% to keyword search. You can adjust this in the sidebar.

After fusion, the system expands each matching child chunk to its full parent chunk, giving the AI complete context.

---

### Stage 5 — 🔀 Rerank (Cross-Encoder Reranking)

The initial retrieval gives a ranked list of chunks. Reranking re-scores them more accurately.

**The difference between initial retrieval and reranking:**

Initial retrieval uses "bi-encoders" — it converts the question and each chunk separately, then compares numbers. This is fast but approximate.

Reranking uses a "cross-encoder" — it reads the question and one chunk together, simultaneously, and scores specifically how well that chunk answers that question. This is slower (can only run on a small set) but much more accurate.

**The threshold check:** If all reranked scores are below a minimum threshold, the system automatically triggers a retry with modified query phrasings. This prevents the AI from getting bad input and producing a low-quality answer.

---

### Stage 6 — 🗜️ Compress (Smart Context Compression)

The retrieved text is condensed before being sent to the main AI model. This removes irrelevant sentences and reduces the amount of text the AI needs to read.

**Important: Compression is automatically skipped for:**

- Table chunks (numbers must be preserved exactly)
- Tabular query types
- List query types
- Any question containing words like "detail," "full," "complete," "all," "show"

**How compression works:** A small AI model reads each retrieved text chunk and extracts only the sentences that are directly relevant to your question. For example, if a chunk is a 500-word paragraph about company history but you asked about the CEO's name, the compressor extracts just the one sentence that names the CEO.

**Hallucination protection:** The compressor has a built-in guard against a specific failure mode. Sometimes AI models produce "hallucinated negations" — they say "there is no information about X" even when there clearly is. The system checks for this pattern and if detected, falls back to the original uncompressed text.

---

### Stage 7 — 💬 Generate (Answer Generation)

The main AI model (running on Groq's fast inference infrastructure) reads your question and all the retrieved context, then writes your answer.

**What makes this step careful:**

- The AI is given strict instructions: answer only from the provided sources, never make up information
- Every claim must be cited using source numbers: [Source 1], [Source 2], etc.
- Numbers, names, and dates must be copied exactly as they appear in the document
- For tabular queries, the answer must include a properly formatted Markdown table
- The AI is given a "citation map" — a list mapping each source number to its exact filename and page number

**Models available (all run on Groq):**

- `llama-3.3-70b-versatile` — Best quality, recommended for most use
- `meta-llama/llama-4-scout-17b` — Fast and capable
- `qwen/qwen3-32b` — Alternative with strong reasoning
- `llama-3.1-8b-instant` — Fastest, for quick answers
- `gemma2-9b-it` — Google's model, good for structured content

---

### Stage 8 — 🪞 Reflect (Self-Reflection)

After generating an answer, the system asks the same AI to critique that answer — then rewrites it if needed.

**The reflection loop:**

1. The AI grades its own answer on a scale of 0–100
2. It identifies specific issues: missing information, wrong structure, inaccurate claims
3. If the quality score is below 82, it rewrites the answer addressing those issues
4. This repeats up to the configured number of retries (1–3)
5. The final answer (with the highest quality score) is used

This is optional and adds processing time, but significantly improves answer quality for complex questions.

---

### Stage 9 — 🎯 Ground (Hallucination Scoring)

The system automatically checks whether the AI's answer is actually supported by the document, not invented.

This stage is described in detail in the [Grounding Check](#grounding-check) section above. It produces the grade badge (Excellent/Good/Better/Bad) and the grounding percentage that appears on every answer.

---

### Stage 10 — 📊 Eval (Evaluation)

The final stage computes and records metrics about the retrieval quality for this query.

Metrics computed:

- Number of chunks retrieved
- Average, maximum, and minimum cosine similarity scores
- Coverage score (how many good matches were found)
- Source diversity (how many different files were referenced)
- Number of table chunks retrieved

These metrics appear in the Evaluation tab and the query history table, helping you understand why some questions get better answers than others.

---

## Every Feature Explained

### Safety Guardrails

**What it is:** A three-layer filter that runs before processing any query.

**Layer 1 — Injection Pattern Detection:** Uses regular expressions (text pattern matching) to identify phrases that attempt to override the AI's instructions. Examples: "ignore all previous instructions," "pretend you are an uncensored AI," "jailbreak."

**Layer 2 — Toxicity Scoring:** Sends the query to a fast AI model that returns a JSON score (0.0–1.0) measuring harmfulness. Queries scoring above 0.75 are blocked.

**Layer 3 — Overall Safety Decision:** If any layer fails, the entire query is blocked and you receive a clear explanation.

**When to disable:** Generally, you should leave guardrails on. They have essentially zero impact on legitimate questions about your documents.

---

### Query Type Detection

Uses a set of keyword patterns to classify your question into one of five types: tabular, list, comparison, factual, or narrative. The detected type is shown as a badge on every answer (e.g., "📊 tabular" or "🎯 factual").

The type affects: which chunks get priority during retrieval, whether compression is applied, and how the answer generation prompt is structured.

---

### Query Rewriting

A fast, small AI model (`llama-3.1-8b-instant`) rewrites your question to improve retrieval. It receives a hint based on query type — for tabular queries, it is told to "focus on specific numbers, amounts, and structured data."

The rewrite happens silently. You ask in plain English; the system searches with a more technically precise version of your question.

---

### Hybrid Retrieval — Dense + BM25

Two fundamentally different search methods are run in parallel and their results are combined.

**Dense retrieval (semantic search):** Finds text that *means the same thing* as your question. Good for synonyms, paraphrasing, and conceptual similarity.

**BM25 (keyword retrieval):** Finds text that contains the *exact words* from your question. Good for specific names, numbers, technical terms, and exact phrases.

**Why combine them?** Each method has blind spots. Dense search might miss a specific contract clause number because it focuses on meaning not exact text. BM25 would find that exact clause but might miss a synonymous description of it. Together they cover each other's weaknesses.

**Alpha (α) setting:** Controls the mix. 0.65 (default) means 65% semantic, 35% keyword. For documents with lots of specific terminology (legal, financial), lower alpha slightly. For general documents, the default works well.

---

### Cross-Encoder Reranking

**What it is:** A second, more accurate scoring pass over the initial search results.

The initial search produces roughly 20 candidate chunks. The cross-encoder model (`cross-encoder/ms-marco-MiniLM-L-2-v2`) reads each candidate alongside your question and assigns a precise relevance score. Results are then re-sorted by this more accurate score.

**The threshold retry mechanism:** If the best cross-encoder score is below a minimum (RERANK_THRESHOLD = -5.0), the system automatically searches again with alternative query phrasings. This is the "Auto-Retries" counter you see on the dashboard.

---

### Smart Context Compression

**What it is:** A step that reduces the amount of text sent to the main AI model by extracting only the most relevant sentences.

**Why this helps:** AI models have a "context window" — a limit on how much text they can read at once. Sending 10,000 words of context when only 500 words are relevant wastes capacity and can cause the AI to miss important details buried in irrelevant text.

**The compression prompt:** The compressor AI is given strict rules — it must never write "there is no information" and must return at least 2–3 complete sentences. This prevents a failure mode where the compressor becomes too aggressive and eliminates everything.

**Auto-skip logic:** Compression is automatically skipped for tables (to preserve all numbers), for list queries (to capture all items), for tabular queries, and when the question contains words like "full," "complete," or "everything."

---

### Answer Generation

**What it is:** The main step where the AI reads everything and writes your answer.

The system prompt given to the generation AI is carefully structured with explicit rules:

- Write in fluent, professional English
- Never copy raw source text verbatim — synthesize and present naturally
- Cite every claim with [Source N]
- Copy numbers, names, and dates exactly
- For tabular queries, produce a Markdown table
- Never reference a page not in the provided sources

The AI receives a "citation map" listing: Source 1 = filename, page; Source 2 = filename, page. This ensures every citation in the answer is accurate and traceable.

---

### Self-Reflection

**What it is:** An optional quality improvement loop where the AI critiques and rewrites its own answer.

**The critique prompt:** The AI receives its own answer alongside the source material and rates quality 0–100, listing specific issues (e.g., "missing salary breakdown table," "CTC figure not mentioned," "answer is too vague").

**The improvement prompt:** If quality is below 82, a second AI call generates an improved answer specifically addressing the listed issues.

**When to use it:** Enable self-reflection for important questions where accuracy is critical. Disable it for quick, exploratory questions where speed matters more. Each reflection iteration adds 3–8 seconds.

---

### Hallucination Scoring

**What it is:** An automatic, mathematical check measuring how much the AI's answer is supported by your actual document.

"Hallucination" in AI means the AI confidently states something that is not true — it makes things up. This is a real problem with large language models. AgentRAG's hallucination scoring does not prevent hallucination but detects it after the fact and reports it to you.

**The math:** Each sentence in the answer is compared to each retrieved chunk using cosine similarity (same technique as vector search). If a sentence's meaning matches the document, it scores high. If its meaning does not appear anywhere in the retrieved context, it scores low.

**The output:** A percentage (e.g., "87% grounded"), a label (GROUNDED/PARTIAL/HALLUCINATED), and a list of specific sentences that scored low. You can use this to know which parts of the answer to double-check in your original document.

---

### Conversation Memory

**What it is:** A sliding window of previous questions and answers that is included as context in every new query.

**Why this matters:** Without memory, every question is independent. If you ask "who is the project manager?" and the system answers "Rahul Sharma," then you ask "what is her email?" — the system would not know who "her" refers to.

With memory, the last N turns of conversation (configurable from 1 to 8) are included in the context, allowing natural follow-up questions.

**What is stored:** Each human question (truncated to 300 characters) and each AI answer (truncated to 500 characters) from the most recent turns.

**Memory is stored in RAM only** — it resets when you clear data or refresh the page.

---

### Multi-hop Retrieval

**What it is:** An approach for complex questions that require information from multiple different parts of a document.

For a question like "Compare the salary of the Marketing Manager to the Finance Manager," the system needs to find information about two different roles potentially in two different sections of the document. Multi-hop retrieval decomposes this into sub-queries, retrieves information for each independently, and merges the results.

The fusion uses Reciprocal Rank Fusion (RRF), a mathematical method for combining multiple ranked lists fairly.

---

### Agent Reasoning

**What it is:** A chain-of-thought reasoning process where the AI plans its approach before answering.

Before generating the final answer, the AI works through explicit steps: ANALYZE (understand the question), RETRIEVE (identify what information is needed), SYNTHESIZE (combine information from sources), CONCLUDE (formulate the final answer).

This structured reasoning improves answers for complex questions by forcing the AI to think step by step rather than jumping straight to a conclusion.

---

## Settings Reference

### LLM (Groq)

**What it is:** The large language model that writes your answers.

All models run on Groq's inference hardware, which is significantly faster than most alternatives. Groq uses custom chips (LPUs — Language Processing Units) optimized specifically for running AI models.

**Choosing a model:**

- `llama-3.3-70b-versatile` — Best quality, 70 billion parameters, recommended default
- `meta-llama/llama-4-scout-17b` — Newer architecture, fast and capable
- `qwen/qwen3-32b` — Good reasoning, alternative to Llama
- `llama-3.1-8b-instant` — Small and very fast, useful for simple questions
- `gemma2-9b-it` — Google's model, good at following structured instructions

### Top-K Parent Chunks

**What it is:** How many parent chunks are retrieved and sent to the AI as context.

Higher K = more context, more complete answers, but slower and more expensive. Lower K = faster, focused answers, but might miss relevant information.

Start at 5 (default). Increase to 7–10 for complex research questions. Decrease to 3 for simple factual lookups.

### Dense Weight (α)

**What it is:** The balance between semantic search and keyword search in hybrid retrieval.

- α = 1.0 → pure semantic search (meaning-based)
- α = 0.0 → pure keyword search (exact word matching)
- α = 0.65 (default) → 65% semantic, 35% keyword

For documents with precise technical terms, names, or numbers (legal contracts, financial reports), slightly lower alpha (0.5–0.6) gives better results. For general-language documents, keep the default.

### Embedding Model

**What it is:** The model that converts text into numbers (embeddings) for vector search.

- `all-MiniLM-L6-v2` — Fast, good quality, recommended for most uses (384 dimensions)
- `all-mpnet-base-v2` — Higher quality, slower (768 dimensions)
- `paraphrase-multilingual-MiniLM-L12-v2` — Use for non-English documents

**Important:** Once you index documents with one embedding model, changing the model requires re-indexing everything, because the number formats are incompatible.

---

## Understanding Your Results

### The Source References Section

Every AI answer shows a section called "Sources Used" with colored cards. Each card represents one retrieved document chunk that was used to generate the answer.

Each source card shows:

- **File name** — Which document the information came from
- **Page number** — Which page in that document (only shown if the page was actually retrieved — the system never guesses page numbers)
- **Content type** — Whether it was a table or text
- **Cosine similarity** — How closely this chunk matched your question (as a percentage and grade)
- **Snippet** — A short preview of the actual text retrieved

### The Timing Strip

Below each answer, a row of timing information shows how many seconds each pipeline stage took. This helps you understand where time is spent and whether enabling/disabling certain features affects speed meaningfully.

### The Chunk Detail Panel

Clicking "Retrieved Chunks" opens a detailed view of every chunk the system found, showing the similarity bar, grade badge, grade explanation, full text preview, and the specific "best match" child text that triggered the retrieval.

---

## Quick Start Guide

### Step 1 — Get a Groq API Key

Go to [console.groq.com](https://console.groq.com), create a free account, and generate an API key. It starts with `gsk_`. Groq offers free credits for getting started.

### Step 2 — Enter and Validate Your Key

In the sidebar, paste your API key into the "Groq API Key" field and click "Validate Key." You should see a green "Connected" status.

### Step 3 — Upload Your Document

Click the file upload area and select your PDF, CSV, TXT, JSON, or Markdown file. You can upload multiple files at once — they all get indexed together.

### Step 4 — Process and Index

Click "⚡ Process & Index." The system will:

- Read and extract all text from your document
- Detect and preserve any tables
- Split content into parent and child chunks
- Convert all chunks to embeddings
- Store everything in the vector database

This typically takes 10–60 seconds depending on document size.

### Step 5 — Ask Questions

Switch to the Chat tab. You will see suggested questions automatically generated from your document. Click one or type your own question and press Enter.

### Step 6 — Review the Answer

Look at:

- The grade badge (Excellent/Good/Better/Bad) — overall trustworthiness
- The source cards — exactly where the information came from and which pages
- The grounding percentage — how much of the answer is from your document
- The chunk details panel — if you want to verify a specific claim

### Recommended Feature Combinations

**For financial or legal documents:** Enable guardrails + grounding check + self-reflection + reranking. Use `llama-3.3-70b-versatile`. Set alpha to 0.55.

**For quick information lookup:** Disable self-reflection to save time. Enable query rewriting + reranking. Use `llama-3.1-8b-instant` for speed.

**For multi-document research:** Enable conversation memory + query rewriting + reranking. Use Top-K = 8. Use `llama-3.3-70b-versatile`.

---

## Technology Stack

| Component          | Technology                           | Purpose                           |
| ------------------ | ------------------------------------ | --------------------------------- |
| UI Framework       | Streamlit                            | Web interface                     |
| Vector Database    | ChromaDB                             | Storing and searching embeddings  |
| Embedding Models   | SentenceTransformers                 | Converting text to numbers        |
| LLM Inference      | Groq API                             | Fast answer generation            |
| PDF Extraction     | pdfplumber                           | Reading PDFs with table detection |
| Keyword Search     | rank_bm25                            | BM25 keyword retrieval            |
| Reranking          | cross-encoder/ms-marco-MiniLM-L-2-v2 | Accurate relevance scoring        |
| Markdown Rendering | Python-markdown                      | Formatting AI answers             |
| Data Processing    | pandas, numpy                        | CSV handling and math             |

### Why Groq Specifically?

Groq builds custom hardware (LPUs) designed exclusively for running language models. This makes Groq significantly faster than GPU-based inference for the same model. The difference is noticeable: answers arrive in 1–3 seconds rather than 10–30 seconds. For a RAG system where speed matters for iterative research, this is a meaningful advantage.

### Why ChromaDB?

ChromaDB is an open-source, embedded vector database — meaning it runs locally inside your application without needing a separate server. It supports cosine similarity search, persistent storage, and metadata filtering. For a document QA application handling thousands to tens of thousands of chunks, ChromaDB provides sufficient performance with zero infrastructure overhead.

---

## Frequently Asked Questions

**Q: Why does the same question sometimes get different answers?**
A: Small variations in temperature (randomness) settings, rewriting, and context selection mean answers can vary slightly. For maximum consistency, disable query rewriting and set a very low temperature.

**Q: The grounding score is low (Bad) but the answer looks correct. Why?**
A: Grounding score measures similarity at the embedding level. If the AI summarized information differently from how it appears in the document, the phrasing might differ even if the meaning is correct. A Bad score means "verify this" — it does not automatically mean "this is wrong."

**Q: Can I upload multiple different documents and ask questions across all of them?**
A: Yes. Upload multiple files and click Process & Index together. All documents are indexed in the same vector database. The system retrieves from all of them simultaneously.

**Q: The table in my PDF is not being detected. What can I do?**
A: Some PDFs use images for tables rather than actual text. If the table was scanned or is a photo, pdfplumber cannot detect it. You would need to use OCR software first, then upload the text output. Alternatively, if you have the data in Excel or CSV, upload that directly — CSV processing always produces table chunks.

**Q: How much does it cost to use?**
A: Groq offers free API credits to start. The cost scales with usage — primarily the number and length of LLM calls (generation, compression, rewriting, reflection). The embedding models run locally on your machine and are free.

---

*Built with Streamlit · ChromaDB · SentenceTransformers · Groq*
