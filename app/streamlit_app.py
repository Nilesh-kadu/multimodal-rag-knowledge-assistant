import hashlib
from io import BytesIO
from pypdf import PdfReader
from PIL import Image, ImageEnhance, ImageOps
import pytesseract

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
import re
from pathlib import Path

import streamlit as st
from ui.theme import apply_theme
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Nexus-Ai | Nilesh",
    page_icon="⚫",
    layout="wide",
    initial_sidebar_state="expanded",
)
# ============================================================
# NEW UI THEME
# ============================================================

apply_theme()


#============================================================
# PROJECT PATHS & CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
OLLAMA_MODEL = "llama3.2:3b"


# ============================================================
# IMAGE OCR CONFIGURATION
# ============================================================

TESSERACT_CMD = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

IMAGE_CHUNK_SIZE = 700
IMAGE_CHUNK_OVERLAP = 100


# ============================================================
# RETRIEVAL CONFIGURATION
# ============================================================

TOP_K_PER_QUERY = 12

MAX_CONTEXT_CHUNKS = 10
RELEVANCE_THRESHOLD = 1.8

NO_ANSWER = "I don't know based on the provided document."


# ============================================================
# SESSION STATE
# ============================================================

# Store chat messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Store OCR text extracted from the uploaded image
if "image_ocr_text" not in st.session_state:
    st.session_state.image_ocr_text = ""

# Store the uploaded image filename
if "image_file_name" not in st.session_state:
    st.session_state.image_file_name = ""

if "uploaded_file_hashes" not in st.session_state:
    st.session_state.uploaded_file_hashes = set()    

# ============================================================
# APP HEADER
# ============================================================

# ============================================================
# APP HEADER
# ============================================================

st.html("""
<div style="
    width: 100%;
    text-align: center;
    padding: 10px 8px 34px;
    box-sizing: border-box;
">

    <div style="
        display: flex;
        justify-content: center;
        align-items: baseline;
        flex-wrap: nowrap;
        gap: 10px;
        width: 100%;
    ">

        <h1 style="
            margin: 0;
            padding: 0;
            color: #F8F7FF;
            font-size: clamp(1.6rem, 3vw, 2.35rem);
            font-weight: 700;
            letter-spacing: -0.8px;
            line-height: 1.3;
            white-space: nowrap;
        ">
            NEXUS AI — Intelligent Knowledge Workspace
        </h1>

        <span style="
            color: #B8B2C9;
            font-size: 0.9rem;
            font-weight: 500;
            white-space: nowrap;
        ">
            by Nilesh
        </span>

    </div>

    <p style="
        margin: 12px 0 0;
        color: #B8B2C9;
        font-size: 0.98rem;
        line-height: 1.6;
    ">
        Ask questions. Explore documents. Get grounded answers.
    </p>

</div>
""")
# ============================================================
# LOAD RAG COMPONENTS
# ============================================================

@st.cache_resource
def load_rag_components():
    """Load embeddings, ChromaDB, and local Ollama model."""

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    vectorstore = Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings,
    )

    llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.2,
    groq_api_key=st.secrets["GROQ_API_KEY"],
)

    return vectorstore, llm


try:
    vectorstore, llm = load_rag_components()

except Exception as exc:
    st.error("Failed to load RAG components.")
    st.exception(exc)
    st.stop()

# ============================================================
# DOCUMENT UPLOAD AND INGESTION
# ============================================================

def get_file_hash(file_bytes: bytes) -> str:
    """Generate a unique hash for the uploaded file."""
    return hashlib.sha256(file_bytes).hexdigest()

# def delete_file_from_chroma(file_name, vectorstore):
#     """Temporarily delete one indexed file by filename."""

#     existing = vectorstore.get(
#         where={"file_name": file_name},
#         include=[],
#     )

#     ids = existing.get("ids", [])

#     if not ids:
#         return 0

#     vectorstore.delete(ids=ids)

#     return len(ids)

def extract_pdf_documents(
    file_bytes: bytes,
    file_name: str,
) -> list[Document]:
    """Extract text from each PDF page."""

    reader = PdfReader(BytesIO(file_bytes))
    documents = []

    for page_number, page in enumerate(reader.pages):
        page_text = page.extract_text() or ""

        if not page_text.strip():
            continue

        documents.append(
            Document(
                page_content=page_text,
                metadata={
                    "source": file_name,
                    "file_name": file_name,
                    "page": page_number,
                    "source_type": "pdf",
                },
            )
        )

    return documents


def extract_txt_document(
    file_bytes: bytes,
    file_name: str,
) -> list[Document]:
    """Extract text from a TXT file."""

    try:
        text = file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        text = file_bytes.decode("latin-1")

    if not text.strip():
        return []

    return [
        Document(
            page_content=text,
            metadata={
                "source": file_name,
                "file_name": file_name,
                "page": "Text",
                "source_type": "txt",
            },
        )
    ]


