"""Module duviri_calculator : Calcul des rotations hebdomadaires du Circuit de Duviri."""

from datetime import datetime, timedelta, timezone
from typing import Any
from data.data_manager import load_duviri_rotations

# Lundi 24 avril 2023 à 00h00 UTC : Début de la Semaine 1 (Excalibur / Braton)
DUVIRI_EPOCH = datetime(2023, 4, 24, 0, 0, 0, tzinfo=timezone.utc)
SECONDS_PER_WEEK = 7 * 24 * 3600


def get_next_monday_utc() -> str:
    """Calcule la date ISO exacte du prochain lundi à 00h00 UTC (reset hebdomadaire)."""
    now = datetime.now(timezone.utc)
    days_until_monday = (7 - now.weekday()) % 7
    if days_until_monday == 0:
        days_until_monday = 7

    next_monday = (now + timedelta(days=days_until_monday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return next_monday.isoformat().replace("+00:00", "Z")


def get_current_duviri_rotation() -> dict[str, Any]:
    """Retourne les rotations Actuelle et Suivante de Duviri (Warframes + Incarnon)."""
    rotations_data = load_duviri_rotations()
    warframes_list = rotations_data.get("warframes_weeks", [])
    incarnon_list = rotations_data.get("incarnon_weeks", [])

    now = datetime.now(timezone.utc)
    elapsed_seconds = (now - DUVIRI_EPOCH).total_seconds()
    weeks_since_epoch = int(elapsed_seconds // SECONDS_PER_WEEK)

    wf_count = len(warframes_list)
    inc_count = len(incarnon_list)

    wf_index = weeks_since_epoch % wf_count if wf_count else 0
    wf_next_index = (wf_index + 1) % wf_count if wf_count else 0

    inc_index = weeks_since_epoch % inc_count if inc_count else 0
    inc_next_index = (inc_index + 1) % inc_count if inc_count else 0

    return {
        "warframe_week_number": wf_index + 1,
        "warframes": warframes_list[wf_index] if wf_count else [],
        "next_warframes": warframes_list[wf_next_index] if wf_count else [],
        "incarnon_week_number": inc_index + 1,
        "incarnon_weapons": incarnon_list[inc_index] if inc_count else [],
        "next_incarnon_weapons": incarnon_list[inc_next_index] if inc_count else [],
        "all_warframes_weeks": warframes_list,
        "all_incarnon_weeks": incarnon_list,
        "expiry": get_next_monday_utc(),
    }
