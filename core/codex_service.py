"""Module codex_service : Recherche dans le Codex (Ressources/Mods/Warframes) & Calcul des Mises à Prix."""

from datetime import datetime, timedelta, timezone
from typing import Any
from data.data_manager import load_codex_data

# Cycle de rotation des Mises à Prix (A -> B -> C) : change toutes les 2h30 (9000 secondes)
BOUNTY_ROTATION_SECONDS = 9000
ROTATION_LETTERS = ["Rotation A", "Rotation B", "Rotation C"]


def search_codex_items(category_key: str, query: str = "") -> list[dict[str, str]]:
    """Retourne la liste filtrée des éléments ('resources', 'mods' ou 'warframes')."""
    all_data = load_codex_data()
    items = all_data.get(category_key, [])
    clean_q = query.strip().lower()
    if not clean_q:
        return items

    return [
        item
        for item in items
        if clean_q in item.get("name", "").lower()
        or clean_q in item.get("category", "").lower()
        or clean_q in item.get("location", "").lower()
        or clean_q in item.get("drop", "").lower()
    ]


def get_current_bounty_rotation() -> dict[str, Any]:
    """Calcule la rotation actuelle (A, B ou C), la suivante et la date d'expiration des Mises à Prix."""
    now = datetime.now(timezone.utc)
    total_secs = int(now.timestamp())

    rot_index = (total_secs // BOUNTY_ROTATION_SECONDS) % 3
    next_index = (rot_index + 1) % 3

    elapsed_in_rot = total_secs % BOUNTY_ROTATION_SECONDS
    rem_seconds = BOUNTY_ROTATION_SECONDS - elapsed_in_rot
    expiry_iso = (now + timedelta(seconds=rem_seconds)).isoformat().replace("+00:00", "Z")

    codex = load_codex_data()
    return {
        "current_rotation": ROTATION_LETTERS[rot_index],
        "next_rotation": ROTATION_LETTERS[next_index],
        "rotation_index": rot_index,  # 0=A, 1=B, 2=C
        "expiry": expiry_iso,
        "hubs": codex.get("bounties", []),
    }
