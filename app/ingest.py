
from pathlib import Path
import hashlib
import sys

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# ============================================================
# CONFIGURATION
# ============================================================

# ============================================================
# PROJECT PATHS
# ============================================================

# Project root: Multimodal-RAG
BASE_DIR = Path(__file__).resolve().parent.parent

# Correct folders in project root
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_DIR = BASE_DIR / "vector_db"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 100

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ============================================================
# CREATE REQUIRED DIRECTORIES
# ============================================================

DATA_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# FIND PDF FILES
# ============================================================

pdf_files = sorted(DATA_DIR.glob("*.pdf"))

if not pdf_files:
    print("\nNo PDF files found in the data folder.")
    print(f"Please add PDF files to: {DATA_DIR}")
    sys.exit(0)

print("\n====================================")
print("PDF INGESTION STARTED")
print("====================================")

print(f"\nFound {len(pdf_files)} PDF file(s):")

for pdf_path in pdf_files:
    print(f"  - {pdf_path.name}")


# ============================================================
# LOAD PDF DOCUMENTS
# ============================================================

all_documents = []

for pdf_path in pdf_files:

    print(f"\nLoading: {pdf_path.name}")

    try:
        loader = PyPDFLoader(str(pdf_path))
        documents = loader.load()

        if not documents:
            print(f"Warning: No pages extracted from {pdf_path.name}")
            continue

        print(f"Pages loaded: {len(documents)}")

        for document in documents:

            # Preserve the original PyPDFLoader metadata.
            # PyPDFLoader page numbers are generally zero-based.

            document.metadata["file_name"] = pdf_path.name
            document.metadata["document_type"] = "PDF"

        all_documents.extend(documents)

    except Exception as error:
        print(f"Error loading {pdf_path.name}: {error}")


if not all_documents:
    print("\nNo PDF pages were successfully loaded.")
    sys.exit(1)

print(f"\nTotal pages loaded: {len(all_documents)}")


# ============================================================
# SPLIT DOCUMENTS INTO CHUNKS
# ============================================================

print("\nSplitting documents into chunks...")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    length_function=len,
    add_start_index=True,
)

chunks = text_splitter.split_documents(all_documents)

# Remove empty chunks.
chunks = [
    document
    for document in chunks
    if document.page_content.strip()
]

if not chunks:
    print("\nNo non-empty chunks were created.")
    sys.exit(1)

print(f"Total chunks created: {len(chunks)}")


# ============================================================
# GENERATE UNIQUE CHUNK IDS
# ============================================================

print("\nGenerating chunk IDs...")


def generate_chunk_id(document):
    """
    Generate a deterministic ID using the source filename,
    page number, chunk start index, and chunk content.
    """

    file_name = document.metadata.get(
        "file_name",
        "unknown",
    )

    page = document.metadata.get(
        "page",
        "unknown",
    )

    start_index = document.metadata.get(
        "start_index",
        "unknown",
    )

    content = document.page_content.strip()

    unique_text = (
        f"{file_name}|"
        f"{page}|"
        f"{start_index}|"
        f"{content}"
    )

    return hashlib.sha256(
        unique_text.encode("utf-8")
    ).hexdigest()


# Generate IDs for every chunk.
chunk_ids = [
    generate_chunk_id(document)
    for document in chunks
]


# ============================================================
# REMOVE DUPLICATE IDS WITHIN THIS INGESTION RUN
# ============================================================

unique_chunks = []
unique_ids = []
seen_ids = set()

for document, chunk_id in zip(chunks, chunk_ids):

    if chunk_id not in seen_ids:
        unique_chunks.append(document)
        unique_ids.append(chunk_id)
        seen_ids.add(chunk_id)

    else:
        print(f"Duplicate chunk skipped: {chunk_id[:12]}")

chunks = unique_chunks
chunk_ids = unique_ids

print(f"Unique chunks to process: {len(chunks)}")


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("\nLoading embedding model...")

try:
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )

except Exception as error:
    print(f"\nFailed to load embedding model: {error}")
    sys.exit(1)

print("Embedding model loaded successfully.")


# ============================================================
# CONNECT TO CHROMADB
# ============================================================

print("\nConnecting to ChromaDB...")

try:
    vectorstore = Chroma(
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings,
    )

except Exception as error:
    print(f"\nFailed to connect to ChromaDB: {error}")
    sys.exit(1)

print(f"ChromaDB directory: {VECTOR_DB_DIR}")


# ============================================================
# CHECK EXISTING CHUNK IDS
# ============================================================

print("\nChecking for existing chunks...")

try:
    existing_data = vectorstore.get(
        ids=chunk_ids,
        include=[],
    )

    existing_ids = set(existing_data["ids"])

except Exception as error:
    print(f"\nFailed to check existing chunks: {error}")
    sys.exit(1)

print(f"Existing chunks found: {len(existing_ids)}")


# ============================================================
# FILTER NEW CHUNKS
# ============================================================

new_chunks = []
new_ids = []

for document, chunk_id in zip(chunks, chunk_ids):

    if chunk_id not in existing_ids:
        new_chunks.append(document)
        new_ids.append(chunk_id)

print(f"New chunks to add: {len(new_chunks)}")


# ============================================================
# ADD NEW CHUNKS TO CHROMADB
# ============================================================

if new_chunks:

    print("\nAdding new chunks to ChromaDB...")

    try:
        vectorstore.add_documents(
            documents=new_chunks,
            ids=new_ids,
        )

        print(
            f"Successfully added "
            f"{len(new_chunks)} new chunks."
        )

    except Exception as error:
        print(f"\nFailed to add chunks: {error}")
        sys.exit(1)

else:
    print("\nNo new chunks found.")
    print("All generated chunks already exist in ChromaDB.")


# ============================================================
# FINAL COUNT
# ============================================================

try:
    final_count = vectorstore._collection.count()

except Exception as error:
    print(f"\nCould not retrieve final collection count: {error}")
    final_count = None


# ============================================================
# INGESTION SUMMARY
# ============================================================

print("\n====================================")
print("INGESTION COMPLETED")
print("====================================")

print(f"PDF files discovered: {len(pdf_files)}")
print(f"Pages successfully loaded: {len(all_documents)}")
print(f"Unique chunks processed: {len(chunks)}")
print(f"New chunks added: {len(new_chunks)}")

if final_count is not None:
    print(f"Total chunks in ChromaDB: {final_count}")

print("====================================")