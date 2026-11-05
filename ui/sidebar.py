"""Module sidebar : Barre latérale gauche fixe avec effet Neon Glow (Gaussian Blur) sur l'onglet actif."""

from pathlib import Path
from typing import Callable
import customtkinter as ctk
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from core.i18n import tr

LOGO_PATH = Path(__file__).resolve().parent.parent / "data" / "app_logo.png"

BG_SIDEBAR = "#0D111A"
BG_ACTIVE_INNER = "#172544"
BG_HOVER_INNER = "#141D30"

NAV_ITEMS_CONFIG = [
    ("welcome", "🏠", "nav_welcome", 2, "home"),
    ("notifications", "🔔", "nav_notifications", 3, "home"),
    ("resources", "💎", "nav_resources", 5, "inv"),
    ("mods", "🃏", "nav_mods", 6, "inv"),
    ("warframes", "⚡", "nav_warframes", 7, "inv"),
    ("worlds", "🌍", "nav_worlds", 9, "cycles"),
    ("bounties", "🎯", "nav_bounties", 10, "cycles"),
    ("duviri", "🌀", "nav_duviri", 11, "cycles"),
    ("baro", "💠", "nav_baro", 12, "cycles"),
]


def _clean_label(raw_text: str) -> str:
    """Retire l'éventuel emoji en préfixe dans la traduction pour aligner le texte proprement."""
    parts = raw_text.split("   ", 1)
    return parts[1].strip() if len(parts) > 1 else raw_text.strip()


def _build_nav_backgrounds() -> tuple[ctk.CTkImage, ctk.CTkImage, ctk.CTkImage]:
    """Génère en 2x Retina les 3 états du bouton : inactif, survolé et sélectionné avec Halo Glow."""
    w, h = 408, 84  # 2x supersampling pour un affichage 204x42 ultra net
    base_rgb = (13, 17, 26)  # #0D111A

    # 1. État inactif
    img_idle = Image.new("RGBA", (w, h), (*base_rgb, 255))

    # 2. État survol (Hover)
    img_hover = Image.new("RGBA", (w, h), (*base_rgb, 255))
    draw_h = ImageDraw.Draw(img_hover)
    draw_h.rounded_rectangle((14, 12, w - 15, h - 13), radius=14, fill=(20, 29, 48, 255), outline=(38, 56, 92, 255), width=2)

    # 3. État actif avec Halo Neon Glow externe (GaussianBlur) + Intérieur uniforme sans couture
    img_active = Image.new("RGBA", (w, h), (*base_rgb, 255))

    # Couche A : Double halo externe diffus bleu/cyan électrique autour du bouton
    halo_outer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(halo_outer).rounded_rectangle(
        (10, 8, w - 11, h - 9), radius=18, fill=(37, 99, 235, 190), outline=(96, 165, 250, 255), width=8
    )
    halo_outer = halo_outer.filter(ImageFilter.GaussianBlur(radius=9))
    img_active = Image.alpha_composite(img_active, halo_outer)

    halo_inner = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(halo_inner).rounded_rectangle(
        (13, 11, w - 14, h - 12), radius=15, outline=(147, 197, 253, 255), width=4
    )
    halo_inner = halo_inner.filter(ImageFilter.GaussianBlur(radius=4))
    img_active = Image.alpha_composite(img_active, halo_inner)

    # Couche B : Corps interne uniforme (#172544) + double bordure néon nette
    draw_act = ImageDraw.Draw(img_active)
    draw_act.rounded_rectangle(
        (14, 12, w - 15, h - 13), radius=14, fill=(23, 37, 68, 255), outline=(121, 192, 255, 255), width=2
    )
    draw_act.rounded_rectangle(
        (16, 14, w - 17, h - 15), radius=12, outline=(45, 85, 155, 255), width=1
    )

    # Couche C : Barre verticale lumineuse à gauche (x=22..28 en 2x, soit x=11..14 en 1x)
    draw_act.rounded_rectangle((22, 24, 28, h - 25), radius=3, fill=(147, 197, 253, 255))

    size = (204, 42)
    return (
        ctk.CTkImage(light_image=img_idle, dark_image=img_idle, size=size),
        ctk.CTkImage(light_image=img_hover, dark_image=img_hover, size=size),
        ctk.CTkImage(light_image=img_active, dark_image=img_active, size=size),
    )