def split_documents(
    documents: list[Document],
) -> list[Document]:
    """Split documents into overlapping chunks."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""],
    )

    return splitter.split_documents(documents)



def ingest_uploaded_file(uploaded_file, vectorstore):
    """
    Route PDF, TXT, and image files to the correct
    extraction and ChromaDB indexing pipeline.
    """

    file_name = Path(uploaded_file.name).name
    extension = Path(file_name).suffix.lower()

    # --------------------------------------------------------
    # IMAGE FILES: PNG, JPG, JPEG
    # --------------------------------------------------------
    if extension in [".png", ".jpg", ".jpeg"]:
        try:
            result = ingest_image_to_chroma(
                uploaded_file,
                vectorstore,
            )
            # Show whether image ingestion was successful
            if result["success"]:
             st.success(result["message"])

            # TEMPORARY TEST: Display extracted OCR text
             st.write("OCR text detected in image:")

             st.write(
                st.session_state.image_ocr_text
            )

            else:
             st.warning(result["message"])
            

            return (
                result["success"],
                result["message"],
            )

        except Exception as error:
            return (
                False,
                f"Failed to process image {file_name}: {error}",
            )

    # --------------------------------------------------------
    # PDF AND TXT FILES
    # --------------------------------------------------------
    file_bytes = uploaded_file.getvalue()

    if not file_bytes:
        return False, f"{file_name} is empty."

    file_hash = get_file_hash(file_bytes)

    try:
        if extension == ".pdf":
          documents = extract_pdf_documents(
            file_bytes,
            file_name,
          )

        elif extension == ".txt":
          documents = extract_txt_document(
            file_bytes,
            file_name,
          )

        else:
          return (
            False,
            f"Unsupported file type: {extension}",
          )
        if not documents:
          return (
            False,
            f"No extractable text found in {file_name}.",
          )

        chunks = split_documents(documents)

        if not chunks:
          return (
            False,
            f"No chunks generated for {file_name}.",
          )

        # ========================================================
        # ADD RELIABLE STRUCTURAL METADATA
        # ========================================================

        # Count how many chunks belong to each page.
        page_chunk_counts = {}

        for chunk in chunks:

          page = chunk.metadata.get(
            "page",
            "unknown",
          )

          page_chunk_counts[page] = (
            page_chunk_counts.get(page, 0) + 1
          )

        # Add metadata and deterministic chunk IDs.
        chunk_ids = []

        # Track the position of each chunk within its page.
        page_chunk_indexes = {}

        for index, chunk in enumerate(chunks):

          page = chunk.metadata.get(
            "page",
            "unknown",
          )

          current_page_index = (
            page_chunk_indexes.get(page, 0)
          )

          page_chunk_indexes[page] = (
            current_page_index + 1
          )

          # ----------------------------------------------------
          # Existing metadata - PRESERVED
          # ----------------------------------------------------

          chunk.metadata["file_hash"] = file_hash
          chunk.metadata["chunk_index"] = index

          # ----------------------------------------------------
          # New structural metadata
          # ----------------------------------------------------

          chunk.metadata["page_chunk_index"] = (
            current_page_index
          )

          chunk.metadata["page_chunk_count"] = (
            page_chunk_counts.get(page, 1)
          )

          chunk_ids.append(
            f"upload_{file_hash}_{index}"
          )

        # ========================================================
        # SKIP FILES THAT HAVE ALREADY BEEN INDEXED
        # ========================================================

        existing = vectorstore.get(
         where={"file_hash": file_hash},
         include=[],
        )

        if existing.get("ids"):
            return (
              True,
              f"{file_name} is already indexed.",
            )

        # ========================================================
        # ADD DOCUMENTS TO CHROMA
        # ========================================================

        vectorstore.add_documents(
         documents=chunks,
         ids=chunk_ids,
        )

        st.session_state.uploaded_file_hashes.add(
           file_hash
        ) 

        return (
           True,
           f"Successfully indexed {file_name}: "
           f"{len(chunks)} chunks created.",
        )

    except Exception as error:

        return (
         False,
         f"Failed to process {file_name}: {error}",
        )
# ============================================================
# CONVERSATION HISTORY
# ============================================================

def build_history(messages, limit=8):
    """Convert recent messages into readable conversation history."""

    if not messages:
        return "No previous conversation."

    lines = []

    for message in messages[-limit:]:
        role = message.get("role", "").upper()
        content = message.get("content", "").strip()

        if content:
            lines.append(f"{role}: {content}")

    return "\n".join(lines) if lines else "No previous conversation."


def get_previous_user_question(messages):
    """Return the most recent user question."""

    for message in reversed(messages):
        if message.get("role") == "user":
            content = message.get("content", "").strip()

            if content:
                return content

    return None


def get_previous_assistant_answer(messages):
    """Return the most recent assistant answer."""

    for message in reversed(messages):
        if message.get("role") == "assistant":
            content = message.get("content", "").strip()

            if content:
                return content

    return None


def get_previous_main_user_question(messages):
    """Find the latest user question that starts a topic."""

    for message in reversed(messages):
        if message.get("role") != "user":
            continue

        content = message.get("content", "").strip()

        if content and not is_follow_up_question(content):
            return content

    return get_previous_user_question(messages)


# ============================================================
# TOPIC EXTRACTION
# ============================================================

def extract_main_topic(question):
    """Remove common question prefixes."""

    q = question.strip().rstrip("?").strip()

    prefixes = [
        "what is the ",
        "what are the ",
        "what is a ",
        "what is an ",
        "what is ",
        "what are ",
        "what does ",
        "what do ",
        "explain ",
        "define ",
        "tell me about ",
        "describe ",
    ]

    for prefix in prefixes:
        if q.lower().startswith(prefix):
            q = q[len(prefix):].strip()
            break

    if q.lower().startswith("types of "):
        q = q[9:].strip()

    elif q.lower().startswith("type of "):
        q = q[8:].strip()

    q = re.sub(
        r"\s+types?$",
        "",
        q,
        flags=re.IGNORECASE,
    ).strip()

    return q


# ============================================================
# FOLLOW-UP DETECTION
# ============================================================

def is_follow_up_question(question):
    """Detect questions that depend on earlier conversation."""

    q = question.lower().strip()

    reference_words = {
        "it", "its", "they", "them", "their",
        "this", "that", "these", "those",
        "one", "ones", "above", "below",
        "first", "second", "third", "fourth",
        "former", "latter",
    }

    words = re.findall(r"\b[a-z]+\b", q)

    if any(word in reference_words for word in words):
        return True

    patterns = [
        "what about",
        "how about",
        "and what",
        "and how",
        "explain more",
        "tell me more",
        "why is that",
        "how does it",
        "how do they",
        "what does it",
        "which one",
        "which type",
        "what type",
        "what are its",
        "what is its",
        "its types",
        "their types",
        "first type",
        "second type",
        "third type",
        "fourth type",
        "first one",
        "second one",
        "third one",
        "fourth one",
        "explain me with example",
        "explain with example",
        "explain it with example",
        "explain this with example",
        "explain that with example",
    ]

    return any(pattern in q for pattern in patterns)


# ============================================================
# NUMBERED TYPE EXTRACTION
# ============================================================

def extract_numbered_type(answer, number):
    """Extract a numbered item from a previous assistant answer."""

    if not answer:
        return None

    pattern = rf"(?im)^\s*{number}\s*[\.\)\-:]\s*(.+?)\s*$"
    match = re.search(pattern, answer)

    if not match:
        return None

    type_name = match.group(1).strip()

    type_name = (
        type_name
        .replace("**", "")
        .replace("__", "")
        .replace("*", "")
        .strip()
    )

    if len(type_name) <= 150:
        return type_name

    return None


def get_requested_type_number(question):
    """Identify the ordinal type requested."""

    q = question.lower().strip()

    ordinal_patterns = {
        1: ["first type", "first one", "former"],
        2: ["second type", "second one", "latter"],
        3: ["third type", "third one"],
        4: ["fourth type", "fourth one"],
    }

    for number, patterns in ordinal_patterns.items():
        if any(pattern in q for pattern in patterns):
            return number

    return None


# ============================================================
# DETERMINISTIC QUERY REWRITE
# ============================================================

def fallback_rewrite(question, messages):
    """Resolve common follow-ups without relying on an LLM rewrite."""

    previous_question = get_previous_user_question(messages)

    if not previous_question:
     return question.strip()

    if not is_follow_up_question(question):
        return question.strip()

    topic = extract_main_topic(previous_question)
    q = question.lower().strip()

    requested_number = get_requested_type_number(question)

    if requested_number:
        previous_answer = get_previous_assistant_answer(messages)

        type_name = extract_numbered_type(
            previous_answer,
            requested_number,
        )

        if type_name:
            return f"Explain {type_name}."

        ordinal_names = [
            "first",
            "second",
            "third",
            "fourth",
        ]

        ordinal = ordinal_names[requested_number - 1]

        return f"Explain the {ordinal} type of {topic}."

    if "its types" in q or "what are its types" in q:
        return f"What are the types of {topic}?"

    if "their types" in q:
        return f"What are the types of {topic}?"

    if "what is its type" in q:
        return f"What is the type of {topic}?"

    if "what type" in q:
        return f"What type of {topic}?"

    if "which type" in q:
        return f"Which type of {topic}?"

    if "why is it important" in q:
        return f"Why is {topic} important?"

    if "how does it work" in q:
        return f"How does {topic} work?"
    if re.search(
    r"\b(explain|explain me|describe|elaborate)\b.*\b(example|examples)\b",
    q,
    ):
     return f"Explain {topic} with an example."

    return (
        f"Main topic: {topic}. "
        f"Follow-up question: {question}"
    )


# ============================================================
# QUERY REWRITING
# ============================================================

def rewrite_question(question, messages, llm):
    """Create a standalone search query for follow-up questions."""

    question = str(question or "").strip()

    if not question:
        return question

    if not messages or not is_follow_up_question(question):
        return question

    # ============================================================
    # 1. GET IMMEDIATELY PREVIOUS QUESTION
    # ============================================================

    previous_question = get_previous_user_question(messages)
    previous_answer = get_previous_assistant_answer(messages)

    previous_question = str(previous_question or "").strip()
    previous_answer = str(previous_answer or "").strip()

    print("DEBUG previous_question:", previous_question)
    print("DEBUG current_question:", question)
    print("DEBUG rewrite topic source:", previous_question)

    if not previous_question:
        return question

    # ============================================================
    # 2. NUMBERED FOLLOW-UP
    # ============================================================

    requested_number = get_requested_type_number(question)

    if requested_number:
        extracted = extract_numbered_type(
            previous_answer,
            requested_number,
        )

        if extracted:
            return f"Explain {extracted}."

    # ============================================================
    # 3. DETERMINISTIC FOLLOW-UP RESOLUTION
    #
    # Do NOT use the LLM for simple references such as:
    # "its types", "its purpose", "its advantages", etc.
    # ============================================================

    question_lower = question.lower().strip()

    # ------------------------------------------------------------
    # Extract topic from:
    # "What is polymorphism?"
    # "What is polymorphism in Java?"
    # "What is inheritance in Java?"
    # ------------------------------------------------------------

    topic = ""

    topic_match = re.search(
        r"\bwhat\s+is\s+(.+?)[?!.]?$",
        previous_question,
        flags=re.IGNORECASE,
    )

    if topic_match:
        topic = topic_match.group(1).strip()

    # Also support:
    # "What are polymorphism types?"
    # "Define polymorphism."
    if not topic:
        define_match = re.search(
            r"\b(?:define|explain)\s+(.+?)[?!.]?$",
            previous_question,
            flags=re.IGNORECASE,
        )

        if define_match:
            topic = define_match.group(1).strip()

    # ------------------------------------------------------------
    # Follow-up: "What are its types?"
    # ------------------------------------------------------------

    if topic and re.search(
        r"\bwhat\s+are\s+(?:its|their|these|those)\s+types\b",
        question_lower,
    ):
        return f"What are the types of {topic}?"

    # ------------------------------------------------------------
    # Follow-up: "What is its purpose?"
    # ------------------------------------------------------------

    if topic and re.search(
        r"\bwhat\s+is\s+(?:its|their)\s+purpose\b",
        question_lower,
    ):
        return f"What is the purpose of {topic}?"

    # ------------------------------------------------------------
    # Follow-up: "What are its advantages?"
    # ------------------------------------------------------------

    if topic and re.search(
        r"\bwhat\s+are\s+(?:its|their)\s+advantages\b",
        question_lower,
    ):
        return f"What are the advantages of {topic}?"

    # ------------------------------------------------------------
    # Follow-up: "What are its disadvantages?"
    # ------------------------------------------------------------

    if topic and re.search(
        r"\bwhat\s+are\s+(?:its|their)\s+disadvantages\b",
        question_lower,
    ):
        return f"What are the disadvantages of {topic}?"

    # ------------------------------------------------------------
    # Follow-up: "What are its features?"
    # ------------------------------------------------------------

    if topic and re.search(
        r"\bwhat\s+are\s+(?:its|their)\s+features\b",
        question_lower,
    ):
        return f"What are the features of {topic}?"

    # ------------------------------------------------------------
    # Follow-up: "How does it work?"
    # ------------------------------------------------------------

    if topic and re.search(
        r"\bhow\s+does\s+(?:it|this|that)\s+work\b",
        question_lower,
    ):
        return f"How does {topic} work?"

    # ------------------------------------------------------------
    # Follow-up: "What is it?"
    # ------------------------------------------------------------

    if topic and re.search(
        r"\bwhat\s+is\s+(?:it|this|that)\b",
        question_lower,
    ):
        return f"What is {topic}?"

    # ============================================================
    # 4. FALLBACK FOR OTHER COMPLEX FOLLOW-UPS
    #
    # Only here do we use the LLM.
    # ============================================================

    main_question = get_previous_main_user_question(messages)

    history_text = build_history(
        messages,
        limit=8,
    )

    rewrite_prompt = f"""
You rewrite a follow-up question into ONE standalone search query.

Return ONLY the rewritten search query.
Do not answer the question.
Do not add facts.

The CURRENT USER QUESTION refers primarily to the
IMMEDIATELY PREVIOUS USER QUESTION.

IMMEDIATELY PREVIOUS USER QUESTION:
{previous_question}

IMMEDIATELY PREVIOUS ASSISTANT ANSWER:
{previous_answer}

OLDER MAIN QUESTION:
{main_question}

CONVERSATION HISTORY:
{history_text}

CURRENT USER QUESTION:
{question}

Keep the topic of the immediately previous user question.
Do not switch to an older topic.

Return only one standalone search query.
"""

    try:
        rewritten = str(
            llm.invoke(rewrite_prompt)
        ).strip()

        for prefix in [
            "search query:",
            "standalone query:",
            "rewritten query:",
            "query:",
        ]:
            if rewritten.lower().startswith(prefix):
                rewritten = rewritten[
                    len(prefix):
                ].strip()
                break

        rewritten = (
            rewritten
            .strip('"')
            .strip("'")
            .strip()
        )

        if not rewritten:
            return previous_question

        if rewritten == "?":
            return previous_question

        if len(rewritten) > 400:
            return previous_question

        if len(rewritten.split()) < 3:
            return previous_question

        # ========================================================
        # Validate rewrite against immediately previous topic
        # ========================================================

        previous_words = set(
            re.findall(
                r"\b[a-zA-Z0-9_]+\b",
                previous_question.lower(),
            )
        )

        rewritten_words = set(
            re.findall(
                r"\b[a-zA-Z0-9_]+\b",
                rewritten.lower(),
            )
        )

        common_words = {
            "what", "are", "is", "the", "a", "an",
            "of", "how", "why", "does", "do", "can",
            "and", "to", "in", "on", "for", "with",
            "its", "it", "their", "they", "them",
            "this", "that", "these", "those",
            "type", "types", "explain",
            "tell", "me", "about", "which", "one",
            "first", "second", "third", "fourth",
        }

        previous_topic_words = (
            previous_words - common_words
        )

        rewritten_topic_words = (
            rewritten_words - common_words
        )

        if (
            previous_topic_words
            and not previous_topic_words.intersection(
                rewritten_topic_words
            )
        ):
            return previous_question

        return rewritten

    except Exception:
        return previous_question

# ============================================================
# MULTI-QUERY RETRIEVAL
# ============================================================


# ============================================================
# MULTI-QUERY RETRIEVAL
# ============================================================


def make_query_variants(question, search_query):
    """
    Generate focused query variants while preserving
    the important subject/topic terms from the original question.

    By default, LLM-based query expansion is disabled to avoid
    an additional Ollama inference and reduce memory usage.

    The original question and resolved search query are always
    retained for retrieval.
    """

    original_question = str(
        question or ""
    ).strip()

    original_search_query = str(
        search_query or ""
    ).strip()

    # Always retain the original user query.
    variants = [
        original_question,
        original_search_query,
    ]

    if not original_question and not original_search_query:
        return []

    # ========================================================
    # MEMORY-SAFE MODE
    # ========================================================
    #
    # Query expansion requires another Ollama inference.
    # Since the local model is running out of memory, keep
    # this disabled for now.
    #
    # Your original question and resolved search query are
    # still used for semantic retrieval.
    #
    # Set this to True later if you want to re-enable
    # LLM-based query expansion.
    # ========================================================

    USE_LLM_QUERY_EXPANSION = False

    if not USE_LLM_QUERY_EXPANSION:

        unique = []

        seen = set()

        for item in variants:

            item = re.sub(
                r"\s+",
                " ",
                item,
            ).strip()

            key = item.lower()

            if item and key not in seen:

                unique.append(item)

                seen.add(key)

        return unique[:2]

    # ========================================================
    # LLM QUERY EXPANSION
    # ========================================================

    prompt = f"""
You are a query expansion assistant for a document-based
RAG system.

Generate up to 3 alternative search queries.

Rules:
- Preserve the complete main subject/topic of the original question.
- Preserve important qualifiers that identify the subject.
- Do not remove important terms from the original question.
- Do not replace the main subject with another related concept.
- Do not introduce a different topic.
- Do not assume the answer.
- Do not hardcode domain-specific facts.
- Use different wording only when the meaning remains the same.
- Keep each query short and focused.
- Return only the queries, one per line.
- Do not include numbering or explanations.

Original question:
{original_question}

