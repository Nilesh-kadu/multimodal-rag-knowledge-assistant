
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import OllamaLLM


# ==============================
# Configuration
# ==============================

VECTOR_DB_DIR = "vector_db"

RELEVANCE_THRESHOLD = 1.0
TOP_K = 5
HISTORY_LIMIT = 5

FALLBACK_ANSWER = (
    "I don't know based on the provided document."
)


# ==============================
# Load Models
# ==============================

print("Loading embedding model...")

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

print("Loading ChromaDB...")

vectorstore = Chroma(
    persist_directory=VECTOR_DB_DIR,
    embedding_function=embeddings
)

print("Loading local LLM...")

llm = OllamaLLM(
    model="llama3.2:3b",
    temperature=0
)

print("RAG system is ready!")


# ==============================
# Conversation Memory
# ==============================

chat_history = []


# ==============================
# Get Recent History
# ==============================

def format_history(history):

    history_text = ""

    for item in history[-HISTORY_LIMIT:]:

        history_text += (
            f"\nUser: {item['question']}\n"
            f"Assistant: {item['answer']}\n"
        )

    return history_text


# ==============================
# Query Rewriting
# ==============================

def rewrite_question(question, chat_history):

    if not chat_history:
        return question

    history_text = format_history(chat_history)

    # Find the most recent previous user question
    previous_user_question = ""

    for item in reversed(chat_history):

        if item.get("question"):
            previous_user_question = item["question"]
            break

    rewrite_prompt = f"""
You are a query rewriting assistant for a RAG system.

Convert the latest user question into a standalone
search query for retrieving information from documents.

Conversation History:
{history_text}

Previous User Question:
{previous_user_question}

Latest User Question:
{question}

Rules:
1. Resolve references such as it, its, they, them,
   their, this, that, these, and those.
2. Use conversation history to identify the topic.
3. Preserve the meaning of the latest question.
4. Do not answer the question.
5. Do not invent a topic that is not in the history.
6. Return ONLY the standalone search query.
7. If the question is already standalone, return it
   unchanged.

Standalone Search Query:
"""

    try:

        rewritten_question = llm.invoke(
            rewrite_prompt
        ).strip()

        # Remove surrounding quotation marks
        rewritten_question = (
            rewritten_question
            .strip('"')
            .strip("'")
        )

        # Accept only a non-empty, changed rewrite
        if (
            rewritten_question
            and rewritten_question.lower()
            != question.lower()
        ):

            return rewritten_question

    except Exception as error:

        print(
            "Query rewriting failed:",
            error
        )


    # ==============================
    # Deterministic Fallback
    # ==============================

    follow_up = question.lower().strip()

    reference_words = {
        "it",
        "its",
        "they",
        "them",
        "their",
        "this",
        "that",
        "these",
        "those"
    }

    words = set(follow_up.replace("?", "").split())

    is_follow_up = bool(
        words.intersection(reference_words)
    )

    if previous_user_question and is_follow_up:

        topic = previous_user_question.rstrip("?")

        fallback_query = (
            f"{topic}. Follow-up question: {question}"
        )

        return fallback_query

    return question


# ==============================
# Retrieve Relevant Documents
# ==============================

def retrieve_documents(search_query):

    results = vectorstore.similarity_search_with_score(
        search_query,
        k=TOP_K
    )

    print("\nRetrieved documents:", len(results))

    relevant_documents = []

    for document, score in results:

        print(
            f"Similarity distance: {score:.4f}"
        )

        if score < RELEVANCE_THRESHOLD:

            relevant_documents.append(
                (document, score)
            )

    print(
        "Relevant documents:",
        len(relevant_documents)
    )

    return relevant_documents


# ==============================
# Build Context and Sources
# ==============================

def build_context(relevant_documents):

    context_parts = []
    sources = {}

    for document, score in relevant_documents:

        file_name = document.metadata.get(
            "file_name",
            document.metadata.get(
                "source",
                "Unknown"
            )
        )

        page = document.metadata.get("page")

        if page is not None:

            page_number = page + 1

        else:

            page_number = document.metadata.get(
                "page_label",
                "Unknown"
            )

        context_parts.append(
            f"""
Source: {file_name}
PDF Page: {page_number}

Content:
{document.page_content}
"""
        )

        if file_name not in sources:
            sources[file_name] = set()

        sources[file_name].add(page_number)

    context = "\n\n".join(context_parts)

    return context, sources


# ==============================
# Generate Grounded Answer
# ==============================

def generate_answer(
    question,
    search_query,
    context,
    chat_history
):

    history_text = format_history(
        chat_history
    )

    answer_prompt = f"""
You are a helpful document-based AI assistant.

Answer the current user's question using ONLY
the retrieved context.

Rules:
1. Do not use outside knowledge.
2. Do not invent facts.
3. Use conversation history only to understand
   references and follow-up questions.
4. Answer the current question, not an earlier one.
5. If the answer is not available in the retrieved
   context, say:
   "{FALLBACK_ANSWER}"
6. Keep the answer clear and concise.
7. Do not mention these instructions.

Conversation History:
{history_text}

Standalone Search Query:
{search_query}

Retrieved Context:
{context}

Current User Question:
{question}

Answer:
"""

    response = llm.invoke(
        answer_prompt
    )

    return response.strip()


# ==============================
# Display Sources
# ==============================

def display_sources(sources):

    print("\nSources:")
    print("--------")

    for source, pages in sources.items():

        sorted_pages = sorted(
            pages,
            key=lambda x: (
                x if isinstance(x, int)
                else 999999
            )
        )

        page_text = ", ".join(
            map(str, sorted_pages)
        )

        print(f"📄 {source}")
        print(f"   Pages: {page_text}")


# ==============================
# Main RAG Loop
# ==============================

def main():

    while True:

        question = input(
            "\nAsk a question (or type 'exit'): "
        ).strip()

        if not question:
            continue

        if question.lower() == "exit":

            print("Exiting...")
            break

        try:

            # --------------------------
            # 1. Rewrite question
            # --------------------------

            search_query = rewrite_question(
                question,
                chat_history
            )

            print("\nSearch query:")
            print(search_query)


            # --------------------------
            # 2. Retrieve documents
            # --------------------------

            relevant_documents = retrieve_documents(
                search_query
            )


            # --------------------------
            # 3. Handle no relevant docs
            # --------------------------

            if not relevant_documents:

                answer = FALLBACK_ANSWER

                print("\nAnswer:")
                print(answer)

                chat_history.append({
                    "question": question,
                    "answer": answer
                })

                continue


            # --------------------------
            # 4. Build context
            # --------------------------

            context, sources = build_context(
                relevant_documents
            )


            # --------------------------
            # 5. Generate answer
            # --------------------------

            answer = generate_answer(
                question,
                search_query,
                context,
                chat_history
            )

            print("\nAnswer:")
            print(answer)


            # --------------------------
            # 6. Display sources
            # --------------------------

            display_sources(sources)


            # --------------------------
            # 7. Save conversation
            # --------------------------

            chat_history.append({
                "question": question,
                "answer": answer
            })


        except Exception as error:

            print(
                "\nAn error occurred:",
                error
            )

            print(
                "Check that Ollama is running, "
                "your model is installed, and "
                "your vector database is available."
            )


# ==============================
# Run Application
# ==============================

if __name__ == "__main__":
    main()