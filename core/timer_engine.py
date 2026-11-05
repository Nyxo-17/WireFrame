"""Module timer_engine : Calcul et formatage des comptes à rebours en temps réel (UTC)."""

from datetime import datetime, timezone


def parse_iso_date(iso_string: str) -> datetime | None:
    """Convertit une date texte ISO (ex: '2026-11-05T16:30:00.000Z') en objet datetime UTC."""
    if not iso_string:
        return None
    try:
        clean_iso = iso_string.replace("Z", "+00:00")
        return datetime.fromisoformat(clean_iso)
    except ValueError:
        return None


def get_remaining_seconds(expiry_iso: str) -> int:
    """Retourne le nombre de secondes restantes avant la date cible (0 si dépassée)."""
    target_date = parse_iso_date(expiry_iso)
    if target_date is None:
        return 0

    now_utc = datetime.now(timezone.utc)
    delta = (target_date - now_utc).total_seconds()
    return max(0, int(delta))


def format_countdown(seconds: int) -> str:
    """Transforme un nombre de secondes en texte complet (ex: '02j 04h 12m 09s' ou '42m 15s')."""
    if seconds <= 0:
        return "Rotation..."

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    if days > 0:
        return f"{days}j {hours:02d}h {minutes:02d}m {secs:02d}s"
    if hours > 0:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    return f"{minutes}m {secs:02d}s"


def format_short_countdown(seconds: int) -> str:
    """Format compact pour le panneau latéral droit (ex: '3j 8h' ou '57m 26s')."""
    if seconds <= 0:
        return "0m 00s"

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    if days > 0:
        return f"{days}j {hours}h"
    if hours > 0:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    return f"{minutes}m {secs:02d}s"


def get_formatted_timer(expiry_iso: str, short: bool = False) -> str:
    """Prend une date ISO et retourne directement le texte du timer (complet ou compact)."""
    remaining = get_remaining_seconds(expiry_iso)
    return format_short_countdown(remaining) if short else format_countdown(remaining)
