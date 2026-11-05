"""Module api_client : Récupération de l'état des serveurs Warframe (API + Fallback local)."""

from datetime import datetime, timedelta, timezone
from typing import Any
import requests
from data.data_manager import load_api_cache, save_api_cache

API_URL = "https://api.warframestat.us/pc/"
HEADERS = {"User-Agent": "WireframeV1-DesktopApp/1.0", "Accept-Language": "fr"}

# Époques de référence UTC pour le mode de secours hors-ligne
VALLIS_EPOCH = datetime(2018, 11, 10, 8, 13, 48, tzinfo=timezone.utc)
BARO_EPOCH = datetime(2023, 4, 21, 13, 0, 0, tzinfo=timezone.utc)


def _translate_state(raw_state: str, world: str) -> str:
    """Traduit l'état renvoyé par l'API en français court (ex: 'Jour', 'Nuit', 'Froid')."""
    state = raw_state.lower()
    if world in ("cetus", "earth"):
        return "Jour" if state == "day" else "Nuit"
    if world == "vallis":
        return "Chaud" if state == "warm" else "Froid"
    if world == "cambion":
        return "Fass" if state == "fass" else "Vome"
    return raw_state.capitalize()


def _build_offline_fallback() -> dict[str, Any]:
    """Génère des cycles calculés localement en UTC si l'API et le cache sont indisponibles."""
    now = datetime.now(timezone.utc)

    # Vallée Orbis : boucle de 1600s (400s Chaud, 1200s Froid)
    vallis_elapsed = int((now - VALLIS_EPOCH).total_seconds()) % 1600
    is_warm = vallis_elapsed < 400
    vallis_rem = (400 - vallis_elapsed) if is_warm else (1600 - vallis_elapsed)
    vallis_exp = (now + timedelta(seconds=vallis_rem)).isoformat().replace("+00:00", "Z")

    # Cetus & Cambion : boucle de 9000s (6000s Jour/Fass, 3000s Nuit/Vome)
    cetus_elapsed = int(now.timestamp()) % 9000
    is_day = cetus_elapsed < 6000
    cetus_rem = (6000 - cetus_elapsed) if is_day else (9000 - cetus_elapsed)
    cetus_exp = (now + timedelta(seconds=cetus_rem)).isoformat().replace("+00:00", "Z")

    # Terre (Forêts) : cycle exact de 8h (4h Jour = 14400s, 4h Nuit = 14400s)
    earth_elapsed = int(now.timestamp()) % 28800
    earth_day = earth_elapsed < 14400
    earth_rem = (14400 - earth_elapsed) if earth_day else (28800 - earth_elapsed)
    earth_exp = (now + timedelta(seconds=earth_rem)).isoformat().replace("+00:00", "Z")

    # Baro Ki'Teer : cycle de 14 jours
    baro_cycle = 14 * 86400
    baro_elapsed = int((now - BARO_EPOCH).total_seconds()) % baro_cycle
    baro_active = baro_elapsed < (2 * 86400)
    baro_rem = (2 * 86400 - baro_elapsed) if baro_active else (baro_cycle - baro_elapsed)
    baro_target = (now + timedelta(seconds=baro_rem)).isoformat().replace("+00:00", "Z")

    return {
        "source": "En direct (Calcul UTC)",
        "cetus": {"state": "Jour" if is_day else "Nuit", "expiry": cetus_exp},
        "vallis": {"state": "Chaud" if is_warm else "Froid", "expiry": vallis_exp},
        "cambion": {"state": "Fass" if is_day else "Vome", "expiry": cetus_exp},
        "earth": {"state": "Jour" if earth_day else "Nuit", "expiry": earth_exp},
        "baro": {
            "active": baro_active,
            "location": "Relais Kronia (Saturne)",
            "activation": now.isoformat() if baro_active else baro_target,
            "expiry": baro_target if baro_active else "",
            "inventory": [],
        },
    }


def fetch_world_state() -> dict[str, Any]:
    """Interroge l'API Warframe, met à jour le cache, ou bascule en mode secours si hors-ligne."""
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=5)
        response.raise_for_status()
        raw = response.json()

        cetus = raw.get("cetusCycle", {})
        vallis = raw.get("vallisCycle", {})
        cambion = raw.get("cambionCycle", {})
        earth = raw.get("earthCycle", {})
        baro = raw.get("voidTrader", {})

        clean_state = {
            "source": "En direct (API)",
            "cetus": {
                "state": _translate_state(cetus.get("state", "day"), "cetus"),
                "expiry": cetus.get("expiry", ""),
            },
            "vallis": {
                "state": _translate_state(vallis.get("state", "cold"), "vallis"),
                "expiry": vallis.get("expiry", ""),
            },
            "cambion": {
                "state": _translate_state(cambion.get("state", "fass"), "cambion"),
                "expiry": cambion.get("expiry", ""),
            },
            "earth": {
                "state": _translate_state(earth.get("state", "day"), "earth"),
                "expiry": earth.get("expiry", ""),
            },
            "baro": {
                "active": bool(baro.get("active", False)),
                "location": baro.get("location", "Relais inconnu"),
                "activation": baro.get("activation", ""),
                "expiry": baro.get("expiry", ""),
                "inventory": [
                    {
                        "item": item.get("item", "Objet"),
                        "ducats": item.get("ducats", 0),
                        "credits": item.get("credits", 0),
                    }
                    for item in baro.get("inventory", [])
                ],
            },
        }
        save_api_cache(clean_state)
        return clean_state

    except requests.RequestException:
        cached = load_api_cache()
        if cached and "earth" in cached:
            cached["source"] = "Cache local"
            return cached
        return _build_offline_fallback()
