"""Runtime configuration for the SA multi-agent demo."""

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

API_URL = os.getenv(
    "GLM_API_URL",
    "https://api-ap-southeast-1.modelarts-maas.com/v2/chat/completions",
)
API_KEY = os.getenv("GLM_API_KEY")
MODEL_NAME = os.getenv("GLM_MODEL", "glm-5.1")
REQUEST_TIMEOUT = int(os.getenv("GLM_REQUEST_TIMEOUT", "60"))
DEBUG = os.getenv("SA_DEMO_DEBUG", "false").lower() in {"1", "true", "yes", "on"}
