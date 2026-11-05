"""Module updater : Système de vérification et d'installation automatique des mises à jour depuis GitHub."""

from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import sys
from typing import Any
import zipfile
import requests

ROOT_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = ROOT_DIR / "version.json"

# Fichiers personnels de l'utilisateur à ne jamais écraser lors d'une mise à jour
PROTECTED_PATHS = {
    "data/settings.json",
    "data/cache.json",
}


def _parse_semver(v_str: str) -> tuple[int, ...]:
    """Convertit '1.2.0' en tuple (1, 2, 0) pour comparer les versions proprement."""
    clean = v_str.strip().lstrip("vV")
    parts = []
    for p in clean.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def get_local_version_info() -> dict[str, str]:
    """Lit les informations de version locale depuis version.json."""
    default_info = {
        "version": "1.0.0",
        "repo": "Nyxo-17/WireFrame",
        "branch": "master",
        "changelog": "",
    }
    if not VERSION_FILE.exists():
        return default_info
    try:
        with open(VERSION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {**default_info, **data}
    except Exception:
        return default_info


def get_local_version() -> str:
    return get_local_version_info().get("version", "1.0.0")


def check_for_updates() -> dict[str, Any]:
    """Interroge le dépôt GitHub de Nyxo_17 pour savoir si une nouvelle version est disponible."""
    local_info = get_local_version_info()
    local_v = local_info.get("version", "1.0.0")
    repo = local_info.get("repo", "Nyxo-17/WireFrame")

    headers = {"User-Agent": "WireFrame-Updater/1.0", "Cache-Control": "no-cache"}
    for branch in (local_info.get("branch", "master"), "main", "master"):
        raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/version.json"
        try:
            resp = requests.get(raw_url, headers=headers, timeout=6)
            if resp.status_code == 200:
                remote_data = resp.json()
                remote_v = remote_data.get("version", local_v)
                is_newer = _parse_semver(remote_v) > _parse_semver(local_v)
                return {
                    "update_available": is_newer,
                    "local_version": local_v,
                    "remote_version": remote_v,
                    "branch": branch,
                    "repo": repo,
                    "changelog": remote_data.get("changelog", "Nouvelle mise à jour disponible !"),
                    "error": None,
                }
        except Exception as exc:
            last_err = str(exc)

    return {
        "update_available": False,
        "local_version": local_v,
        "remote_version": local_v,
        "branch": local_info.get("branch", "master"),
        "repo": repo,
        "changelog": "",
        "error": "Dépôt GitHub non encore publié ou hors-ligne.",
    }


def download_and_apply_update(repo: str = "Nyxo-17/WireFrame", branch: str = "master") -> tuple[bool, str]:
    """Télécharge l'archive ZIP de la dernière version sur GitHub et met à jour les fichiers locaux."""
    zip_url = f"https://github.com/{repo}/archive/refs/heads/{branch}.zip"
    headers = {"User-Agent": "WireFrame-Updater/1.0"}
    try:
        resp = requests.get(zip_url, headers=headers, timeout=25)
        resp.raise_for_status()

        with zipfile.ZipFile(BytesIO(resp.content)) as zf:
            names = zf.namelist()
            if not names:
                return False, "Archive GitHub vide."
            root_prefix = names[0].split("/")[0] + "/"

            for member in names:
                if not member.startswith(root_prefix) or member.endswith("/"):
                    continue
                rel_path = member[len(root_prefix):]
                if not rel_path or rel_path in PROTECTED_PATHS or rel_path.startswith("data/img_cache/"):
                    continue

                target_file = ROOT_DIR / rel_path
                target_file.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(member) as src, open(target_file, "wb") as dst:
                    shutil.copyfileobj(src, dst)

        return True, "Mise à jour installée avec succès !"
    except Exception as exc:
        return False, f"Échec de la mise à jour : {exc}"


def restart_application() -> None:
    """Relance immédiatement l'application avec la nouvelle version."""
    python_exe = sys.executable
    main_script = str(ROOT_DIR / "main.py")
    os.execl(python_exe, python_exe, main_script)
