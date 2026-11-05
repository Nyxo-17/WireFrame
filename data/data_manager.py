"""Module data_manager : Seul point d'accès aux fichiers JSON du dossier data/."""

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent
DUVIRI_FILE = DATA_DIR / "duviri_rotations.json"
TRANSLATIONS_FILE = DATA_DIR / "translations.json"
CODEX_FILE = DATA_DIR / "codex_data.json"
CACHE_FILE = DATA_DIR / "cache.json"


def _read_json_safe(file_path: Path, default_value: Any) -> Any:
    """Fonction utilitaire sécurisée pour lire un fichier JSON sans jamais planter."""
    if not file_path.exists():
        return default_value
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as error:
        print(f"[Erreur Data] Impossible de lire {file_path.name} : {error}")
        return default_value


def load_duviri_rotations() -> dict[str, list[list[str]]]:
    """Charge et retourne les listes des rotations de Duviri."""
    return _read_json_safe(DUVIRI_FILE, {"warframes_weeks": [], "incarnon_weeks": []})


def load_translations() -> dict[str, dict[str, str]]:
    """Charge le dictionnaire de traductions FR / EN."""
    return _read_json_safe(TRANSLATIONS_FILE, {"fr": {}, "en": {}})


def load_codex_data() -> dict[str, list[dict[str, str]]]:
    """Charge l'encyclopédie des Ressources, Mods, Warframes et Mises à Prix."""
    return _read_json_safe(
        CODEX_FILE,
        {"resources": [], "mods": [], "warframes": [], "bounties": []},
    )


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
    """Charge la dernière sauvegarde connue de l'API."""
    return _read_json_safe(CACHE_FILE, None)
