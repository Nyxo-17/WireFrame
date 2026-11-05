"""Module sidebar : Barre latérale gauche fixe avec icônes/textes alignés et double anneau Neon Glow."""

from pathlib import Path
from typing import Callable
import customtkinter as ctk
from PIL import Image
from core.i18n import tr
from core.updater import get_local_version

LOGO_PATH = Path(__file__).resolve().parent.parent / "data" / "app_logo.png"

BG_SIDEBAR = "#0D111A"

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


class Sidebar(ctk.CTkFrame):
    """Menu latéral fixe avec alignement strict des textes et effet Neon Glow sur l'onglet actif."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Callable[[str], None],
        on_refresh: Callable[[], None],
        on_check_update: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(master, width=220, corner_radius=0, fg_color=BG_SIDEBAR)
        self.on_navigate = on_navigate
        self.on_refresh = on_refresh
        self.on_check_update = on_check_update
        self.active_key: str = "welcome"

        self.nav_outer_glows: dict[str, ctk.CTkFrame] = {}
        self.nav_rows: dict[str, ctk.CTkFrame] = {}
        self.nav_pills: dict[str, ctk.CTkFrame] = {}
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
        """Crée un bouton avec anneau externe Halo Glow + cadre interne Néon + barre lumineuse + Icône & Texte."""
        # 1. Anneau externe (Halo diffus autour du bouton actif)
        glow_outer = ctk.CTkFrame(
            self,
            height=40,
            corner_radius=10,
            border_width=2,
            border_color=BG_SIDEBAR,
            fg_color="transparent",
        )
        glow_outer.grid(row=row, column=0, padx=9, pady=1, sticky="ew")
        glow_outer.grid_propagate(False)
        glow_outer.grid_columnconfigure(0, weight=1)
        glow_outer.grid_rowconfigure(0, weight=1)

        # 2. Cadre interne du bouton (Néon lumineux quand sélectionné)
        item_frame = ctk.CTkFrame(
            glow_outer,
            height=34,
            corner_radius=8,
            border_width=2,
            border_color=BG_SIDEBAR,
            fg_color="transparent",
            cursor="hand2",
        )
        item_frame.grid(row=0, column=0, padx=2, pady=2, sticky="nsew")
        item_frame.grid_propagate(False)
        item_frame.grid_columnconfigure(0, minsize=8, weight=0)
        item_frame.grid_columnconfigure(1, minsize=30, weight=0)
        item_frame.grid_columnconfigure(2, weight=1)
        item_frame.grid_rowconfigure(0, weight=1)

        # 3. Barre verticale néon à gauche
        pill = ctk.CTkFrame(
            item_frame,
            width=4,
            height=18,
            corner_radius=2,
            fg_color=BG_SIDEBAR,
        )
        pill.grid(row=0, column=0, padx=(5, 1), pady=7)

        # 4. Icône alignée (pady=4 pour ne jamais couper la bordure)
        icon_lbl = ctk.CTkLabel(
            item_frame,
            text=icon,
            width=26,
            height=24,
            font=ctk.CTkFont(size=13),
            text_color="#B1BAC4",
            anchor="center",
        )
        icon_lbl.grid(row=0, column=1, padx=(2, 2), pady=4)

        # 5. Texte aligné (pady=4 pour garder la bordure supérieure/inférieure intacte)
        text_lbl = ctk.CTkLabel(
            item_frame,
            text=_clean_label(tr(tr_key)),
            height=24,
            font=ctk.CTkFont(size=13),
            text_color="#B1BAC4",
            anchor="w",
        )
        text_lbl.grid(row=0, column=2, padx=(4, 8), pady=4, sticky="ew")

        for widget in (glow_outer, item_frame, pill, icon_lbl, text_lbl):
            widget.bind("<Button-1>", lambda _e, k=key: self.select_tab(k))
            widget.bind("<Enter>", lambda _e, k=key: self._on_hover(k, True))
            widget.bind("<Leave>", lambda _e, k=key: self._on_hover(k, False))

        self.nav_outer_glows[key] = glow_outer
        self.nav_rows[key] = item_frame
        self.nav_pills[key] = pill
        self.nav_icons[key] = icon_lbl
        self.nav_labels[key] = (text_lbl, tr_key)

    def _on_hover(self, key: str, entering: bool) -> None:
        if key == self.active_key:
            return
        outer = self.nav_outer_glows.get(key)
        frame = self.nav_rows.get(key)
        pill = self.nav_pills.get(key)
        icon_lbl = self.nav_icons.get(key)
        text_lbl, _ = self.nav_labels[key]
        if not frame or not outer or not pill or not icon_lbl:
            return
        if entering:
            outer.configure(fg_color="#101829", border_color="#192845")
            frame.configure(fg_color="#162035", border_color="#2A4374")
            pill.configure(fg_color="#3B82F6")
            icon_lbl.configure(text_color="#E6EDF3")
            text_lbl.configure(text_color="#E6EDF3")
        else:
            outer.configure(fg_color="transparent", border_color=BG_SIDEBAR)
            frame.configure(fg_color="transparent", border_color=BG_SIDEBAR)
            pill.configure(fg_color=BG_SIDEBAR)
            icon_lbl.configure(text_color="#B1BAC4")
            text_lbl.configure(text_color="#B1BAC4")

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
            height=32,
            corner_radius=7,
            fg_color="#161E31",
            border_width=1,
            border_color="#2A3B5C",
            hover_color="#1F2D4A",
            text_color="#58A6FF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_refresh,
        )
        self.refresh_btn.grid(row=17, column=0, padx=12, pady=(0, 6), sticky="ew")

        v_str = get_local_version()
        self.update_btn = ctk.CTkButton(
            self,
            text=f"{tr('btn_check_update')} (v{v_str})",
            height=28,
            corner_radius=7,
            fg_color="#131926",
            border_width=1,
            border_color="#232F46",
            hover_color="#1D2B44",
            text_color="#8B949E",
            font=ctk.CTkFont(size=11),
            command=self.on_check_update if self.on_check_update else lambda: None,
        )
        self.update_btn.grid(row=18, column=0, padx=12, pady=(0, 10), sticky="ew")

    def select_tab(self, active_key: str) -> None:
        self.active_key = active_key
        active_sec = self.nav_section_map.get(active_key, "home")

        # Illumine l'en-tête de la catégorie active
        for sec_id, hdr_lbl in self.section_headers.items():
            hdr_lbl.configure(text_color="#58A6FF" if sec_id == active_sec else "#6E7681")

        for key, frame in self.nav_rows.items():
            outer = self.nav_outer_glows[key]
            pill = self.nav_pills[key]
            icon_lbl = self.nav_icons[key]
            text_lbl, _ = self.nav_labels[key]
            if key == active_key:
                # Double anneau lumineux (Halo externe bleu + Coeur néon cyan)
                outer.configure(fg_color="#132347", border_color="#2563EB")
                frame.configure(fg_color="#1B3160", border_color="#79C0FF")
                pill.configure(fg_color="#BAE6FD")
                icon_lbl.configure(text_color="#79C0FF")
                text_lbl.configure(
                    text_color="#FFFFFF",
                    font=ctk.CTkFont(size=13, weight="bold"),
                )
            else:
                outer.configure(fg_color="transparent", border_color=BG_SIDEBAR)
                frame.configure(fg_color="transparent", border_color=BG_SIDEBAR)
                pill.configure(fg_color=BG_SIDEBAR)
                icon_lbl.configure(text_color="#B1BAC4")
                text_lbl.configure(
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
        self.update_btn.configure(text=f"{tr('btn_check_update')} (v{get_local_version()})")
        for key, (text_lbl, tr_key) in self.nav_labels.items():
            text_lbl.configure(text=_clean_label(tr(tr_key)))
