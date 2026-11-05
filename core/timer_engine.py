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
    """Transforme un nombre de secondes en texte lisible (ex: '02j 04h 12m 09s' ou '42m 15s')."""
    if seconds <= 0:
        return "Rotation en cours..."

    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, secs = divmod(remainder, 60)

    if days > 0:
        return f"{days:02d}j {hours:02d}h {minutes:02d}m {secs:02d}s"
    if hours > 0:
        return f"{hours:02d}h {minutes:02d}m {secs:02d}s"
    return f"{minutes:02d}m {secs:02d}s"


def get_formatted_timer(expiry_iso: str) -> str:
    """Fonction tout-en-un : prend une date ISO et retourne directement le texte du timer."""
    remaining = get_remaining_seconds(expiry_iso)
    return format_countdown(remaining)