class Sidebar(ctk.CTkFrame):
    """Menu latéral fixe avec alignement strict et effet Glow lumineux sur la section sélectionnée."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Callable[[str], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__(master, width=220, corner_radius=0, fg_color=BG_SIDEBAR)
        self.on_navigate = on_navigate
        self.on_refresh = on_refresh
        self.active_key: str = "welcome"

        self._bg_idle, self._bg_hover, self._bg_active = _build_nav_backgrounds()

        self.nav_rows: dict[str, ctk.CTkLabel] = {}
        self.nav_icons: dict[str, ctk.CTkLabel] = {}
        self.nav_labels: dict[str, tuple[ctk.CTkLabel, str]] = {}
        self.nav_section_map: dict[str, str] = {}

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(15, weight=1)

        self._build_creator_badge()
        self._build_navigation()
        self._build_footer()

    def _build_creator_badge(self) -> None:
        profile_box = ctk.CTkFrame(self, fg_color="transparent")
        profile_box.grid(row=0, column=0, padx=14, pady=(12, 8), sticky="ew")
        profile_box.grid_columnconfigure(1, weight=1)

        if LOGO_PATH.exists():
            pil_logo = Image.open(LOGO_PATH)
            ctk_logo = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(40, 40))
            emblem = ctk.CTkLabel(profile_box, text="", image=ctk_logo, width=40, height=40)
        else:
            emblem = ctk.CTkLabel(
                profile_box,
                text="❖",
                width=38,
                height=38,
                corner_radius=6,
                fg_color="#2A2415",
                text_color="#E5C158",
                font=ctk.CTkFont(size=20, weight="bold"),
            )
        emblem.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="w")

        ctk.CTkLabel(
            profile_box,
            text="Nyxo_17",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        ).grid(row=0, column=1, sticky="ew")

        self.role_lbl = ctk.CTkLabel(
            profile_box,
            text=tr("creator_role"),
            font=ctk.CTkFont(size=11),
            text_color="#7D8590",
            anchor="w",
        )
        self.role_lbl.grid(row=1, column=1, sticky="ew")

    def _build_navigation(self) -> None:
        self.sec_home_lbl = self._make_section_header("sec_home", row=1)
        self.sec_inv_lbl = self._make_section_header("sec_inventory", row=4)
        self.sec_cycles_lbl = self._make_section_header("sec_cycles", row=8)
        self.section_headers = {
            "home": self.sec_home_lbl,
            "inv": self.sec_inv_lbl,
            "cycles": self.sec_cycles_lbl,
        }

        for key, icon, tr_key, row_idx, sec_id in NAV_ITEMS_CONFIG:
            self.nav_section_map[key] = sec_id
            self._create_aligned_nav_item(key, icon, tr_key, row_idx)

    def _make_section_header(self, tr_key: str, row: int) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(
            self,
            text=tr(tr_key),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#6E7681",
            anchor="w",
        )
        lbl.grid(row=row, column=0, padx=16, pady=(9, 2), sticky="ew")
        return lbl

    def _create_aligned_nav_item(self, key: str, icon: str, tr_key: str, row: int) -> None:
        """Crée une ligne de menu avec support d'image Glow en arrière-plan et 2 colonnes strictement alignées."""
        item_box = ctk.CTkLabel(
            self,
            text="",
            image=self._bg_idle,
            width=204,
            height=42,
            fg_color=BG_SIDEBAR,
            cursor="hand2",
        )
        item_box.grid(row=row, column=0, padx=8, pady=0)
        item_box.grid_propagate(False)
        item_box.grid_columnconfigure(0, minsize=40, weight=0)
        item_box.grid_columnconfigure(1, weight=1)
        item_box.grid_rowconfigure(0, weight=1)

        icon_lbl = ctk.CTkLabel(
            item_box,
            text=icon,
            width=26,
            height=24,
            fg_color=BG_SIDEBAR,
            font=ctk.CTkFont(size=13),
            text_color="#B1BAC4",
            anchor="center",
        )
        icon_lbl.grid(row=0, column=0, padx=(16, 2), pady=9)

        text_lbl = ctk.CTkLabel(
            item_box,
            text=_clean_label(tr(tr_key)),
            height=24,
            fg_color=BG_SIDEBAR,
            font=ctk.CTkFont(size=13),
            text_color="#B1BAC4",
            anchor="w",
        )
        text_lbl.grid(row=0, column=1, padx=(2, 14), pady=9, sticky="ew")

        for widget in (item_box, icon_lbl, text_lbl):
            widget.bind("<Button-1>", lambda _e, k=key: self.select_tab(k))
            widget.bind("<Enter>", lambda _e, k=key: self._on_hover(k, True))
            widget.bind("<Leave>", lambda _e, k=key: self._on_hover(k, False))

        self.nav_rows[key] = item_box
        self.nav_icons[key] = icon_lbl
        self.nav_labels[key] = (text_lbl, tr_key)

    def _on_hover(self, key: str, entering: bool) -> None:
        if key == self.active_key:
            return
        box = self.nav_rows.get(key)
        icon_lbl = self.nav_icons.get(key)
        text_lbl, _ = self.nav_labels[key]
        if not box or not icon_lbl:
            return
        inner_bg = BG_HOVER_INNER if entering else BG_SIDEBAR
        box.configure(image=self._bg_hover if entering else self._bg_idle)
        icon_lbl.configure(fg_color=inner_bg, text_color="#E6EDF3" if entering else "#B1BAC4")
        text_lbl.configure(fg_color=inner_bg, text_color="#E6EDF3" if entering else "#B1BAC4")

    def _build_footer(self) -> None:
        self.status_label = ctk.CTkLabel(
            self,
            text="📡 ...",
            font=ctk.CTkFont(size=11),
            text_color="#7D8590",
            anchor="w",
        )
        self.status_label.grid(row=16, column=0, padx=16, pady=(4, 4), sticky="ew")

        self.refresh_btn = ctk.CTkButton(
            self,
            text=tr("btn_refresh"),
            height=34,
            corner_radius=7,
            fg_color="#161E31",
            border_width=1,
            border_color="#2A3B5C",
            hover_color="#1F2D4A",
            text_color="#58A6FF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_refresh,
        )
        self.refresh_btn.grid(row=17, column=0, padx=12, pady=(0, 12), sticky="ew")

    def select_tab(self, active_key: str) -> None:
        self.active_key = active_key
        active_sec = self.nav_section_map.get(active_key, "home")

        # Illumine également l'en-tête de la catégorie active
        for sec_id, hdr_lbl in self.section_headers.items():
            hdr_lbl.configure(text_color="#58A6FF" if sec_id == active_sec else "#6E7681")

        for key, box in self.nav_rows.items():
            icon_lbl = self.nav_icons[key]
            text_lbl, _ = self.nav_labels[key]
            if key == active_key:
                box.configure(image=self._bg_active)
                icon_lbl.configure(fg_color=BG_ACTIVE_INNER, text_color="#79C0FF")
                text_lbl.configure(
                    fg_color=BG_ACTIVE_INNER,
                    text_color="#FFFFFF",
                    font=ctk.CTkFont(size=13, weight="bold"),
                )
            else:
                box.configure(image=self._bg_idle)
                icon_lbl.configure(fg_color=BG_SIDEBAR, text_color="#B1BAC4")
                text_lbl.configure(
                    fg_color=BG_SIDEBAR,
                    text_color="#B1BAC4",
                    font=ctk.CTkFont(size=13, weight="normal"),
                )
        self.on_navigate(active_key)

    def update_status(self, source_text: str) -> None:
        self.status_label.configure(text=f"📡 {source_text}")

    def update_language(self) -> None:
        self.role_lbl.configure(text=tr("creator_role"))
        self.sec_home_lbl.configure(text=tr("sec_home"))
        self.sec_inv_lbl.configure(text=tr("sec_inventory"))
        self.sec_cycles_lbl.configure(text=tr("sec_cycles"))
        self.refresh_btn.configure(text=tr("btn_refresh"))
        for key, (text_lbl, tr_key) in self.nav_labels.items():
            text_lbl.configure(text=_clean_label(tr(tr_key)))
