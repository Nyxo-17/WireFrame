"""Module image_loader : Téléchargement asynchrone et cache disque des images officielles Warframe."""

from pathlib import Path
import threading
from typing import Callable
from PIL import Image, ImageDraw
import requests

CDN_BASE_URL = "https://cdn.warframestat.us/img"
IMG_CACHE_DIR = Path(__file__).resolve().parent.parent / "data" / "img_cache"
IMG_CACHE_DIR.mkdir(parents=True, exist_ok=True)

_MEMORY_CACHE: dict[tuple[str, int], Image.Image] = {}


def create_placeholder_pil(size: int = 56, accent: str = "#3B82F6") -> Image.Image:
    """Crée une vignette stylisée sombre en attendant le téléchargement de l'image."""
    key = (f"__placeholder_{accent}", size)
    if key in _MEMORY_CACHE:
        return _MEMORY_CACHE[key]

    img = Image.new("RGBA", (size, size), (20, 26, 41, 255))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([1, 1, size - 2, size - 2], radius=8, outline=accent, width=2)
    # Petit losange Orokin au centre
    c = size // 2
    r = size // 5
    draw.polygon([(c, c - r), (c + r, c), (c, c + r), (c - r, c)], outline="#E5C158", width=2)
    _MEMORY_CACHE[key] = img
    return img


def _load_and_fit(file_path: Path, size: int) -> Image.Image | None:
    """Ouvre une image locale et la redimensionne proprement dans un carré transparent."""
    try:
        with Image.open(file_path) as raw:
            rgba = raw.convert("RGBA")
            rgba.thumbnail((size - 4, size - 4), Image.Resampling.LANCZOS)
            canvas = Image.new("RGBA", (size, size), (16, 22, 36, 255))
            offset_x = (size - rgba.width) // 2
            offset_y = (size - rgba.height) // 2
            canvas.paste(rgba, (offset_x, offset_y), rgba)
            return canvas
    except Exception:
        return None


def fetch_item_image_async(
    image_name: str,
    size: int,
    on_ready: Callable[[Image.Image], None],
) -> Image.Image:
    """Retourne l'image en cache immédiatement, ou lance son téléchargement en tâche de fond."""
    if not image_name:
        return create_placeholder_pil(size)

    cache_key = (image_name, size)
    if cache_key in _MEMORY_CACHE:
        return _MEMORY_CACHE[cache_key]

    local_file = IMG_CACHE_DIR / image_name
    if local_file.exists():
        loaded = _load_and_fit(local_file, size)
        if loaded:
            _MEMORY_CACHE[cache_key] = loaded
            return loaded

    def _worker() -> None:
        try:
            url = f"{CDN_BASE_URL}/{image_name}"
            resp = requests.get(url, timeout=6)
            if resp.status_code == 200 and resp.content:
                local_file.write_bytes(resp.content)
                pil_img = _load_and_fit(local_file, size)
                if pil_img:
                    _MEMORY_CACHE[cache_key] = pil_img
                    on_ready(pil_img)
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()
    return create_placeholder_pil(size)

