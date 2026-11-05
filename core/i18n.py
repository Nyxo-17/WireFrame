"""Module i18n : Gestionnaire de langue Français / Anglais (Internationalisation)."""

from data.data_manager import load_translations

_TRANSLATIONS = load_translations()
_CURRENT_LANG = "fr"

# Correspondance pour traduire dynamiquement les états de planètes FR <-> EN
_STATE_MAP = {
    "jour": "state_day",
    "day": "state_day",
    "nuit": "state_night",
    "night": "state_night",
    "chaud": "state_warm",
    "warm": "state_warm",
    "froid": "state_cold",
    "cold": "state_cold",
    "fass": "state_fass",
    "vome": "state_vome",
}


def get_lang() -> str:
    """Retourne le code de la langue actuelle ('fr' ou 'en')."""
    return _CURRENT_LANG


def set_lang(lang_code: str) -> None:
    """Change la langue active ('fr' ou 'en')."""
    global _CURRENT_LANG
    if lang_code in ("fr", "en"):
        _CURRENT_LANG = lang_code


def tr(key: str) -> str:
    """Retourne le texte traduit correspondant à la clé dans la langue active."""
    lang_dict = _TRANSLATIONS.get(_CURRENT_LANG, {})
    return lang_dict.get(key, key)


def tr_state(raw_state: str) -> str:
    """Traduit l'état d'un monde ouvert (Jour/Day, Nuit/Night, Froid/Cold...) selon la langue."""
    clean = raw_state.strip().lower()
    state_key = _STATE_MAP.get(clean)
    return tr(state_key) if state_key else raw_state

