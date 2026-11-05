"""Module sidebar : Barre latérale gauche bilingue FR/EN au style 'WireFrame by Nyxo_17'."""

from typing import Callable
import customtkinter as ctk
from core.i18n import tr


class Sidebar(ctk.CTkFrame):
    """Menu latéral contenant l'en-tête créateur Nyxo_17 et les sections de navigation."""

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
            "worlds": "nav_worlds",
            "duviri": "nav_duviri",
            "baro": "nav_baro",
        }

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(10, weight=1)

        self._build_creator_badge()
        self._build_navigation()
        self._build_footer()

    def _build_creator_badge(self) -> None:
        """Affiche l'encart 'Nyxo_17 - Créateur de WireFrame' en haut à gauche."""
        profile_box = ctk.CTkFrame(self, fg_color="transparent")
        profile_box.grid(row=0, column=0, padx=14, pady=(14, 12), sticky="ew")

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
        """Construit les catégories et boutons de navigation."""
        self.sec_home_lbl = ctk.CTkLabel(
            self,
            text=tr("sec_home"),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#6E7681",
            anchor="w",
        )
        self.sec_home_lbl.grid(row=1, column=0, padx=18, pady=(10, 4), sticky="ew")
        self._create_nav_btn("welcome", tr("nav_welcome"), row=2)

        self.sec_cycles_lbl = ctk.CTkLabel(
            self,
            text=tr("sec_cycles"),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#6E7681",
            anchor="w",
        )
        self.sec_cycles_lbl.grid(row=3, column=0, padx=18, pady=(12, 4), sticky="ew")

        for key, row_idx in [("worlds", 4), ("duviri", 5), ("baro", 6)]:
            self._create_nav_btn(key, tr(self.nav_keys_map[key]), row=row_idx)

    def _create_nav_btn(self, key: str, text: str, row: int) -> None:
        btn = ctk.CTkButton(
            self,
            text=text,
            anchor="w",
            height=38,
            corner_radius=7,
            border_width=1,
            border_color="#0D111A",
            fg_color="transparent",
            text_color="#B1BAC4",
            hover_color="#161E2E",
            font=ctk.CTkFont(size=13),
            command=lambda k=key: self.select_tab(k),
        )
        btn.grid(row=row, column=0, padx=12, pady=3, sticky="ew")
        self.nav_buttons[key] = btn

    def _build_footer(self) -> None:
        self.status_label = ctk.CTkLabel(
            self,
            text="📡 ...",
            font=ctk.CTkFont(size=11),
            text_color="#7D8590",
            anchor="w",
        )
        self.status_label.grid(row=11, column=0, padx=16, pady=(4, 6), sticky="ew")

        self.refresh_btn = ctk.CTkButton(
            self,
            text=tr("btn_refresh"),
            height=36,
            corner_radius=7,
            fg_color="#161E31",
            border_width=1,
            border_color="#2A3B5C",
            hover_color="#1F2D4A",
            text_color="#58A6FF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_refresh,
        )
        self.refresh_btn.grid(row=12, column=0, padx=12, pady=(0, 14), sticky="ew")

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
        """Met à jour tous les textes de la barre latérale lors du changement FR/EN."""
        self.role_lbl.configure(text=tr("creator_role"))
        self.sec_home_lbl.configure(text=tr("sec_home"))
        self.sec_cycles_lbl.configure(text=tr("sec_cycles"))
        self.refresh_btn.configure(text=tr("btn_refresh"))
        for key, btn in self.nav_buttons.items():
            btn.configure(text=tr(self.nav_keys_map[key]))
