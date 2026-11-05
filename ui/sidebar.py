"""Module sidebar : Barre latérale gauche qui se déploie au survol et se range automatiquement."""

from pathlib import Path
from typing import Callable
import customtkinter as ctk
from PIL import Image
from core.i18n import tr

LOGO_PATH = Path(__file__).resolve().parent.parent / "data" / "app_logo.png"

EXPANDED_WIDTH = 225
COLLAPSED_WIDTH = 64

NAV_ITEMS_CONFIG = [
    ("welcome", "🏠", "nav_welcome", 2),
    ("notifications", "🔔", "nav_notifications", 3),
    ("resources", "💎", "nav_resources", 5),
    ("mods", "🃏", "nav_mods", 6),
    ("warframes", "🛡️", "nav_warframes", 7),
    ("worlds", "🌍", "nav_worlds", 9),
    ("bounties", "🎯", "nav_bounties", 10),
    ("duviri", "🌀", "nav_duviri", 11),
    ("baro", "💠", "nav_baro", 12),
]


def _clean_label(raw_text: str) -> str:
    parts = raw_text.split("   ", 1)
    return parts[1].strip() if len(parts) > 1 else raw_text.strip()


class Sidebar(ctk.CTkFrame):
    """Menu latéral auto-rétractable (mode icônes 64px hors survol, mode complet 225px au survol)."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Callable[[str], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__(master, width=COLLAPSED_WIDTH, corner_radius=0, fg_color="#0D111A")
        self.on_navigate = on_navigate
        self.on_refresh = on_refresh
        self.is_collapsed: bool = False
        self._last_source_text: str = "Live"

        self.nav_rows: dict[str, ctk.CTkFrame] = {}
        self.nav_labels: dict[str, tuple[ctk.CTkLabel, str]] = {}

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(15, weight=1)

        self._build_creator_badge()
        self._build_navigation()
        self._build_footer()
        self.set_collapsed(True)

    def _build_creator_badge(self) -> None:
        self.profile_box = ctk.CTkFrame(self, fg_color="transparent")
        self.profile_box.grid(row=0, column=0, padx=12, pady=(12, 8), sticky="ew")
        self.profile_box.grid_columnconfigure(1, weight=1)

        if LOGO_PATH.exists():
            pil_logo = Image.open(LOGO_PATH)
            ctk_logo = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(40, 40))
            self.emblem = ctk.CTkLabel(
                self.profile_box, text="", image=ctk_logo, width=40, height=40
            )
        else:
            self.emblem = ctk.CTkLabel(
                self.profile_box,
                text="❖",
                width=38,
                height=38,
                corner_radius=6,
                fg_color="#2A2415",
                text_color="#E5C158",
                font=ctk.CTkFont(size=20, weight="bold"),
            )
        self.emblem.grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="w")

        self.name_lbl = ctk.CTkLabel(
            self.profile_box,
            text="Nyxo_17",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        self.name_lbl.grid(row=0, column=1, sticky="ew")

        self.role_lbl = ctk.CTkLabel(
            self.profile_box,
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

        for key, icon, tr_key, row_idx in NAV_ITEMS_CONFIG:
            self._create_aligned_nav_item(key, icon, tr_key, row_idx)

    def _make_section_header(self, tr_key: str, row: int) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(
            self,
            text=tr(tr_key),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#6E7681",
            anchor="w",
        )
        lbl.grid(row=row, column=0, padx=16, pady=(10, 3), sticky="ew")
        return lbl

    def _create_aligned_nav_item(self, key: str, icon: str, tr_key: str, row: int) -> None:
        item_frame = ctk.CTkFrame(
            self,
            height=36,
            corner_radius=7,
            border_width=1,
            border_color="#0D111A",
            fg_color="transparent",
            cursor="hand2",
        )
        item_frame.grid(row=row, column=0, padx=10, pady=2, sticky="ew")
        item_frame.grid_propagate(False)
        item_frame.grid_columnconfigure(0, minsize=40, weight=0)
        item_frame.grid_columnconfigure(1, weight=1)
        item_frame.grid_rowconfigure(0, weight=1)

        icon_lbl = ctk.CTkLabel(
            item_frame,
            text=icon,
            width=36,
            font=ctk.CTkFont(size=14),
            text_color="#B1BAC4",
            anchor="center",
        )
        icon_lbl.grid(row=0, column=0, padx=(2, 2), sticky="ns")

        text_lbl = ctk.CTkLabel(
            item_frame,
            text=_clean_label(tr(tr_key)),
            font=ctk.CTkFont(size=13),
            text_color="#B1BAC4",
            anchor="w",
        )
        text_lbl.grid(row=0, column=1, padx=(2, 8), sticky="nsew")

        for widget in (item_frame, icon_lbl, text_lbl):
            widget.bind("<Button-1>", lambda _e, k=key: self.select_tab(k))
            widget.bind("<Enter>", lambda _e, k=key: self._on_hover(k, True))
            widget.bind("<Leave>", lambda _e, k=key: self._on_hover(k, False))

        self.nav_rows[key] = item_frame
        self.nav_labels[key] = (text_lbl, tr_key)

    def _on_hover(self, key: str, entering: bool) -> None:
        frame = self.nav_rows.get(key)
        if not frame or frame.cget("border_color") == "#3B82F6":
            return
        frame.configure(fg_color="#161E2E" if entering else "transparent")

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
        self.refresh_btn.grid(row=17, column=0, padx=10, pady=(0, 12), sticky="ew")

    def set_collapsed(self, collapsed: bool) -> None:
        """Range la colonne à gauche (64px) ou la déploie (225px) en masquant/affichant les textes."""
        if self.is_collapsed == collapsed:
            return
        self.is_collapsed = collapsed

        if collapsed:
            self.configure(width=COLLAPSED_WIDTH)
            self.name_lbl.grid_remove()
            self.role_lbl.grid_remove()
            self.sec_home_lbl.grid_remove()
            self.sec_inv_lbl.grid_remove()
            self.sec_cycles_lbl.grid_remove()
            self.status_label.grid_remove()
            self.refresh_btn.configure(text="🔄", width=42)
            for text_lbl, _ in self.nav_labels.values():
                text_lbl.grid_remove()
        else:
            self.configure(width=EXPANDED_WIDTH)
            self.name_lbl.grid()
            self.role_lbl.grid()
            self.sec_home_lbl.grid()
            self.sec_inv_lbl.grid()
            self.sec_cycles_lbl.grid()
            self.status_label.grid()
            self.refresh_btn.configure(text=tr("btn_refresh"))
            for text_lbl, _ in self.nav_labels.values():
                text_lbl.grid()

    def select_tab(self, active_key: str) -> None:
        for key, frame in self.nav_rows.items():
            text_lbl, _ = self.nav_labels[key]
            if key == active_key:
                frame.configure(fg_color="#17223B", border_color="#3B82F6")
                text_lbl.configure(
                    text_color="#FFFFFF", font=ctk.CTkFont(size=13, weight="bold")
                )
            else:
                frame.configure(fg_color="transparent", border_color="#0D111A")
                text_lbl.configure(
                    text_color="#B1BAC4", font=ctk.CTkFont(size=13, weight="normal")
                )
        self.on_navigate(active_key)

    def update_status(self, source_text: str) -> None:
        self._last_source_text = source_text
        self.status_label.configure(text=f"📡 {source_text}")

    def update_language(self) -> None:
        self.role_lbl.configure(text=tr("creator_role"))
        self.sec_home_lbl.configure(text=tr("sec_home"))
        self.sec_inv_lbl.configure(text=tr("sec_inventory"))
        self.sec_cycles_lbl.configure(text=tr("sec_cycles"))
        if not self.is_collapsed:
            self.refresh_btn.configure(text=tr("btn_refresh"))
        for key, (text_lbl, tr_key) in self.nav_labels.items():
            text_lbl.configure(text=_clean_label(tr(tr_key)))