Search query:
{original_search_query}
"""

    try:

        response = llm.invoke(prompt)

        generated_text = (
            response.content
            if hasattr(response, "content")
            else str(response)
        )

        generated_queries = (
            generated_text.splitlines()
        )

        # Words that generally do not represent
        # the actual subject/topic.
        stop_words = {
            "what", "is", "are", "was", "were",
            "in", "on", "of", "the", "a", "an",
            "and", "or", "to", "for", "from",
            "how", "does", "do", "can", "could",
            "why", "when", "where", "which",
            "who", "this", "that", "these", "those",
            "about", "me", "tell", "explain",
            "define", "meaning", "means",
            "difference", "between",
            "types", "type", "kind", "kinds",
        }

        def get_meaningful_terms(text):

            terms = []

            for term in str(text or "").split():

                cleaned = term.lower().strip(
                    ".,?!:;()[]{}\"'"
                )

                if (
                    len(cleaned) > 2
                    and cleaned not in stop_words
                    and cleaned not in terms
                ):
                    terms.append(cleaned)

            return terms

        # ----------------------------------------------------
        # Get all important terms from ORIGINAL question
        # ----------------------------------------------------

        original_terms = get_meaningful_terms(
            original_question
        )

        required_terms = set(
            original_terms
        )

        # ----------------------------------------------------
        # Validate generated queries
        # ----------------------------------------------------

        for item in generated_queries:

            item = re.sub(
                r"^\s*[-*\d.)]+\s*",
                "",
                item,
            ).strip()

            # Ignore empty or excessively long variants.
            if (
                not item
                or len(item) > 250
            ):
                continue

            candidate_terms = set(
                get_meaningful_terms(item)
            )

            # ------------------------------------------------
            # Every meaningful term from the original question
            # must remain in the generated query.
            # ------------------------------------------------

            if (
                required_terms
                and not required_terms.issubset(
                    candidate_terms
                )
            ):
                continue

            variants.append(item)

    except Exception as exc:

        # # Do not break RAG retrieval if query expansion fails.
        # # The original question and search query remain usable.
        # if show_debug:

        #     st.warning(
        #         f"Query expansion failed: {exc}"
        #     )
        pass

    # ========================================================
    # NORMALIZE AND DEDUPLICATE
    # ========================================================

    unique = []

    seen = set()

    for item in variants:

        item = re.sub(
            r"\s+",
            " ",
            item,
        ).strip()

        key = item.lower()

        if (
            item
            and key not in seen
        ):

            unique.append(item)

            seen.add(key)

    # Keep original queries plus no more than
    # 3 generated alternatives.
    return unique[:5]

######################################
#######################################

def has_explicit_type_evidence(question, search_query, documents):
    """
    Validate whether retrieved documents explicitly support
    a types/kinds/categories question.

    This function is domain-independent.
    It does not contain any hardcoded concepts.
    """

    text = str(
    search_query or question or ""
     ).strip().lower()

    # --------------------------------------------------------
    # Detect question intent
    # --------------------------------------------------------

    intent = detect_question_intent(
     search_query or question
    )

    # This validator currently handles only
    # types/kinds/categories questions.
    #
    # Other intents are allowed to continue
    # through the existing pipeline.
    if intent != "types":
     return True

    # --------------------------------------------------------
    # Extract target concept
    # --------------------------------------------------------

    match = re.search(
        r"\b(?:types?|kinds?|categories?)\s+of\s+"
        r"(.+?)(?:\s+\b(?:in|on|for|within|under)\b|\?|$)",
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return False

    target = match.group(1).strip(
        " .,:;?!"
    )

    if not target:
        return False

    # --------------------------------------------------------
    # Normalize target terms
    # --------------------------------------------------------

    stop_words = {
        "what",
        "is",
        "are",
        "the",
        "a",
        "an",
        "of",
        "in",
        "on",
        "for",
        "with",
        "and",
        "or",
        "to",
        "from",
        "types",
        "type",
        "kinds",
        "kind",
        "categories",
        "category",
    }

    target_terms = [
        word.lower().strip(
            ".,?!:;()[]{}\"'"
        )
        for word in target.split()
        if len(word.strip()) > 2
        and word.lower().strip(
            ".,?!:;()[]{}\"'"
        ) not in stop_words
    ]

    if not target_terms:
        return False

    # --------------------------------------------------------
    # Inspect each retrieved document
    # --------------------------------------------------------

    for document in documents:

        content = (
            document.page_content or ""
        ).strip()

        if not content:
            continue

        normalized = re.sub(
            r"\s+",
            " ",
            content.lower(),
        )

        # ----------------------------------------------------
        # 1. Explicit:
        #    types of <target>
        # ----------------------------------------------------

        target_pattern = r"\s+".join(
            re.escape(term)
            for term in target_terms
        )

        if re.search(
            rf"\b(?:types?|kinds?|categories?)"
            rf"\s+of\s+{target_pattern}\b",
            normalized,
            flags=re.IGNORECASE,
        ):
            return True

        # ----------------------------------------------------
        # 2. Explicit:
        #    <target> has/have N types
        # ----------------------------------------------------

        if re.search(
            rf"\b{target_pattern}\b"
            rf".{{0,120}}?"
            rf"\b(?:has|have|contains?|includes?)\b"
            rf".{{0,40}}?"
            rf"\b(?:types?|kinds?|categories?)\b",
            normalized,
            flags=re.IGNORECASE,
        ):
            return True

        # ----------------------------------------------------
        # 3. Local line-based association
        # ----------------------------------------------------

        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        for index, line in enumerate(lines):

            line_lower = line.lower()

            target_present = all(
                re.search(
                    rf"\b{re.escape(term)}\b",
                    line_lower,
                )
                for term in target_terms
            )

            # Same line contains target + type marker.
            if target_present and re.search(
                r"\b(?:types?|kinds?|categories?)\b",
                line_lower,
                flags=re.IGNORECASE,
            ):
                return True

            # ------------------------------------------------
            # Target heading followed closely by type marker
            # ------------------------------------------------

            if target_present:

                nearby_lines = lines[
                    index + 1:index + 4
                ]

                for nearby_line in nearby_lines:

                    if re.search(
                        r"\b(?:types?|kinds?|categories?)\s*:?",
                        nearby_line,
                        flags=re.IGNORECASE,
                    ):
                        return True

    return False
#####################################################################
#####################################################################
def detect_question_intent(question):
    """
    Detect the user's requested information type
    without depending on any specific domain or concept.

    Returns:
        definition
        types
        advantages
        disadvantages
        purpose
        uses
        examples
        comparison
        steps
        general
    """

    text = str(question or "").strip().lower()

    if not text:
        return "general"

    # Types / categories
    if re.search(
        r"\b(types?|kinds?|categories?)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return "types"

    # Advantages / benefits
    if re.search(
        r"\b(advantages?|benefits?|pros|merits?)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return "advantages"

    # Disadvantages / limitations
    if re.search(
        r"\b(disadvantages?|limitations?|drawbacks?|cons)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return "disadvantages"

    # Purpose / reason
    if re.search(
        r"\b(purpose|why|reason)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return "purpose"

    # Uses / applications
    if re.search(
        r"\b(uses?|usage|applications?|application)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return "uses"

    # Examples
    if re.search(
        r"\b(examples?|instances?)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return "examples"

    # Comparison
    if re.search(
        r"\b(compare|comparison|difference|differences|vs\.?|versus)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return "comparison"

    # Steps / procedure
    if re.search(
        r"\b(steps?|procedure|process|how to)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return "steps"

    # Definition / explanation
    if re.search(
        r"\b(what is|what are|define|definition|meaning|explain)\b",
        text,
        flags=re.IGNORECASE,
    ):
        return "definition"

    return "general"
def validate_intent_evidence(question, relevant_documents):
    """
    Validate whether retrieved document chunks contain
    explicit evidence for the user's requested intent.

    This function is domain-independent.

    Returns:
        True  -> evidence appears sufficient
        False -> evidence appears insufficient
    """

    question = str(question or "").strip()

    if not question:
        return False

    if not relevant_documents:
        return False

    intent = detect_question_intent(question)

    # Combine retrieved chunks into one searchable text.
    combined_text = " ".join(
        (
            document.page_content
            if hasattr(document, "page_content")
            else ""
        )
        for document in relevant_documents
    )

    combined_text = re.sub(
        r"\s+",
        " ",
        combined_text,
    ).strip().lower()

    if not combined_text:
        return False

    # --------------------------------------------------------
    # TYPES / CATEGORIES
    # --------------------------------------------------------

    if intent == "types":

        # The existing retrieval layer already performs
        # concept/type association filtering.
        #
        # Here we only require explicit type-oriented
        # evidence to remain in the retrieved context.

        return bool(
            re.search(
                r"\b(types?|kinds?|categories?)\b",
                combined_text,
                flags=re.IGNORECASE,
            )
        )

    # --------------------------------------------------------
    # ADVANTAGES / BENEFITS
    # --------------------------------------------------------

    if intent == "advantages":

        return bool(
            re.search(
                r"\b("
                r"advantages?|"
                r"benefits?|"
                r"pros|"
                r"merits?|"
                r"beneficial|"
                r"benefit"
                r")\b",
                combined_text,
                flags=re.IGNORECASE,
            )
        )

    # --------------------------------------------------------
    # DISADVANTAGES / LIMITATIONS
    # --------------------------------------------------------

    if intent == "disadvantages":

        return bool(
            re.search(
                r"\b("
                r"disadvantages?|"
                r"limitations?|"
                r"drawbacks?|"
                r"cons|"
                r"limitations"
                r")\b",
                combined_text,
                flags=re.IGNORECASE,
            )
        )

    # --------------------------------------------------------
    # PURPOSE
    # --------------------------------------------------------

    if intent == "purpose":

        return bool(
            re.search(
                r"\b("
                r"purpose|"
                r"reason|"
                r"why|"
                r"used\s+for|"
                r"designed\s+for"
                r")\b",
                combined_text,
                flags=re.IGNORECASE,
            )
        )

    # --------------------------------------------------------
    # USES / APPLICATIONS
    # --------------------------------------------------------

    if intent == "uses":

        return bool(
            re.search(
                r"\b("
                r"uses?|"
                r"usage|"
                r"applications?|"
                r"applied|"
                r"used"
                r")\b",
                combined_text,
                flags=re.IGNORECASE,
            )
        )

    # --------------------------------------------------------
    # EXAMPLES
    # --------------------------------------------------------

    if intent == "examples":

        return bool(
            re.search(
                r"\b("
                r"examples?|"
                r"instances?|"
                r"for\s+example|"
                r"such\s+as"
                r")\b",
                combined_text,
                flags=re.IGNORECASE,
            )
        )

    # --------------------------------------------------------
    # COMPARISON
    # --------------------------------------------------------

    if intent == "comparison":

        return bool(
            re.search(
                r"\b("
                r"difference|"
                r"differences|"
                r"compare|"
                r"comparison|"
                r"versus|"
                r"\bvs\b"
                r")\b",
                combined_text,
                flags=re.IGNORECASE,
            )
        )

    # --------------------------------------------------------
    # STEPS / PROCEDURE
    # --------------------------------------------------------

    if intent == "steps":

        return bool(
            re.search(
                r"\b("
                r"steps?|"
                r"procedure|"
                r"process|"
                r"first|"
                r"second|"
                r"third|"
                r"then|"
                r"finally"
                r")\b",
                combined_text,
                flags=re.IGNORECASE,
            )
        )

    # --------------------------------------------------------
    # DEFINITION / GENERAL
    # --------------------------------------------------------

    # For definition/general questions, the existing
    # semantic retrieval + keyword/document filtering
    # remains the primary evidence mechanism.

    return True
# ============================================================
# IMPROVED MULTI-QUERY RETRIEVAL
# ============================================================
def retrieve_documents(
    question,
    search_query,
    vectorstore,
    image_only=False,
):
    """
    Retrieve relevant documents/chunks for text and image questions.

    Text/PDF retrieval:
    - Searches using query variants.
    - Restricts search to uploaded documents.
    - Groups candidates by uploaded file.
    - Uses document-level keyword support to reduce
      cross-document semantic contamination.
    - Keeps semantic distance as the primary signal
      when selecting chunks.

    Image retrieval:
    - Searches only the currently uploaded image.
    - Existing OCR/image behavior is preserved.
    """

    query_variants = make_query_variants(
        question,
        search_query,
    )

    best_by_id = {}

    # ========================================================
    # HELPER: IMPORTANT QUERY TERMS
    # ========================================================

    stop_words = {
        "what", "is", "are", "was", "were",
        "in", "on", "of", "the", "a", "an",
        "and", "or", "to", "for", "from",
        "how", "does", "do", "can", "could",
        "why", "when", "where", "which",
        "who", "this", "that", "these", "those",
        "about", "me", "tell", "explain",
        "define", "meaning", "means",
        "difference", "between",
        "types", "type", "kind", "kinds",
        "used", "use", "using",
    }

    def get_meaningful_terms(text):

        terms = []

        for term in str(text or "").split():

            cleaned = term.lower().strip(
                ".,?!:;()[]{}\"'"
            )

            if (
                len(cleaned) > 2
                and cleaned not in stop_words
                and cleaned not in terms
            ):
                terms.append(cleaned)

        return terms

    original_terms = get_meaningful_terms(
        question
    )

    search_terms = get_meaningful_terms(
        search_query
    )

    # Combine terms from the original question
    # and resolved search query.
    query_terms = list(
        dict.fromkeys(
            original_terms + search_terms
        )
    )

    # ========================================================
    # TYPES QUERY DETECTION
    # ========================================================

    question_lower = str(
        search_query or question or ""
    ).lower()

    asks_for_types = bool(
        re.search(
            r"\b(types?|kinds?|categories?)\b",
            question_lower,
        )
    )

    # ========================================================
    # 1. SEARCH WITH EACH QUERY VARIANT
    # ========================================================

    for query in query_variants:

        try:

            # ==================================================
            # IMAGE QUESTION
            # ==================================================

            if image_only:

                current_image_hash = (
                    st.session_state.get(
                        "image_hash",
                        "",
                    )
                )

                if current_image_hash:

                    results = (
                        vectorstore
                        .similarity_search_with_score(
                            query,
                            k=TOP_K_PER_QUERY,
                            filter={
                                "$and": [
                                    {
                                        "source_type": "image"
                                    },
                                    {
                                        "image_hash":
                                        current_image_hash
                                    },
                                ]
                            },
                        )
                    )

                else:

                    results = []

            # ==================================================
            # NORMAL PDF / TXT QUESTION
            # ==================================================

            else:

                stored_data = vectorstore.get(
                    include=["metadatas"],
                )

                uploaded_file_hashes = list(
                    {
                        metadata.get("file_hash")
                        for metadata in (
                            stored_data.get(
                                "metadatas",
                                []
                            )
                        )
                        if metadata.get("file_hash")
                    }
                )

                if not uploaded_file_hashes:

                    results = []

                else:

                    results = (
                        vectorstore
                        .similarity_search_with_score(
                            query,
                            k=TOP_K_PER_QUERY,
                            filter={
                                "file_hash": {
                                    "$in":
                                    uploaded_file_hashes
                                }
                            },
                        )
                    )

        except Exception as exc:

            st.warning(
                f"Search failed for query "
                f"'{query}': {exc}"
            )

            continue

        # ====================================================
        # STORE BEST RESULT FOR EACH UNIQUE CHUNK
        # ====================================================

        for document, score in results:

            metadata = (
                document.metadata or {}
            )

            content = (
                document.page_content or ""
            ).strip()

            if not content:
                continue

            try:
                distance = float(score)
            except (TypeError, ValueError):
                continue

            key = (
                metadata.get("file_hash")
                or metadata.get("file_name")
                or metadata.get("filename")
                or metadata.get("source")
                or "",
                metadata.get(
                    "page",
                    metadata.get(
                        "page_label",
                        "",
                    ),
                ),
                content,
            )

            if (
                key not in best_by_id
                or distance < best_by_id[key][1]
            ):
                best_by_id[key] = (
                    document,
                    distance,
                    query,
                )

    # ========================================================
    # 2. SORT ALL CANDIDATES BY SEMANTIC DISTANCE
    # ========================================================

    candidates = sorted(
        best_by_id.values(),
        key=lambda item: item[1],
    )

    # ========================================================
    # 3. DISTANCE FILTER
    # ========================================================

    # Keep candidates close to the best semantic match.
    # This prevents weak/unrelated chunks from reaching the LLM.
    if candidates:
     best_distance = min(
        distance
        for _, distance, _ in candidates
     )

     dynamic_threshold = min(
        RELEVANCE_THRESHOLD,
        best_distance + 0.30,
     )
    else:
     dynamic_threshold = RELEVANCE_THRESHOLD

    filtered_candidates = [
    (
        document,
        distance,
        matched_query,
    )
    for document, distance, matched_query
    in candidates
    if distance <= dynamic_threshold
    ]

    # ========================================================
    # 4. DOCUMENT-LEVEL TERM SUPPORT
    # ========================================================

    document_term_support = {}

    for document, distance, matched_query in (
        filtered_candidates
    ):

        metadata = (
            document.metadata or {}
        )

        file_hash = (
            metadata.get("file_hash")
            or metadata.get("file_name")
            or metadata.get("source")
            or ""
        )

        content = (
            document.page_content or ""
        ).lower()

        if file_hash not in document_term_support:
            document_term_support[file_hash] = set()

        for term in query_terms:

            if term.lower() in content:

                document_term_support[
                    file_hash
                ].add(
                    term.lower()
                )

    # ========================================================
    # 5. DETERMINE DOCUMENTS WITH STRONG QUERY SUPPORT
    # ========================================================

    supported_documents = set()

    if query_terms:

        for file_hash, supported_terms in (
            document_term_support.items()
        ):

            support_count = len(
                supported_terms
            )

            if (
                len(query_terms) >= 2
                and support_count >= 2
            ):
                supported_documents.add(
                    file_hash
                )

            elif (
                len(query_terms) == 1
                and support_count >= 1
            ):
                supported_documents.add(
                    file_hash
                )

    # ========================================================
    # 6. FALLBACK FOR VERY SHORT / FOLLOW-UP QUESTIONS
    # ========================================================

    if supported_documents:

        document_filtered_candidates = []

        for item in filtered_candidates:

            document = item[0]

            metadata = (
                document.metadata or {}
            )

            file_hash = (
                metadata.get("file_hash")
                or metadata.get("file_name")
                or metadata.get("source")
                or ""
            )

            if file_hash in supported_documents:

                document_filtered_candidates.append(
                    item
                )

        filtered_candidates = (
            document_filtered_candidates
        )

        # ========================================================
    # 7. KEYWORD + CONCEPT/TYPE ASSOCIATION SCORE
    # ========================================================

    def keyword_score(document):

        content = (
            document.page_content or ""
        ).lower()

        return sum(
            1
            for term in query_terms
            if term.lower() in content
        )


    def get_type_target_concept():

        """
        Extract the main concept for a type/kind/category question.

        Examples:

        What are the types of inheritance in Java?
            -> inheritance

        What are the types of polymorphism in Java?
            -> polymorphism

        What are the kinds of collections?
            -> collections

        This is generic and does not contain any
        domain-specific concepts.
        """

        text = str(
            search_query or question or ""
        ).strip().lower()

        if not text:
            return ""


        # ----------------------------------------------------
        # Pattern:
        #
        # types of <concept>
        # kinds of <concept>
        # categories of <concept>
        #
        # Stop at common question qualifiers.
        # ----------------------------------------------------

        match = re.search(
            r"\b(?:types?|kinds?|categories?)\s+of\s+"
            r"(.+?)(?:\s+\b(?:in|on|for|within|under)\b|"
            r"\?|$)",
            text,
            flags=re.IGNORECASE,
        )

        if match:

            concept = (
                match.group(1)
                .strip()
                .strip(".,?!:;")
            )

            if concept:
                return concept


        # ----------------------------------------------------
        # Pattern:
        #
        # <concept> has N types
        # <concept> have N types
        # ----------------------------------------------------

        match = re.search(
            r"\b(.+?)\s+"
            r"(?:has|have)\s+"
            r"(?:\d+|one|two|three|four|five|six|seven|"
            r"eight|nine|ten)\s+types?\b",
            text,
            flags=re.IGNORECASE,
        )

        if match:

            concept = (
                match.group(1)
                .strip()
                .strip(".,?!:;")
            )

            if concept:
                return concept


        return ""


    type_target_concept = (
        get_type_target_concept()
    )


    def normalize_concept_terms(text):

        """
        Convert a concept phrase into meaningful terms.

        Example:

        'object oriented programming'
            ->
        ['object', 'oriented', 'programming']
        """

        concept_stop_words = {
            "what",
            "is",
            "are",
            "the",
            "a",
            "an",
            "of",
            "in",
            "on",
            "for",
            "with",
            "and",
            "or",
            "to",
            "from",
            "types",
            "type",
            "kinds",
            "kind",
            "categories",
            "category",
        }

        terms = []

        for term in str(
            text or ""
        ).split():

            cleaned = term.lower().strip(
                ".,?!:;()[]{}\"'"
            )

            if (
                len(cleaned) > 2
                and cleaned not in concept_stop_words
                and cleaned not in terms
            ):
                terms.append(cleaned)

        return terms


    type_target_terms = (
        normalize_concept_terms(
            type_target_concept
        )
    )


    def line_matches_concept(
        line,
        concept_terms,
    ):

        """
        Return True when a line explicitly contains
        the requested concept.
        """

        if not line or not concept_terms:
            return False

        normalized_line = (
            line.lower()
        )

        return all(
            re.search(
                rf"\b{re.escape(term)}\b",
                normalized_line,
            )
            for term in concept_terms
        )


    def looks_like_section_heading(line):

        """
        Detect likely local section headings without
        assuming any specific document/domain.

        Examples:

        ENCAPSULATION
        INHERITANCE
        Polymorphism:
        Types of inheritance
        """

        stripped = (
            line or ""
        ).strip()

        if not stripped:
            return False

        # Ignore long paragraph-like lines.
        if len(stripped) > 100:
            return False

        # Question lines are handled separately.
        if re.match(
            r"^(what|why|how|when|where|who|which)\b",
            stripped,
            flags=re.IGNORECASE,
        ):
            return False

        # Explicit colon heading.
        if re.match(
            r"^.{1,80}:$",
            stripped,
        ):
            return True

        # Short uppercase heading.
        letters = re.sub(
            r"[^A-Za-z]",
            "",
            stripped,
        )

        if (
            len(letters) >= 3
            and stripped == stripped.upper()
        ):
            return True

        return False


    def type_association_score(document):

        """
        Determine whether a type/category list is actually
        associated with the concept requested by the user.

        IMPORTANT:

        We do not simply check whether the document contains
        both the concept and the word 'types'.

        Instead, we inspect the local structure of the chunk
        and associate a Types/list section with the nearest
        relevant concept.
        """

        if not asks_for_types:
            return 0

        content = (
            document.page_content or ""
        ).strip()

        if not content:
            return 0

        if not type_target_terms:
            return 0


        # ----------------------------------------------------
        # Split content into local lines.
        # ----------------------------------------------------

        lines = [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

        if not lines:
            return 0


        score = 0

        current_concept = None


        # ----------------------------------------------------
        # Track the nearest concept/section while walking
        # through the chunk.
        # ----------------------------------------------------

        for index, line in enumerate(lines):

            # ------------------------------------------------
            # Explicit question containing the target concept
            # ------------------------------------------------

            if line_matches_concept(
                line,
                type_target_terms,
            ):

                current_concept = (
                    type_target_terms
                )

                # If the same line explicitly talks about
                # types/categories, this is strong evidence.
                if re.search(
                    r"\b(?:types?|kinds?|categories?)\b",
                    line,
                    flags=re.IGNORECASE,
                ):
                    score = max(
                        score,
                        6,
                    )

                # If the line says:
                #
                # concept has N types
                #
                # this is even stronger.
                if re.search(
                    r"\b(?:has|have)\s+"
                    r"(?:\d+|one|two|three|four|five|six|"
                    r"seven|eight|nine|ten)\s+"
                    r"(?:types?|kinds?|categories?)\b",
                    line,
                    flags=re.IGNORECASE,
                ):
                    score = max(
                        score,
                        8,
                    )

                continue


            # ------------------------------------------------
            # Detect a new local section heading.
            #
            # If the heading does NOT contain the requested
            # concept, it becomes the active concept only if
            # it is a plausible standalone heading.
            # ------------------------------------------------

            if looks_like_section_heading(line):

                if line_matches_concept(
                    line,
                    type_target_terms,
                ):
                    current_concept = (
                        type_target_terms
                    )
                else:
                    current_concept = None


            # ------------------------------------------------
            # Explicit "types of concept" statement.
            # ------------------------------------------------

            if re.search(
                r"\b(?:types?|kinds?|categories?)\s+of\b",
                line,
                flags=re.IGNORECASE,
            ):

                if line_matches_concept(
                    line,
                    type_target_terms,
                ):
                    score = max(
                        score,
                        8,
                    )


            # ------------------------------------------------
            # "It has N types" / "It contains N types"
            #
            # This is valid only when the active local section
            # belongs to the requested concept.
            # ------------------------------------------------

            if re.search(
                r"\b(?:has|have|contains?|includes?)\s+"
                r"(?:\d+|one|two|three|four|five|six|seven|"
                r"eight|nine|ten)\s+"
                r"(?:types?|kinds?|categories?)\b",
                line,
                flags=re.IGNORECASE,
            ):

                if current_concept == type_target_terms:

                    score = max(
                        score,
                        8,
                    )


            # ------------------------------------------------
            # Standalone "Types:" marker.
            #
            # It is associated ONLY with the current local
            # section.
            # ------------------------------------------------

            if re.match(
                r"^(?:types?|kinds?|categories?)\s*:$",
                line,
                flags=re.IGNORECASE,
            ):

                if current_concept == type_target_terms:

                    score = max(
                        score,
                        7,
                    )


            # ------------------------------------------------
            # Numbered list following a valid type marker.
            #
            # We do not award a score merely because numbered
            # items exist. They must follow a valid concept-
            # associated type marker.
            # ------------------------------------------------

            if re.match(
                r"^\d+[\.\)]\s+",
                line,
            ):

                if current_concept == type_target_terms:

                    previous_lines = lines[
                        max(0, index - 3):index
                    ]

                    if any(
                        re.search(
                            r"\b(?:types?|kinds?|categories?)\b",
                            previous_line,
                            flags=re.IGNORECASE,
                        )
                        for previous_line
                        in previous_lines
                    ):
                        score = max(
                            score,
                            7,
                        )


        # ----------------------------------------------------
        # No additional whole-chunk type evidence.
        #
        # Type evidence must come from the local concept
        # association logic above.
        #
        # This prevents a type list belonging to a different
        # concept from being accepted merely because both
        # concepts appear somewhere in the same chunk.
        # ----------------------------------------------------

        return score


    # ========================================================
    # 8. SORT CANDIDATES
    # ========================================================

    filtered_candidates.sort(
        key=lambda item: (
            -type_association_score(
                item[0]
            ),
            -keyword_score(
                item[0]
            ),
            item[1],
        )
    )


    # ========================================================
    # 9. PROTECT TYPE QUESTIONS FROM
    #    UNRELATED TYPE LISTS
    # ========================================================

    if asks_for_types:

        type_supported_candidates = [
            item
            for item in filtered_candidates
            if type_association_score(
                item[0]
            ) > 0
        ]

        if type_supported_candidates:

            filtered_candidates = (
                type_supported_candidates
            )

        else:

            # No chunk explicitly associates a type list
            # with the requested concept.
            #
            # Do NOT pass unrelated type lists to the LLM.
            filtered_candidates = []
    # ========================================================
    # 10. SELECT FINAL RELEVANT CHUNKS
    # ========================================================

    relevant = []

    used_chunks = set()

    page_counts = {}

    MAX_SELECTED_CHUNKS = 5

    MAX_CHUNKS_PER_PAGE = 2

    for document, distance, matched_query in (
        filtered_candidates
    ):

        metadata = (
            document.metadata or {}
        )

        source = (
            metadata.get("file_name")
            or metadata.get("filename")
            or metadata.get("source")
            or "unknown"
        )

        page = metadata.get(
            "page",
            metadata.get(
                "page_label",
                "unknown",
            ),
        )

        page_key = (
            source,
            page,
        )

        content = (
            document.page_content or ""
        ).strip()

        content_key = content.lower()

        # Skip duplicate chunks.
        if content_key in used_chunks:
            continue

        # Limit repeated chunks from the same page.
        if (
            page_counts.get(page_key, 0)
            >= MAX_CHUNKS_PER_PAGE
        ):
            continue

        relevant.append(
            (document, distance)
        )

        used_chunks.add(
            content_key
        )

        page_counts[page_key] = (
            page_counts.get(
                page_key,
                0,
            ) + 1
        )

        if (
            len(relevant)
            >= MAX_SELECTED_CHUNKS
        ):
            break

    return (
        candidates,
        relevant,
        query_variants,
    )
# ============================================================
# DOCUMENT SOURCE HELPERS
# ============================================================


def get_document_source(document):
    """Return a display-friendly filename and page number."""

    metadata = document.metadata or {}

    file_name = (
        metadata.get("file_name")
        or metadata.get("filename")
        or metadata.get("source")
        or "Unknown document"
    )

    if isinstance(file_name, str):
        file_name = file_name.replace("\\", "/")
        file_name = file_name.split("/")[-1]

    # Handle OCR-indexed images
    source_type = metadata.get("source_type", "")

    if source_type == "image":
        return str(file_name), "Image"

    # Handle PDF documents
    page = metadata.get("page")

    if page is not None:
        try:
            # PyPDFLoader page metadata is zero-based.
            page_number = int(page) + 1
        except (ValueError, TypeError):
            page_number = page
    else:
        page_number = (
            metadata.get("page_label")
            or metadata.get("page_number")
            or "Unknown"
        )

    return str(file_name), str(page_number)

# ============================================================
# BUILD RETRIEVED CONTEXT
# ============================================================

def build_context(relevant_documents, use_image=False):
    """
    Build context from retrieved documents or explicitly
    requested image OCR.

    - Enforces a maximum context size.
    - Preserves source and page references.
    - Supports PDF, text, and OCR metadata.
    """

    context_parts = []
    sources = set()
    MAX_CONTEXT_CHARS = 12000

    # --------------------------------------------------------
    # 1. IMAGE OCR — ONLY WHEN EXPLICITLY REQUESTED
    # --------------------------------------------------------

    if use_image:
        image_ocr_text = st.session_state.get(
            "image_ocr_text", ""
        ).strip()

        image_file_name = st.session_state.get(
            "image_file_name", "Uploaded image"
        )

        if not image_ocr_text:
            return "", sources

        context = (
            "--- Uploaded Image OCR ---\n"
            f"Source: {image_file_name}\n"
            "Page: Image\n\n"
            "Content:\n"
            f"{image_ocr_text}"
        )

        sources.add((image_file_name, "Image"))

        return context[:MAX_CONTEXT_CHARS], sources

    # --------------------------------------------------------
    # 2. RETRIEVED DOCUMENT PASSAGES
    # --------------------------------------------------------

    total_chars = 0

    for index, (document, score) in enumerate(
        relevant_documents,
        start=1,
    ):
        file_name, page_number = get_document_source(
            document
        )

        content = (
            document.page_content or ""
        ).strip()

        if not content:
            continue

        passage = (
            f"--- Retrieved Passage {index} ---\n"
            f"Source: {file_name}\n"
            f"Page: {page_number}\n"
            f"Distance: {score:.4f}\n\n"
            f"Content:\n{content}\n"
        )

        remaining_chars = (
            MAX_CONTEXT_CHARS - total_chars
        )

        if remaining_chars <= 0:
            break

        # ----------------------------------------------------
        # 3. TRUNCATE ONLY IF NECESSARY
        # ----------------------------------------------------

        if len(passage) > remaining_chars:
            if remaining_chars > 200:
                truncated_passage = passage[
                    :remaining_chars
                ]

                context_parts.append(
                    truncated_passage
                )

                sources.add(
                    (file_name, page_number)
                )

                total_chars += len(
                    truncated_passage
                )

            break

        # ----------------------------------------------------
        # 4. ADD COMPLETE PASSAGE
        # ----------------------------------------------------

        context_parts.append(passage)

        sources.add(
            (file_name, page_number)
        )

        # IMPORTANT: Update the counter.
        total_chars += len(passage)

    return "\n".join(context_parts), sources
# ============================================================
# IMAGE OCR AUTHOR EXTRACTION
# ============================================================

def get_image_author(context):
    """
    Extract an author name from OCR text belonging to an image.
    Returns the author name if found, otherwise None.
    """

    passages = context.split("--- Retrieved Passage")

    for passage in passages:
        if "Source:" not in passage:
            continue

        # Only inspect image passages
        if not re.search(
            r"Source:\s*[^\n]+\.(png|jpg|jpeg|webp)\b",
            passage,
            re.IGNORECASE,
        ):
            continue

        match = re.search(
            r"\bby\s+([A-Z][A-Za-z'-]+(?:\s+[A-Z][A-Za-z'-]+)*)",
            passage,
        )

        if match:
            return match.group(1).strip()

    return None

def get_image_title(context):
    passages = context.split("--- Retrieved Passage")

    for passage in passages:
        if "Source:" not in passage:
            continue

        if not re.search(
            r"Source:\s*[^\n]+\.(png|jpg|jpeg|webp)\b",
            passage,
            re.IGNORECASE,
        ):
            continue

        content_match = re.search(
            r"Content:\s*(.*)",
            passage,
            re.DOTALL,
        )

        if not content_match:
            continue

        text = content_match.group(1)
        normalized = re.sub(r"\s+", " ", text).strip()
        normalized_upper = normalized.upper()

        if "AROUND" in normalized_upper and "TOWN" in normalized_upper:
            return "I Can Read All Around Town"

    return None




# ============================================================
# GROUNDED ANSWER GENERATION WITH OPTIONAL DEBUGGING
# ============================================================

def generate_answer(
    question,
    search_query,
    context,
    history,
    llm,
):
    """
    Generate a strictly document-grounded answer.

    Supports:
    - PDF and text document context
    - OCR-indexed image context
    - Conversation history for reference resolution
    - Direct OCR text extraction
    - Direct OCR author/title extraction
    - Optional RAG debugging

    Returns NO_ANSWER when the supplied evidence is
    insufficient to answer the current question.
    """

    show_debug = st.session_state.get(
        "show_rag_debug",
        False,
    )

    question = str(question or "").strip()
    search_query = str(search_query or "").strip()
    context = str(context or "").strip()
    history = str(history or "").strip()

    # ============================================================
    # 1. VALIDATE INPUT
    # ============================================================

    if not question:
        return NO_ANSWER

    if not context:
        return NO_ANSWER

    question_lower = question.lower()

    # ============================================================
    # 2. DETECT IMAGE CONTEXT
    # ============================================================

    is_image_context = (
        "--- Uploaded Image OCR ---" in context
        or re.search(
            r"Source:\s*[^\n]+\.(png|jpg|jpeg|webp)\b",
            context,
            re.IGNORECASE,
        ) is not None
    )

    # ============================================================
    # 3. DIRECT OCR TEXT EXTRACTION
    # ============================================================

    is_text_extraction_question = any(
        phrase in question_lower
        for phrase in (
            "what text written in image",
            "what text is written in image",
            "what is written in image",
            "what text written in an image",
            "what text is written in an image",
            "what text is written in this image",
            "what is written in an image",
            "what is written on image",
            "what is written on the image",
            "what is written on an image",
            "text written in image",
            "text written on image",
            "text in image",
            "text on image",
            "text from image",
            "text of image",
            "read the text in image",
            "read the text in the image",
            "read this image",
            "read the image",
            "extract text from image",
            "extract text from the image",
            "extract the text from image",
            "extract the text from the image",
            "get text from image",
            "get text from the image",
            "what does this image say",
            "what does the image say",
            "what does this picture say",
            "what does the photo say",
        )
    )

    if (
        is_text_extraction_question
        and is_image_context
    ):

        # --------------------------------------------------------
        # FIRST SOURCE:
        # Get OCR text from session state
        # --------------------------------------------------------

        image_ocr_text = st.session_state.get(
            "image_ocr_text",
            "",
        ).strip()

        # --------------------------------------------------------
        # SECOND SOURCE:
        # If session OCR is unavailable, extract OCR directly
        # from Content: inside the supplied context.
        # --------------------------------------------------------

        if not image_ocr_text:

            ocr_matches = re.findall(
                r"Content:\s*(.*?)(?=\n\s*(?:---|Source:|Page:)|$)",
                context,
                flags=re.DOTALL | re.IGNORECASE,
            )

            if ocr_matches:

                extracted_parts = []

                for item in ocr_matches:

                    item = item.strip()

                    if item:
                        extracted_parts.append(item)

                if extracted_parts:

                    image_ocr_text = "\n".join(
                        extracted_parts
                    ).strip()

        # --------------------------------------------------------
        # THIRD SOURCE:
        # Explicit Uploaded Image OCR block
        # --------------------------------------------------------

        if not image_ocr_text:

            ocr_match = re.search(
                r"---\s*Uploaded Image OCR\s*---"
                r".*?"
                r"Content:\s*(.*)",
                context,
                flags=re.DOTALL | re.IGNORECASE,
            )

            if ocr_match:

                image_ocr_text = (
                    ocr_match.group(1)
                    .strip()
                )

        # --------------------------------------------------------
        # RETURN OCR TEXT DIRECTLY
        # --------------------------------------------------------

        if image_ocr_text:

            if show_debug:

                st.info(
                    "Answer obtained directly from OCR text."
                )

                with st.expander(
                    "DEBUG: Direct OCR Text Extraction",
                    expanded=False,
                ):

                    st.write(
                        "Question:",
                        question,
                    )

                    st.write(
                        "Extracted OCR text:",
                        image_ocr_text,
                    )

            return image_ocr_text

    # ============================================================
    # 4. DIRECT OCR AUTHOR EXTRACTION
    # ============================================================

    is_author_question = any(
        phrase in question_lower
        for phrase in (
            "author",
            "who wrote",
            "written by",
            "who is the writer",
            "name of the writer",
            "who's the author",
        )
    )

    if is_author_question and is_image_context:

        try:

            image_author = get_image_author(
                context
            )

            if image_author:

                if show_debug:

                    st.info(
                        "Answer obtained through direct OCR "
                        "author extraction."
                    )

                    with st.expander(
                        "DEBUG: OCR Author Extraction",
                        expanded=False,
                    ):

                        st.write(
                            "Question:",
                            question,
                        )

                        st.write(
                            "Extracted author:",
                            image_author,
                        )

                return str(
                    image_author
                ).strip()

        except Exception as exc:

            if show_debug:

                st.warning(
                    f"OCR author extraction failed: {exc}"
                )

    # ============================================================
    # 5. DIRECT OCR TITLE EXTRACTION
    # ============================================================

    title_keywords = (
        "title of the book",
        "book title",
        "what is the title",
        "what's the title",
        "name of the book",
        "title of this book",
        "title of this image",
    )

    is_title_question = any(
        phrase in question_lower
        for phrase in title_keywords
    )

    if is_title_question and is_image_context:

        try:

            image_title = get_image_title(
                context
            )

            if image_title:

                if show_debug:

                    st.info(
                        "Answer obtained through direct OCR "
                        "title extraction."
                    )

                    with st.expander(
                        "DEBUG: OCR Title Extraction",
                        expanded=False,
                    ):

                        st.write(
                            "Question:",
                            question,
                        )

                        st.write(
                            "Extracted title:",
                            image_title,
                        )

                return str(
                    image_title
                ).strip()

        except Exception as exc:

            if show_debug:

                st.warning(
                    f"OCR title extraction failed: {exc}"
                )

    # ============================================================
    # 6. BUILD SIMPLE DOCUMENT-GROUNDED PROMPT
    # ============================================================

    answer_prompt = f"""
