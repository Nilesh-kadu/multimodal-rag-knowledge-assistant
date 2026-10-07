"""
NEXUS AI - Global Knowledge Base

This module manages the global conversational knowledge base.

IMPORTANT:
- Global knowledge uses a SEPARATE Chroma collection.
- It does NOT modify the existing user/document collection.
- Existing RAG retrieval functions remain untouched.
- The global PDF is indexed only once.
"""

from pathlib import Path
import hashlib

from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

GLOBAL_DATA_DIR = PROJECT_ROOT / "data" / "global"

GLOBAL_PDF = (
    GLOBAL_DATA_DIR
    / "NEXUS_AI_1000_Conversational_Questions.pdf"
)

VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"


# ============================================================
# CONFIGURATION
# ============================================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

GLOBAL_COLLECTION_NAME = "nexus_global_knowledge"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


# ============================================================
# FILE HASH
# ============================================================

def get_file_hash(file_path: Path) -> str:
    """
    Generate SHA256 hash for the global PDF.
    Used to prevent duplicate indexing.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


# ============================================================
# LOAD GLOBAL PDF
# ============================================================

def extract_global_pdf_documents():
    """
    Extract text from the global conversational PDF.

    Returns:
        list[Document]
    """

    if not GLOBAL_PDF.exists():
        raise FileNotFoundError(
            f"Global knowledge PDF not found: {GLOBAL_PDF}"
        )

    reader = PdfReader(str(GLOBAL_PDF))

    documents = []

    file_hash = get_file_hash(GLOBAL_PDF)

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text() or ""

        text = text.strip()

        if not text:
            continue

        document = Document(
            page_content=text,
            metadata={
                "source": GLOBAL_PDF.name,
                "page": page_number,
                "file_hash": file_hash,

                # Important scope information
                "knowledge_scope": "global",

                # This PDF is for conversational intent,
                # not factual document answers.
                "knowledge_type": "conversation",

                "source_type": "global_conversation",
            },
        )

        documents.append(document)

    return documents


# ============================================================
# SPLIT GLOBAL DOCUMENTS
# ============================================================

def split_global_documents(documents):
    """
    Split global PDF pages into chunks using the same
    chunking strategy as the existing RAG application.
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            " ",
            "",
        ],
    )

    chunks = splitter.split_documents(documents)

    for index, chunk in enumerate(chunks):

        chunk.metadata["chunk_index"] = index
        chunk.metadata["knowledge_scope"] = "global"
        chunk.metadata["knowledge_type"] = "conversation"
        chunk.metadata["source_type"] = "global_conversation"

    return chunks


# ============================================================
# CREATE GLOBAL VECTORSTORE
# ============================================================

def get_global_vectorstore():
    """
    Create/load a completely separate Chroma collection
    for global conversational knowledge.
    """

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

    global_vectorstore = Chroma(
        collection_name=GLOBAL_COLLECTION_NAME,
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings,
    )

    return global_vectorstore


# ============================================================
# INITIALIZE GLOBAL KNOWLEDGE
# ============================================================

def initialize_global_knowledge():
    """
    Initialize the global conversational knowledge base.

    The PDF is indexed only when it has not already been
    indexed into the global collection.

    Returns:
        tuple:
            (success: bool, message: str)
    """

    try:

        # ----------------------------------------------------
        # Check PDF
        # ----------------------------------------------------

        if not GLOBAL_PDF.exists():

            return (
                False,
                f"Global knowledge PDF not found: {GLOBAL_PDF}"
            )


        # ----------------------------------------------------
        # Create separate global vectorstore
        # ----------------------------------------------------

        vectorstore = get_global_vectorstore()


        # ----------------------------------------------------
        # Check whether this PDF is already indexed
        # ----------------------------------------------------

        file_hash = get_file_hash(GLOBAL_PDF)

        existing = vectorstore.get(
            where={
                "file_hash": file_hash
            },
            include=[],
        )


        if existing.get("ids"):

            return (
                True,
                "Global conversational knowledge is already indexed."
            )


        # ----------------------------------------------------
        # Extract PDF
        # ----------------------------------------------------

        documents = extract_global_pdf_documents()

        if not documents:

            return (
                False,
                "No readable text was found in the global PDF."
            )


        # ----------------------------------------------------
        # Split documents
        # ----------------------------------------------------

        chunks = split_global_documents(documents)

        if not chunks:

            return (
                False,
                "No chunks were created from the global PDF."
            )


        # ----------------------------------------------------
        # Generate unique IDs
        # ----------------------------------------------------

        ids = []

        for index, _chunk in enumerate(chunks):

            chunk_id = (
                f"global_{file_hash}_{index}"
            )

            ids.append(chunk_id)


        # ----------------------------------------------------
        # Add to GLOBAL collection
        # ----------------------------------------------------

        vectorstore.add_documents(
            documents=chunks,
            ids=ids,
        )


        return (
            True,
            f"Global knowledge initialized successfully. "
            f"Added {len(chunks)} chunks."
        )


    except Exception as exc:

        return (
            False,
            f"Global knowledge initialization failed: {exc}"
        )