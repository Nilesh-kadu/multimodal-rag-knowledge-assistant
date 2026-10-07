"""
NEXUS AI - User Knowledge Base

Manages isolated Chroma collections for individual users.

Each user gets a separate Chroma collection:
    nexus_user_<user_id>

Global knowledge is NOT handled here.
"""
from functools import lru_cache
from datetime import datetime, timezone, timedelta
import re
from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from datetime import datetime, timezone, timedelta


# ============================================================
# PROJECT CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

VECTOR_DB_DIR = PROJECT_ROOT / "vector_db"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
USER_DATA_TTL_HOURS = 24


# ============================================================
# EMBEDDINGS
# ============================================================
@lru_cache(maxsize=1)
def get_embeddings():
    """
    Load the same embedding model used by NEXUS AI.
    """

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL
    )


# ============================================================
# USER ID VALIDATION
# ============================================================

def sanitize_user_id(user_id: str) -> str:
    """
    Convert a user ID into a safe Chroma collection suffix.
    """

    user_id = str(user_id or "").strip().lower()

    if not user_id:
        raise ValueError("User ID cannot be empty.")

    user_id = re.sub(
        r"[^a-zA-Z0-9_-]",
        "_",
        user_id,
    )

    return user_id[:50]


# ============================================================
# USER COLLECTION NAME
# ============================================================

def get_user_collection_name(user_id: str) -> str:
    """
    Generate the isolated Chroma collection name
    for a user.
    """

    safe_user_id = sanitize_user_id(user_id)

    return f"nexus_user_{safe_user_id}"


# ============================================================
# USER VECTORSTORE
# ============================================================

def get_user_vectorstore(user_id: str):
    """
    Return the Chroma vectorstore belonging ONLY to
    the specified user.
    """

    collection_name = get_user_collection_name(
        user_id
    )

    embeddings = get_embeddings()

    user_vectorstore = Chroma(
        collection_name=collection_name,
        persist_directory=str(VECTOR_DB_DIR),
        embedding_function=embeddings,
    )

    return user_vectorstore
def update_user_activity(user_id: str):
    """
    Update the last activity timestamp for a user's collection.
    """

    vectorstore = get_user_vectorstore(user_id)

    collection = vectorstore._collection

    metadata = collection.metadata or {}

    metadata["last_activity"] = (
        datetime.now(timezone.utc).isoformat()
    )

    collection.modify(
        metadata=metadata
    )
def get_user_last_activity(user_id: str):
    """
    Return the last activity timestamp for a user.
    """

    vectorstore = get_user_vectorstore(user_id)

    metadata = vectorstore._collection.metadata or {}

    last_activity = metadata.get("last_activity")

    if not last_activity:
        return None

    try:
        return datetime.fromisoformat(last_activity)
    except ValueError:
        return None

def delete_expired_user_collections():
    """
    Delete user collections that have been inactive
    for more than USER_DATA_TTL_HOURS.
    """

    import chromadb

    client = chromadb.PersistentClient(
        path=str(VECTOR_DB_DIR)
    )

    now = datetime.now(timezone.utc)

    deleted_collections = []

    collections = client.list_collections()

    for collection in collections:

        collection_name = collection.name

        # Only process NEXUS user collections.
        if not collection_name.startswith(
            "nexus_user_"
        ):
            continue

        metadata = collection.metadata or {}

        last_activity = metadata.get(
            "last_activity"
        )

        # Do not delete collections that do not
        # have activity information.
        if not last_activity:
            continue

        try:
            last_activity_time = (
                datetime.fromisoformat(
                    last_activity
                )
            )
        except ValueError:
            continue

        inactive_for = (
            now - last_activity_time
        )

        if inactive_for >= timedelta(
            hours=USER_DATA_TTL_HOURS
        ):
            client.delete_collection(
                collection_name
            )

            deleted_collections.append(
                collection_name
            )

    return deleted_collections    
# ============================================================
# USER ACTIVITY / 24-HOUR TTL
# ============================================================

USER_DATA_TTL_HOURS = 24


def update_user_activity(user_id: str):
    """
    Update the last activity timestamp for the user's
    Chroma collection.
    """

    vectorstore = get_user_vectorstore(user_id)

    collection = vectorstore._collection

    metadata = collection.metadata or {}

    metadata["last_activity"] = (
        datetime.now(timezone.utc).isoformat()
    )

    collection.modify(
        metadata=metadata
    )


def get_user_last_activity(user_id: str):
    """
    Return the last activity timestamp for a user.
    """

    vectorstore = get_user_vectorstore(user_id)

    metadata = (
        vectorstore._collection.metadata
        or {}
    )

    value = metadata.get("last_activity")

    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except Exception:
        return None

def delete_expired_user_collections():
    """
    Delete user collections that have had no activity
    for more than 24 hours.

    Only collections beginning with:
        nexus_user_
    are considered.
    """

    import chromadb

    client = chromadb.PersistentClient(
        path=str(VECTOR_DB_DIR)
    )

    now = datetime.now(timezone.utc)

    deleted_collections = []

    collections = client.list_collections()

    for collection in collections:

        collection_name = collection.name

        # Safety check:
        # NEVER touch global or unrelated collections.
        if not collection_name.startswith(
            "nexus_user_"
        ):
            continue

        metadata = collection.metadata or {}

        last_activity = metadata.get(
            "last_activity"
        )

        if not last_activity:
            continue

        try:
            last_activity_time = (
                datetime.fromisoformat(
                    last_activity
                )
            )

        except Exception:
            continue

        inactive_for = (
            now - last_activity_time
        )

        if inactive_for >= timedelta(
            hours=USER_DATA_TTL_HOURS
        ):

            client.delete_collection(
                collection_name
            )

            deleted_collections.append(
                collection_name
            )

    return deleted_collections    
# ============================================================
# CHECK USER KNOWLEDGE
# ============================================================

def get_user_document_count(user_id: str) -> int:
    """
    Return the number of indexed chunks belonging to
    the specified user's collection.
    """

    vectorstore = get_user_vectorstore(user_id)

    data = vectorstore.get(
        include=[],
    )

    return len(data.get("ids", []))


# ============================================================
# DELETE USER KNOWLEDGE
# ============================================================

def clear_user_knowledge(user_id: str) -> int:
    """
    Delete all indexed knowledge belonging to one user.

    Returns:
        Number of deleted chunks.
    """

    vectorstore = get_user_vectorstore(user_id)

    data = vectorstore.get(
        include=[],
    )

    ids = data.get("ids", [])

    if not ids:
        return 0

    vectorstore.delete(
        ids=ids
    )

    return len(ids)