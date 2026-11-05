"""Module welcome_view : Page centrale d'accueil bilingue FR/EN."""

from typing import Callable
import customtkinter as ctk
from core.i18n import tr


class WelcomeView(ctk.CTkFrame):
    """Vue d'accueil présentant la bannière et la grille de cartes de navigation rapide."""

    def __init__(self, master: ctk.CTkBaseClass, on_navigate: Callable[[str], None]) -> None:
        super().__init__(master, fg_color="transparent")
        self.on_navigate = on_navigate
        self.card_widgets: list[tuple[ctk.CTkLabel, ctk.CTkLabel, ctk.CTkButton, str, str]] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.page_title = ctk.CTkLabel(
            self,
            text=tr("welcome_page_title"),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        self.page_title.grid(row=0, column=0, padx=4, pady=(0, 12), sticky="ew")

        self._build_hero_banner()
        self._build_feature_cards()
        self._build_signature()

    def _build_hero_banner(self) -> None:
        banner = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color="#131B2E",
            border_width=1,
            border_color="#23304C",
        )
        banner.grid(row=1, column=0, pady=(0, 14), sticky="ew")
        banner.grid_columnconfigure(0, weight=1)

        self.banner_title = ctk.CTkLabel(
            banner,
            text=tr("welcome_banner_title"),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF",
        )
        self.banner_title.grid(row=0, column=0, padx=20, pady=(16, 6))

        self.banner_desc = ctk.CTkLabel(
            banner,
            text=tr("welcome_banner_desc"),
            font=ctk.CTkFont(size=12),
            text_color="#8B949E",
            justify="center",
        )
        self.banner_desc.grid(row=1, column=0, padx=20, pady=(0, 16))

    def _build_feature_cards(self) -> None:
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.grid(row=2, column=0, sticky="nsew")
        grid.grid_columnconfigure((0, 1), weight=1, uniform="feat_col")

        cards_data = [
            ("card1_title", "card1_desc", "worlds", 0, 0),
            ("card2_title", "card2_desc", "duviri", 0, 1),
            ("card3_title", "card3_desc", "duviri", 1, 0),
            ("card4_title", "card4_desc", "baro", 1, 1),
        ]

        for t_key, d_key, target_key, r, c in cards_data:
            self._make_card(grid, t_key, d_key, target_key, r, c)

    def _make_card(
        self, parent: ctk.CTkFrame, t_key: str, d_key: str, target_key: str, r: int, c: int
    ) -> None:
        card = ctk.CTkFrame(
            parent,
            corner_radius=10,
            fg_color="#121826",
            border_width=1,
            border_color="#212C42",
        )
        card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, padx=14, pady=(14, 6), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        title_lbl = ctk.CTkLabel(
            top,
            text=tr(t_key),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#58A6FF",
            anchor="w",
        )
        title_lbl.grid(row=0, column=0, sticky="w")

        open_btn = ctk.CTkButton(
            top,
            text=tr("open_btn"),
            width=76,
            height=26,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#1C273E",
            text_color="#D0D7DE",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda k=target_key: self.on_navigate(k),
        )
        open_btn.grid(row=0, column=1, sticky="e")

        desc_lbl = ctk.CTkLabel(
            card,
            text=tr(d_key),
            font=ctk.CTkFont(size=12),
            text_color="#8B949E",
            justify="left",
            anchor="w",
            wraplength=260,
        )
        desc_lbl.grid(row=1, column=0, padx=14, pady=(0, 16), sticky="ew")
        self.card_widgets.append((title_lbl, desc_lbl, open_btn, t_key, d_key))

    def _build_signature(self) -> None:
        sig_frame = ctk.CTkFrame(self, fg_color="transparent")
        sig_frame.grid(row=3, column=0, pady=(8, 0), sticky="e")

        self.created_lbl = ctk.CTkLabel(
            sig_frame,
            text=tr("created_by"),
            font=ctk.CTkFont(size=13),
            text_color="#7D8590",
        )
        self.created_lbl.grid(row=0, column=0)

        ctk.CTkLabel(
            sig_frame,
            text="Nyxo_17",
            font=ctk.CTkFont(size=14, weight="bold", slant="italic"),
            text_color="#F0F6FC",
        ).grid(row=0, column=1)

    def update_language(self) -> None:
        """Traduit tous les textes de la page Bienvenue en FR ou EN."""
        self.page_title.configure(text=tr("welcome_page_title"))
        self.banner_title.configure(text=tr("welcome_banner_title"))
        self.banner_desc.configure(text=tr("welcome_banner_desc"))
        self.created_lbl.configure(text=tr("created_by"))
        for title_lbl, desc_lbl, open_btn, t_key, d_key in self.card_widgets:
            title_lbl.configure(text=tr(t_key))
            desc_lbl.configure(text=tr(d_key))
            open_btn.configure(text=tr("open_btn"))
