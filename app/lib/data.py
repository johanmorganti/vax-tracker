import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "data")


def _load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_countries():
    return _load_json(os.path.join(DATA_DIR, "countries", "_index.json"))


def load_schedule(country_code):
    path = os.path.join(DATA_DIR, "countries", f"{country_code.lower()}.json")
    if not os.path.exists(path):
        return None
    return _load_json(path)


def load_antigens():
    data = _load_json(os.path.join(DATA_DIR, "antigens.json"))
    return {a["id"]: a for a in data["antigens"]}


def load_products():
    data = _load_json(os.path.join(DATA_DIR, "products.json"))
    return {p["id"]: p for p in data["products"]}
