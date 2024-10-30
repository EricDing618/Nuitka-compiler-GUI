import json
from pathlib import Path

DEFAULT_WINDOW_SIZE = "900x700"
DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = {
    "en": "English",
    "ru": "Русский",
    "es": "Español",
    "zh": "中文",
    "ar": "العربية"
}

def load_translations():
    try:
        translations_path = Path(__file__).parent / 'translations.json'
        with open(translations_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError("translations.json not found!")
