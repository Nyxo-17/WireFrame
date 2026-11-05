"""Module data_manager : Seul point d'accès aux fichiers JSON du dossier data/."""

import json
from pathlib import Path
from typing import Any

# Chemin absolu vers le dossier data/ (peu importe d'où l'application est lancée)
DATA_DIR = Path(__file__).resolve().parent
DUVIRI_FILE = DATA_DIR / "duviri_rotations.json"
CACHE_FILE = DATA_DIR / "cache.json"


def load_duviri_rotations() -> dict[str, list[list[str]]]:
    """Charge et retourne les listes des rotations de Duviri depuis le fichier JSON."""
    if not DUVIRI_FILE.exists():
        return {"warframes_weeks": [], "incarnon_weeks": []}

    try:
        with open(DUVIRI_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"[Erreur Data] Impossible de lire {DUVIRI_FILE.name} : {error}")
        return {"warframes_weeks": [], "incarnon_weeks": []}


def save_api_cache(data: dict[str, Any]) -> bool:
    """Sauvegarde la dernière réponse de l'API Warframe dans data/cache.json."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)
        return True
    except OSError as error:
        print(f"[Erreur Data] Impossible d'écrire le cache : {error}")
        return False


def load_api_cache() -> dict[str, Any] | None:
    """Charge la dernière sauvegarde connue de l'API (utile en cas de coupure Internet)."""
    if not CACHE_FILE.exists():
        return None

    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"[Erreur Data] Cache corrompu ou illisible : {error}")
        return None

