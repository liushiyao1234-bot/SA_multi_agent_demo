"""Load the local product knowledge base."""

import json
from pathlib import Path

from config import PROJECT_ROOT


def load_products(path=None):
    product_path = Path(path) if path else PROJECT_ROOT / "products.json"
    with product_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
