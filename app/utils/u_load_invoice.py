import json
from pathlib import Path

def load_invoice_from_file(file_path: str = "data/invoice.json") -> dict:
    path = Path(file_path)
    if path.exists():
        with open(path, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"{file_path} not found.")
