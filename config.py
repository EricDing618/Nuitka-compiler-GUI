import json
from pathlib import Path

DEFAULT_WINDOW_SIZE = "900x700"
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ru": "Русский",
    "es": "Español"
}

def load_translations():
    try:
        with open('translations.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("translations.json not found!")
