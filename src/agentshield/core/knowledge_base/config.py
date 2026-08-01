"""
config.py
---------

Central configuration loader for the Knowledge Base module.

Responsibilities:
    • Load environment variables from .env
    • Load settings.yaml
    • Resolve project paths
    • Expose configuration constants to every module

Every other file should import configuration ONLY from here.
"""

import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# =============================================================================
# Load .env
# =============================================================================

load_dotenv()

# =============================================================================
# Project Paths
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parents[4]

CONFIG_FILE = Path(__file__).resolve().parent / "settings.yaml"

# =============================================================================
# Load YAML Configuration
# =============================================================================

with CONFIG_FILE.open("r", encoding="utf-8") as file:
    SETTINGS = yaml.safe_load(file) or {}

# =============================================================================
# Helper Function
# =============================================================================


def _get(*keys, default=None):
    """
    Safely retrieve nested values from settings.yaml.

    Example:
        _get("chunking", "chunk_size")
    """

    value = SETTINGS

    for key in keys:

        if not isinstance(value, dict):
            return default

        value = value.get(key)

        if value is None:
            return default

    return value


# =============================================================================
# Paths
# =============================================================================

DATA_ROOT = PROJECT_ROOT / _get("paths", "data_root")

SCRAPED_ROOT = PROJECT_ROOT / _get("paths", "scraped_root")

QDRANT_PATH = PROJECT_ROOT / _get("paths", "qdrant_path")

CACHE_FILE = PROJECT_ROOT / _get("paths", "cache_file")

BM25_INDEX_FILE = PROJECT_ROOT / _get("paths", "bm25_index_file")

NVD_CACHE_FILE = PROJECT_ROOT / _get(
    "paths",
    "nvd_cve_cache_file",
)

COMPLIANCE_MAP_FILE = (
    Path(__file__).resolve().parent
    / _get("compliance", "map_file")
)

# =============================================================================
# Embedding Configuration
# =============================================================================

EMBEDDING_MODEL_NAME = os.getenv(
    "EMBEDDING_MODEL",
    _get("embedding", "model"),
)

EMBEDDING_DIM = (
    _get("embedding", "dims", default={})
    .get(EMBEDDING_MODEL_NAME, 768)
)

BGE_QUERY_PREFIX = _get(
    "embedding",
    "bge_query_prefix",
    default="",
)

# =============================================================================
# Chunking
# =============================================================================

CHUNK_SIZE = _get(
    "chunking",
    "chunk_size",
    default=500,
)

CHUNK_OVERLAP = _get(
    "chunking",
    "chunk_overlap",
    default=50,
)

# =============================================================================
# Vector Database
# =============================================================================

COLLECTION_NAME = _get(
    "vector_db",
    "collection_name",
)

VECTOR_BATCH_SIZE = _get(
    "vector_db",
    "batch_size",
    default=64,
)

# =============================================================================
# Retrieval
# =============================================================================

DEFAULT_TOP_K = _get(
    "retrieval",
    "default_top_k",
    default=5,
)

DENSE_WEIGHT = _get(
    "retrieval",
    "dense_weight",
    default=0.6,
)

SPARSE_WEIGHT = _get(
    "retrieval",
    "sparse_weight",
    default=0.4,
)

RRF_K = _get(
    "retrieval",
    "rrf_k",
    default=60,
)

DENSE_POOL = _get(
    "retrieval",
    "dense_pool",
    default=20,
)

SPARSE_POOL = _get(
    "retrieval",
    "sparse_pool",
    default=20,
)

BM25_K1 = _get(
    "retrieval",
    "bm25_k1",
    default=1.5,
)

BM25_B = _get(
    "retrieval",
    "bm25_b",
    default=0.75,
)


# =============================================================================
# Deduplication
# =============================================================================

SEMANTIC_DEDUP_THRESHOLD = _get(
    "dedup",
    "semantic_threshold",
    default=0.97,
)

# =============================================================================
# Categories
# =============================================================================

CATEGORY_MAP = _get(
    "categories",
    default={},
)

# =============================================================================
# Ingestion / Scrapers
# =============================================================================

DOC_REFRESH_FOLDERS = _get(
    "ingestion",
    "doc_refresh_folders",
    default=[],
)

NVD_API_URL = _get(
    "ingestion",
    "nvd_api_url",
    default="https://services.nvd.nist.gov/rest/json/cves/2.0",
)

NVD_RESULTS_PER_PAGE = _get(
    "ingestion",
    "nvd_results_per_page",
    default=200,
)

SCRAPER_TIMEOUT = _get(
    "ingestion",
    "timeout",
    default=30,
)

SCRAPER_DAYS_BACK = _get(
    "ingestion",
    "days_back",
    default=1,
)

VERIFY_SSL = _get(
    "ingestion",
    "verify_ssl",
    default=True,
)

USER_AGENT = _get(
    "ingestion",
    "user_agent",
    default="AgentShield-AI/1.0",
)

AWS_DOC_URL = _get(
    "ingestion",
    "aws_doc_url",
    default="",
)

AZURE_DOC_URL = _get(
    "ingestion",
    "azure_doc_url",
    default="",
)

GCP_DOC_URL = _get(
    "ingestion",
    "gcp_doc_url",
    default="",
)

CIS_DOC_URL = _get(
    "ingestion",
    "cis_doc_url",
    default="",
)

SUPPORTED_EXTENSIONS = tuple(
    _get(
        "ingestion",
        "supported_extensions",
        default=[
            ".txt",
            ".json",
            ".md",
        ],
    )
)

# =============================================================================
# Scheduler
# =============================================================================

SCHEDULER_REFRESH_HOUR = _get(
    "scheduler",
    "refresh_hour",
    default=3,
)

SCHEDULER_TIMEZONE = _get(
    "scheduler",
    "timezone",
    default="UTC",
)

SCHEDULER_MAX_INSTANCES = _get(
    "scheduler",
    "max_instances",
    default=1,
)

SCHEDULER_COALESCE = _get(
    "scheduler",
    "coalesce",
    default=True,
)

SCHEDULER_MISFIRE_GRACE_TIME = _get(
    "scheduler",
    "misfire_grace_time",
    default=3600,
)

# =============================================================================
# Environment Variables
# =============================================================================

HF_TOKEN = os.getenv("HF_TOKEN")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

NVD_API_KEY = os.getenv("NVD_API_KEY")

QDRANT_MODE = os.getenv("QDRANT_MODE", "local")

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")

QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))

QDRANT_GRPC_PORT = int(os.getenv("QDRANT_GRPC_PORT", "6334"))

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# =============================================================================
# Ensure required directories exist
# =============================================================================

DATA_ROOT.mkdir(parents=True, exist_ok=True)
SCRAPED_ROOT.mkdir(parents=True, exist_ok=True)
QDRANT_PATH.mkdir(parents=True, exist_ok=True)