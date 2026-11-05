"""Module sidebar : Barre latérale gauche complète avec Notifications, Inventaire & Cycles."""

from typing import Callable
import customtkinter as ctk
from core.i18n import tr


class Sidebar(ctk.CTkFrame):
    """Menu latéral contenant l'en-tête Nyxo_17, Accueil, Notifications, Inventaire et Cycles."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Callable[[str], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__(master, width=220, corner_radius=0, fg_color="#0D111A")
        self.on_navigate = on_navigate
        self.on_refresh = on_refresh
        self.nav_buttons: dict[str, ctk.CTkButton] = {}
        self.nav_keys_map = {
            "welcome": "nav_welcome",
            "notifications": "nav_notifications",
            "resources": "nav_resources",
            "mods": "nav_mods",
            "warframes": "nav_warframes",
            "worlds": "nav_worlds",
            "bounties": "nav_bounties",
            "duviri": "nav_duviri",
            "baro": "nav_baro",
        }

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(15, weight=1)

        self._build_creator_badge()
        self._build_navigation()
        self._build_footer()

    def _build_creator_badge(self) -> None:
        profile_box = ctk.CTkFrame(self, fg_color="transparent")
        profile_box.grid(row=0, column=0, padx=14, pady=(12, 6), sticky="ew")

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
        emblem.grid(row=0, column=0, rowspan=2, padx=(0, 10))

        ctk.CTkLabel(
            profile_box,
            text="Nyxo_17",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        self.role_lbl = ctk.CTkLabel(
            profile_box,
            text=tr("creator_role"),
            font=ctk.CTkFont(size=11),
            text_color="#7D8590",
            anchor="w",
        )
        self.role_lbl.grid(row=1, column=1, sticky="w")

    def _build_navigation(self) -> None:
        self.sec_home_lbl = self._make_section_header("sec_home", row=1)
        self._create_nav_btn("welcome", row=2)
        self._create_nav_btn("notifications", row=3)

        self.sec_inv_lbl = self._make_section_header("sec_inventory", row=4)
        for key, row_idx in [("resources", 5), ("mods", 6), ("warframes", 7)]:
            self._create_nav_btn(key, row=row_idx)

        self.sec_cycles_lbl = self._make_section_header("sec_cycles", row=8)
        for key, row_idx in [("worlds", 9), ("bounties", 10), ("duviri", 11), ("baro", 12)]:
            self._create_nav_btn(key, row=row_idx)

    def _make_section_header(self, tr_key: str, row: int) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(
            self,
            text=tr(tr_key),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#6E7681",
            anchor="w",
        )
        lbl.grid(row=row, column=0, padx=18, pady=(8, 2), sticky="ew")
        return lbl

    def _create_nav_btn(self, key: str, row: int) -> None:
        btn = ctk.CTkButton(
            self,
            text=tr(self.nav_keys_map[key]),
            anchor="w",
            height=33,
            corner_radius=7,
            border_width=1,
            border_color="#0D111A",
            fg_color="transparent",
            text_color="#B1BAC4",
            hover_color="#161E2E",
            font=ctk.CTkFont(size=13),
            command=lambda k=key: self.select_tab(k),
        )
        btn.grid(row=row, column=0, padx=12, pady=2, sticky="ew")
        self.nav_buttons[key] = btn

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
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color="#17223B", border_color="#3B82F6", text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", border_color="#0D111A", text_color="#B1BAC4")
        self.on_navigate(active_key)

    def update_status(self, source_text: str) -> None:
        self.status_label.configure(text=f"📡 {source_text}")

    def update_language(self) -> None:
        self.role_lbl.configure(text=tr("creator_role"))
        self.sec_home_lbl.configure(text=tr("sec_home"))
        self.sec_inv_lbl.configure(text=tr("sec_inventory"))
        self.sec_cycles_lbl.configure(text=tr("sec_cycles"))
        self.refresh_btn.configure(text=tr("btn_refresh"))
        for key, btn in self.nav_buttons.items():
            btn.configure(text=tr(self.nav_keys_map[key]))