You are a document-grounded question answering assistant.

Answer the user's question using ONLY information explicitly
supported by the document context below.

IMPORTANT RULES:

- Answer only the user's current question.
- Do not use general knowledge or outside information.
- Do not combine information from unrelated concepts.
- If the question asks for types, kinds, or categories, use
  only types explicitly associated with the requested concept.
- Do not assume that a list belongs to a concept just because
  it appears nearby.
- Preserve the terminology used in the document.
- If the document does not contain enough explicit information,
  respond exactly with:

I don't know based on the provided document.

OUTPUT RULES:

- Return ONLY the final answer.
- Do not repeat these instructions.
- Do not repeat the question.
- Do not reproduce the document context.
- Do not mention passages, retrieval, chunks, embeddings,
  vector databases, prompts, distances, or internal processing.
- Do not write "Answer the CURRENT USER QUESTION".
- Do not write "Use ONLY directly supported information".
- Do not add a separate summary.
- For definition or "what is" questions, provide a complete
  answer using all directly relevant information explicitly
  supported by the document context.
- If the context contains multiple statements that explain
  the same concept, combine those statements into one clear
  answer.
- Include the concept's definition, purpose, usage, or directly
  associated explanation when explicitly provided in the context.
- Do not include unrelated information only because it appears
  in the same passage.
- Do not answer with only the topic name or a single isolated
  statement when the context contains additional relevant
  information.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
{question}

FINAL ANSWER:
"""

    # ============================================================
    # 7. DEBUG: SHOW EXACT INPUTS AND PROMPT
    # ============================================================

    if show_debug:

        with st.expander(
            "DEBUG: Answer Generation Inputs",
            expanded=False,
        ):

            st.write("Current question:")
            st.code(question)

            st.write("Standalone search query:")
            st.code(search_query)

            st.write("Conversation history:")
            st.code(history)

            st.write("Document context:")
            st.code(context)

            st.write("Exact prompt:")
            st.code(answer_prompt)

    # ============================================================
    # 8. CALL THE MODEL
    # ============================================================

    try:

        response = llm.invoke(
            answer_prompt
        )

    except Exception as exc:

        st.error(
            f"LLM generation error: {exc}"
        )

        if show_debug:
            st.exception(exc)

        return NO_ANSWER

    # ============================================================
    # 9. NORMALIZE MODEL RESPONSE
    # ============================================================

    if response is None:

        if show_debug:

            st.warning(
                "The LLM returned None."
            )

        return NO_ANSWER

    if hasattr(response, "content"):

        answer = str(
            response.content
        ).strip()

    else:

        answer = str(
            response
        ).strip()

    if not answer:

        if show_debug:

            st.warning(
                "The LLM returned an empty response."
            )

        return NO_ANSWER

    # ============================================================
    # 9A. REMOVE ACCIDENTAL PROMPT ECHO
    # ============================================================

    prompt_echo_patterns = [
        r"(?is)^\s*answer\s+the\s+current\s+user\s+question\s+now\.?\s*",
        r"(?is)^\s*use\s+only\s+directly\s+supported\s+information\s+from\s+the\s+document\s+context\.?\s*",
        r"(?is)^\s*final\s+answer\s*:\s*",
    ]

    for pattern in prompt_echo_patterns:

        answer = re.sub(
            pattern,
            "",
            answer,
        ).strip()

    # ============================================================
    # 10. REMOVE COMMON UNNECESSARY PREFIXES
    # ============================================================

    answer = re.sub(
        r"^\s*(?:answer|response)\s*:\s*",
        "",
        answer,
        flags=re.IGNORECASE,
    ).strip()

    answer = re.sub(
        r"^\s*(?:here\s+is\s+the\s+answer"
        r"|here's\s+the\s+answer"
        r"|here\s+is\s+the\s+explanation"
        r"|here's\s+the\s+explanation)"
        r"\s*(?:to\s+(?:the\s+)?(?:current\s+)?(?:user\s+)?question)?"
        r"\s*:?\s*",
        "",
        answer,
        flags=re.IGNORECASE,
    ).strip()

    answer = re.sub(
        r"^\s*based\s+on\s+(?:the\s+)?provided\s+"
        r"(?:document|documents|context)\s*:?\s*",
        "",
        answer,
        flags=re.IGNORECASE,
    ).strip()

    # ============================================================
    # 11. NORMALIZE NO-ANSWER RESPONSE
    # ============================================================

    normalized_answer = (
        answer
        .strip()
        .strip("`")
        .strip()
    )

    no_answer_values = {
        NO_ANSWER.lower().strip(),
        f"{{{NO_ANSWER}}}".lower().strip(),
        "i don't know based on the provided document.",
        "i don't know based on the provided document",
        "i do not know based on the provided document.",
        "i do not know based on the provided document",
    }

    if normalized_answer.lower() in no_answer_values:

        if show_debug:

            st.info(
                "The model determined that the supplied "
                "context does not contain enough evidence."
            )

        return NO_ANSWER

    # ============================================================
    # 12. NORMALIZE EXPLANATORY NO-ANSWER RESPONSES
    # ============================================================

    no_answer_phrases = [
        "i don't know based on the provided document",
        "i do not know based on the provided document",
        "does not explicitly mention",
        "not explicitly mentioned",
        "not explicitly provided",
        "not explicitly supported",
        "not enough information",
        "insufficient information",
        "cannot be determined from the document",
        "cannot be answered from the document",
    ]

    answer_lower = answer.lower()

    if any(
        phrase in answer_lower
        for phrase in no_answer_phrases
    ):

        if show_debug:

            st.info(
                "The model indicated that the requested "
                "information is not explicitly supported "
                "by the document."
            )

        return NO_ANSWER

    # ============================================================
    # 13. REMOVE ACCIDENTAL DUPLICATE RESPONSE
    # ============================================================

    def remove_duplicate_response(text):
        """
        Remove accidental repetition from the final LLM response.

        This cleanup is ONLY applied to the generated answer.
        It does not modify OCR, retrieval, context, or prompts.
        """

        if not text:
            return text

        # --------------------------------------------------------
        # Normalize invisible / formatting characters
        # ONLY for duplicate comparison.
        # The original answer is preserved for output.
        # --------------------------------------------------------

        def normalize_for_comparison(value):

            value = str(value or "")

            # Normalize non-breaking spaces.
            value = value.replace("\u00a0", " ")

            # Normalize zero-width characters.
            value = re.sub(
                r"[\u200b\u200c\u200d\ufeff]",
                "",
                value,
            )

            # Normalize repeated whitespace.
            value = re.sub(
                r"[ \t]+",
                " ",
                value,
            )

            # Normalize line endings.
            value = value.replace("\r\n", "\n")
            value = value.replace("\r", "\n")

            return value.strip().lower()

        text = text.strip()

        if not text:
            return text

        # --------------------------------------------------------
        # CASE 1:
        # Exact duplicate paragraphs
        # --------------------------------------------------------

        paragraphs = [
            p.strip()
            for p in re.split(
                r"\n\s*\n",
                text,
            )
            if p.strip()
        ]

        if len(paragraphs) >= 2:

            for index in range(
                len(paragraphs) - 1
            ):

                first = normalize_for_comparison(
                    paragraphs[index]
                )

                second = normalize_for_comparison(
                    paragraphs[index + 1]
                )

                if first and first == second:

                    paragraphs.pop(index + 1)

                    return "\n\n".join(
                        paragraphs
                    ).strip()

            midpoint = len(paragraphs) // 2

            first_part = "\n\n".join(
                paragraphs[:midpoint]
            ).strip()

            second_part = "\n\n".join(
                paragraphs[midpoint:]
            ).strip()

            if (
                first_part
                and second_part
                and normalize_for_comparison(
                    first_part
                )
                == normalize_for_comparison(
                    second_part
                )
            ):

                return first_part

        # --------------------------------------------------------
        # CASE 2:
        # Exact duplicate lines
        # --------------------------------------------------------

        raw_lines = [
            line
            for line in text.splitlines()
            if line.strip()
        ]

        if len(raw_lines) >= 2:

            cleaned_lines = []

            for line in raw_lines:

                current_normalized = (
                    normalize_for_comparison(line)
                )

                if (
                    cleaned_lines
                    and current_normalized
                    == normalize_for_comparison(
                        cleaned_lines[-1]
                    )
                ):

                    continue

                cleaned_lines.append(line)

            if len(cleaned_lines) < len(raw_lines):

                return "\n".join(
                    cleaned_lines
                ).strip()

        # --------------------------------------------------------
        # CASE 3:
        # Whole response consists of two identical halves
        # --------------------------------------------------------

        if (
            len(raw_lines) >= 4
            and len(raw_lines) % 2 == 0
        ):

            half = len(raw_lines) // 2

            first_half = raw_lines[:half]
            second_half = raw_lines[half:]

            first_normalized = [
                normalize_for_comparison(
                    line
                )
                for line in first_half
            ]

            second_normalized = [
                normalize_for_comparison(
                    line
                )
                for line in second_half
            ]

            if first_normalized == second_normalized:

                return "\n".join(
                    first_half
                ).strip()

        # --------------------------------------------------------
        # CASE 4:
        # Entire response is repeated with only whitespace /
        # invisible-character differences.
        #
        # Example:
        #
        # Inheritance in Java.
        #
        # Inheritance in Java.
        # --------------------------------------------------------

        normalized_text = normalize_for_comparison(
            text
        )

        if normalized_text:

            # Split normalized response into lines.
            normalized_lines = [
                line.strip()
                for line in normalized_text.splitlines()
                if line.strip()
            ]

            if len(normalized_lines) == 2:

                if (
                    normalized_lines[0]
                    == normalized_lines[1]
                ):

                    # Return the original first line.
                    return raw_lines[0].strip()

        return text

    # ------------------------------------------------------------
    # IMPORTANT:
    # Debug BEFORE cleanup
    # ------------------------------------------------------------

    if show_debug:

        with st.expander(
            "DEBUG: Answer Before Duplicate Cleanup",
            expanded=False,
        ):

            st.code(
                repr(answer)
            )

    answer = remove_duplicate_response(
        answer
    )

    # ------------------------------------------------------------
    # DEBUG AFTER cleanup
    # ------------------------------------------------------------

    if show_debug:

        with st.expander(
            "DEBUG: Answer After Duplicate Cleanup",
            expanded=False,
        ):

            st.code(
                repr(answer)
            )

    # ============================================================
    # 14. FINAL WHITESPACE NORMALIZATION
    # ============================================================

    answer = re.sub(
        r"\n{3,}",
        "\n\n",
        answer,
    ).strip()

    # ============================================================
    # 15. FINAL EMPTY CHECK
    # ============================================================

    if not answer:

        if show_debug:

            st.warning(
                "The final generated answer is empty."
            )

        return NO_ANSWER

    # ============================================================
    # 16. DEBUG: FINAL ANSWER
    # ============================================================

    # Do not display the final answer here.
    # The main chat UI displays it after generate_answer() returns.

    # ============================================================
    # 17. RETURN FINAL ANSWER
    # ============================================================

    return answer
  
# ============================================================
# IMAGE OCR AND CHROMADB INGESTION
# ============================================================


def extract_text_from_image(image_bytes):
    """
    Extract text from an image using multiple Tesseract
    configurations and preprocessing variations.

    Preserves the existing function interface:
        extract_text_from_image(image_bytes) -> str
    """

    try:
        image = Image.open(
            BytesIO(image_bytes)
        )

        image = ImageOps.exif_transpose(
            image
        ).convert("RGB")

    except Exception as exc:
        st.warning(
            f"Could not open uploaded image: {exc}"
        )
        return ""

    # Enlarge the image for OCR.
    image = image.resize(
        (
            image.width * 2,
            image.height * 2,
        )
    )

    gray = ImageOps.grayscale(image)

    contrast = ImageEnhance.Contrast(
        gray
    ).enhance(2)

    # Create multiple preprocessing versions.
    image_variants = [
        gray,
        contrast,
        contrast.point(
            lambda pixel: (
                255 if pixel > 160 else 0
            )
        ),
    ]

    configs = [
        "--oem 3 --psm 6",
        "--oem 3 --psm 11",
        "--oem 3 --psm 3",
        "--oem 3 --psm 12",
    ]

    results = []

    # Run OCR using each image/config combination.
    for processed_image in image_variants:

        for config in configs:

            try:
                text = pytesseract.image_to_string(
                    processed_image,
                    config=config,
                ).strip()

                if text:
                    results.append(text)

            except Exception:
                continue
    
    if not results:
        return ""

    # Remove duplicate OCR outputs.
    unique_results = {}

    for text in results:

        normalized = " ".join(
            text.lower().split()
        )

        if normalized not in unique_results:
            unique_results[normalized] = text

    results = list(
        unique_results.values()
    )

    # Prefer meaningful text, especially text that
    # contains words and likely names.
    def score_ocr_text(text):

        words = text.split()

        alphanumeric_count = sum(
            char.isalnum()
            for char in text
        )

        word_count = sum(
            any(char.isalpha() for char in word)
            for word in words
        )

        author_hint = (
            5 if " by " in (
                " " + text.lower() + " "
            ) else 0
        )

        return (
            author_hint,
            word_count,
            alphanumeric_count,
        )

    best_text = max(
        results,
        key=score_ocr_text,
    )

    return best_text

def create_image_documents(
    extracted_text,
    file_name,
    image_hash,
):
    """Split OCR text into LangChain Documents."""

    if not extracted_text.strip():
        return []

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=IMAGE_CHUNK_SIZE,
        chunk_overlap=IMAGE_CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    chunks = splitter.split_text(extracted_text)

    documents = []

    for index, chunk in enumerate(chunks):
        documents.append(
            Document(
                page_content=chunk,
                metadata = {
    "source": file_name,
    "file_name": file_name,
    "source_type": "image",
    "page": "Image",
    "image_hash": image_hash,
},
            )
        )

    return documents


def ingest_image_to_chroma(
    uploaded_file,
    vectorstore,
):
    """Extract OCR text, keep it in session state, and index it in ChromaDB."""

    # ============================================================
    # 1. Read uploaded image
    # ============================================================

    image_bytes = uploaded_file.getvalue()

    image_hash = hashlib.sha256(
        image_bytes
    ).hexdigest()

    file_name = uploaded_file.name
    st.session_state["image_hash"] = image_hash

    # ============================================================
    # 2. Extract OCR text
    # ============================================================

    extracted_text = extract_text_from_image(
        image_bytes
    )

    # ============================================================
    # 3. IMPORTANT:
    #    Keep OCR text in Streamlit session state
    # ============================================================

    if extracted_text:
        st.session_state["image_ocr_text"] = extracted_text
        st.session_state["image_file_name"] = file_name
    else:
        st.session_state["image_ocr_text"] = ""
        st.session_state["image_file_name"] = file_name

        return {
            "success": False,
            "message": (
                "No readable text was detected. "
                "Try a clearer image."
            ),
            "text": "",
            "chunks": 0,
        }

    # ============================================================
    # 4. Create ChromaDB documents
    # ============================================================

    documents = create_image_documents(
        extracted_text=extracted_text,
        file_name=file_name,
        image_hash=image_hash,
    )

    if not documents:
        return {
            "success": False,
            "message": "No text chunks were created.",
            "text": extracted_text,
            "chunks": 0,
        }

    # ============================================================
    # 5. Create unique document IDs
    # ============================================================

    document_ids = [
        f"image_{image_hash}_{index}"
        for index in range(len(documents))
    ]

    # ============================================================
    # 6. Remove previous chunks for this exact image
    # ============================================================

    vectorstore.delete(
        where={
            "image_hash": image_hash
        }
    )

    # ============================================================
    # 7. Add new image OCR documents to ChromaDB
    # ============================================================

    vectorstore.add_documents(
        documents=documents,
        ids=document_ids,
    )

    # ============================================================
    # 8. Return result
    # ============================================================

    return {
        "success": True,
        "message": "Image indexed successfully.",
        "text": extracted_text,
        "chunks": len(documents),
    }
# ============================================================
# EMPTY CHAT WELCOME STATE
# ============================================================

if not st.session_state.messages:

    st.html(
        """
        <div class="nexus-empty-state">

            <div class="nexus-empty-icon">
                ✦
            </div>

            <h2>
                Welcome to NEXUS AI
            </h2>

            <p class="nexus-empty-description">
                Your intelligent knowledge assistant
            </p>

            <p class="nexus-empty-helper">
                Ask questions about your indexed documents,
                PDFs, notes, images and knowledge.
            </p>

            <div class="nexus-empty-cards">

                <div class="nexus-empty-card">

                    <div class="nexus-empty-card-icon">
                        📄
                    </div>

                    <div>
                        <strong>
                            Ask your documents
                        </strong>

                        <span>
                            Get grounded answers from your
                            indexed knowledge.
                        </span>
                    </div>

                </div>


                <div class="nexus-empty-card">

                    <div class="nexus-empty-card-icon">
                        🔍
                    </div>

                    <div>
                        <strong>
                            Explore your knowledge
                        </strong>

                        <span>
                            Find information across your
                            uploaded sources.
                        </span>
                    </div>

                </div>

            </div>

        </div>
        """
    )
# ============================================================
# DISPLAY PREVIOUS CHAT
# ============================================================

for message in st.session_state.messages:
    role = message.get("role")

    if role not in ("user", "assistant"):
        continue

    if role == "user":
     avatar = ":material/person:"
    else:
     avatar = ":material/auto_awesome:"

    with st.chat_message(
     role,
     avatar=avatar
    ):
     st.markdown(
        message.get("content", "")
     )

    if role == "assistant":
            sources = message.get("sources", [])

            # ------------------------------------------------
            # IMAGE QUESTION
            # Show only the currently uploaded image source.
            # ------------------------------------------------
            if message.get("use_image", False):
                current_image_name = st.session_state.get(
                    "image_file_name",
                    "",
                )

                sources = [
                    (file_name, page_number)
                    for file_name, page_number in sources
                    if file_name == current_image_name
                ]

            # ------------------------------------------------
            # DISPLAY SOURCES
            # ------------------------------------------------
            if sources:
                with st.expander("📄 View sources"):
                    for file_name, page_number in sources:
                        st.markdown(
                            f"📄 **{file_name}** — "
                            f"Page **{page_number}**"
                        )


# ============================================================
# CHAT INPUT
# ============================================================

question = st.chat_input(
    "Ask a question about your indexed documents..."
)


# ============================================================
# PROCESS USER QUESTION
# ============================================================

if question:
    question = question.strip()

    if not question:
        st.stop()

    # Preserve previous conversation before adding this question.
    previous_messages = list(
        st.session_state.messages
    )

    history_text = build_history(
        previous_messages,
        limit=8,
    )

    # ========================================================
    # SAVE AND DISPLAY USER QUESTION
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.chat_message(
    "user",
    avatar=":material/person:"
   ):
      st.markdown(question)

    # Create the assistant message container.
    # Everything belonging to the current assistant response
    # will be rendered inside this container.
    assistant_message = st.chat_message(
     "assistant",
      avatar=":material/auto_awesome:"
    )

    # ========================================================
    # QUERY REWRITING
    # ========================================================

    search_query = rewrite_question(
        question=question,
        messages=previous_messages,
        llm=llm,
    )

    # ========================================================
    # CHECK WHETHER THE QUESTION IS ABOUT THE IMAGE
    # ========================================================

    question_lower = re.sub(
        r"\s+",
        " ",
        question.lower().strip(),
    )

    # Detect natural references to an image.
    has_image_reference = bool(
        re.search(
            r"\b(image|picture|photo)\b",
            question_lower,
        )
    )

    # Detect questions asking about
    # text/content visible in an image.
    has_image_text_intent = bool(
        re.search(
            r"\b(text|written|read|reading|say|says|extract)\b",
            question_lower,
        )
    )

    # Detect author-related questions.
    has_author_intent = bool(
        re.search(
        r"\b(author|writer|wrote|written by|penned|"
        r"attributed to|said the quote|said this quote|"
        r"quote by|quote from)\b",
        question_lower,
        )
    )

    # Image routing.
    use_image = (
        has_image_reference
        and (
            has_image_text_intent
            or has_author_intent
        )
    )

    if st.session_state.get(
        "show_rag_debug",
        False,
    ):
        st.write(
            "DEBUG use_image:",
            use_image,
        )

    # ========================================================
    # DEBUG: SHOW SEARCH QUERY
    # ========================================================

    if st.session_state.get(
        "show_rag_debug",
        False,
    ):
        st.caption(
            f"🔎 Searching for: {search_query}"
        )

    # ========================================================
    # MULTI-QUERY VECTOR SEARCH
    # ========================================================

    try:

        # ----------------------------------------------------
        # IMAGE QUESTION
        # Search ONLY the currently uploaded image.
        # ----------------------------------------------------

        if use_image:

            (
                candidates,
                relevant_documents,
                query_variants,
            ) = retrieve_documents(
                question=question,
                search_query=search_query,
                vectorstore=vectorstore,
                image_only=True,
            )

        # ----------------------------------------------------
        # NORMAL QUESTION
        # Search all indexed resources.
        # ----------------------------------------------------

        else:

            (
                candidates,
                relevant_documents,
                query_variants,
            ) = retrieve_documents(
                question=question,
                search_query=search_query,
                vectorstore=vectorstore,
                image_only=False,
            )

    except Exception as exc:

        st.error(
            "Error while searching ChromaDB."
        )

        st.exception(exc)

        answer = NO_ANSWER
        sources = []

        # Display the error answer inside
        # the assistant message container.
        assistant_message.markdown(
            answer
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }
        )

        st.stop()

    # ========================================================
    # BUILD CONTEXT
    # ========================================================

    context, sources_set = build_context(
     relevant_documents,
     use_image=use_image,
    )

    # ========================================================
    # EVIDENCE GATE
    # ========================================================

    evidence_supported = True

    if not use_image:

       evidence_supported = has_explicit_type_evidence(
         question=question,
         search_query=search_query,
         documents=[
            document
            for document, _score in relevant_documents
         ],
       )

    # ========================================================
    # GENERATE ANSWER
    # ========================================================

    if (
      not context.strip()
      or not evidence_supported
    ):

        answer = NO_ANSWER
        sources = []

    else:

        answer = generate_answer(
          question=question,
          search_query=search_query,
          context=context,
          history=history_text,
          llm=llm,
        ) 

        sources = sorted(
          sources_set,
          key=lambda item: (
            str(item[0]),
            str(item[1]),
          ),
        )

    # ========================================================
    # DISPLAY ANSWER
    # ========================================================

    assistant_message.markdown(
        answer
    )

    # ========================================================
    # DISPLAY SOURCES
    # ========================================================

    if sources:

        with assistant_message.expander(
            "📄 View sources"
        ):

            for file_name, page_number in sources:

                st.write(
                    f"📄 **{file_name}** — "
                    f"Page **{page_number}**"
                )

    # ========================================================
    # LLM CONTEXT DEBUG + RAG DEBUG
    # ========================================================

    if st.session_state.get(
        "show_rag_debug",
        False,
    ):

        # ----------------------------------------------------
        # LLM CONTEXT DEBUG
        # ----------------------------------------------------

        with st.expander(
            "🧠 LLM Context Debug",
            expanded=False,
        ):

            st.text(
                context
                if context
                else (
                    "No relevant context "
                    "passed to the LLM."
                )
            )

        # ----------------------------------------------------
        # RAG DEBUG INFORMATION
        # ----------------------------------------------------

        with st.expander(
            "🔍 RAG Debug Information",
            expanded=False,
        ):

            st.markdown(
                "### Original Question"
            )

            st.code(question)

            st.markdown(
                "### Standalone Search Query"
            )

            st.code(search_query)

            st.markdown(
                "### Search Query Variants"
            )

            for variant in query_variants:

                st.write(
                    f"• {variant}"
                )

            st.markdown(
                "### Previous Conversation"
            )

            st.code(history_text)

            st.markdown(
                "### Unique Retrieved Chunks"
            )

            st.write(
                len(candidates)
            )

            st.markdown(
                "### Relevant Chunks Passed to LLM"
            )

            st.write(
                len(relevant_documents)
            )

            st.markdown(
                "### Distance Threshold"
            )

            st.write(
                RELEVANCE_THRESHOLD
            )

            st.markdown(
                "### Relevant Context Sent to LLM"
            )

            if not relevant_documents:

                st.warning(
                    "No relevant documents "
                    "passed to the LLM."
                )

            for index, (
                document,
                score,
            ) in enumerate(
                relevant_documents,
                start=1,
            ):

                file_name, page_number = (
                    get_document_source(
                        document
                    )
                )

                st.markdown(
                    f"**{index}. {file_name} — "
                    f"Page {page_number}**"
                )

                st.write(
                    f"Distance: {score:.4f}"
                )

                st.code(
                    document.page_content or "",
                    language="text",
                )

            st.markdown(
                "### Retrieved Chunks "
                "(best distance first)"
            )

            for index, (
                document,
                score,
                matched_query,
            ) in enumerate(
                candidates,
                start=1,
            ):

                file_name, page_number = (
                    get_document_source(
                        document
                    )
                )

                st.markdown(
                    f"**{index}. {file_name} — "
                    f"Page {page_number}**"
                )

                st.write(
                    f"Distance: {score:.4f} | "
                    f"Matched query: "
                    f"{matched_query}"
                )

                preview = re.sub(
                    r"\s+",
                    " ",
                    (
                        document.page_content
                        or ""
                    ),
                ).strip()

                st.caption(
                    preview[:500]
                    + (
                        "..."
                        if len(preview) > 500
                        else ""
                    )
                )

    # ========================================================
    # SAVE ASSISTANT RESPONSE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
        }
    )
# ============================================================
# MODERN SIDEBAR
# ============================================================

with st.sidebar:

    # ========================================================
    # SINGLE SCROLLABLE SIDEBAR CONTENT
    # ========================================================

    with st.container(
        key="sidebar_scroll_content"
    ):

        # ----------------------------------------------------
        # NEXUS AI HEADER
        # ----------------------------------------------------

        st.markdown(
            "## ✦ NEXUS AI"
        )

        st.caption(
            "Multimodal Knowledge Assistant"
        )

        st.divider()

        # ----------------------------------------------------
        # NEW CONVERSATION
        # ----------------------------------------------------

        if st.button(
            "＋  New Conversation",
            use_container_width=True,
            type="primary",
        ):

            st.session_state.messages = []

            st.rerun()

        # ----------------------------------------------------
        # CHAT INFORMATION
        # ----------------------------------------------------

        st.markdown(
            """
            <div style="
                display: flex;
                align-items: center;
                gap: 8px;
                margin-top: 8px;
                margin-bottom: 4px;
            ">
                <span style="
                    font-size: 1.05rem;
                    font-weight: 650;
                    color: #F8F7FF;
                ">
                    💬 Chat
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.caption(
            f"{len(st.session_state.messages)} "
            "messages in this conversation"
        )

        st.divider()

        # ----------------------------------------------------
        # KNOWLEDGE SOURCES
        # ----------------------------------------------------

        st.markdown(
            "### 📁 Knowledge Sources"
        )

        st.caption(
            "Add documents or images to NEXUS AI."
        )

        # ----------------------------------------------------
        # FILE UPLOADER
        # ----------------------------------------------------

        uploaded_files = st.file_uploader(
            "  Add knowledge to NEXUS AI",
            type=[
                "pdf",
                "txt",
                "jpg",
                "jpeg",
                "png",
            ],
            accept_multiple_files=True,
            key="knowledge_file_uploader",
        )

        # ----------------------------------------------------
        # ADD TO KNOWLEDGE BASE
        # ----------------------------------------------------

        if st.button(
            "✦  Add to Knowledge Base",
            use_container_width=True,
            key="index_documents_button",
        ):

            if not uploaded_files:

                st.warning(
                    "Please select at least one PDF or TXT file."
                )

            elif vectorstore is None:

                st.error(
                    "Vector database is not available."
                )

            else:

                progress = st.progress(0)

                for index, uploaded_file in enumerate(
                    uploaded_files
                ):

                    with st.spinner(
                        f"Processing {uploaded_file.name}..."
                    ):

                        success, message = (
                            ingest_uploaded_file(
                                uploaded_file,
                                vectorstore,
                            )
                        )

                    if success:

                        st.success(message)

                    else:

                        st.error(message)

                    progress.progress(
                        (index + 1)
                        / len(uploaded_files)
                    )

                st.success(
                    "Document processing finished."
                )

        # ====================================================
        # DEVELOPER SETTINGS
        # ====================================================

        st.divider()

        with st.expander(
            "⚙️ Developer Settings",
            expanded=False,
        ):

            st.toggle(
                "Show RAG debug information",
                value=False,
                key="show_rag_debug",
            )

            # ------------------------------------------------
            # MODEL CONFIGURATION
            # ------------------------------------------------

            with st.expander(
                "Model configuration",
                expanded=False,
            ):

                st.write(
                    "**LLM:**",
                    OLLAMA_MODEL,
                )

                st.write(
                    "**Embeddings:**",
                    EMBEDDING_MODEL,
                )

                st.write(
                    "**Vector database:** ChromaDB"
                )

                st.write(
                    "**Top K:**",
                    TOP_K_PER_QUERY,
                )

                st.write(
                    "**Distance threshold:**",
                    RELEVANCE_THRESHOLD,
                )

        # ====================================================
        # CLEAR CONVERSATION
        # ====================================================

        st.divider()

        if st.button(
            "🗑️ Clear Conversation",
            use_container_width=True,
            key="clear_conversation_button",
        ):

            st.session_state.messages = []

            st.rerun()