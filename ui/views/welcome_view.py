"""Module welcome_view : Page centrale d'accueil avec grille des 6 fonctionnalités."""

from typing import Callable
import customtkinter as ctk
from core.i18n import tr


class WelcomeView(ctk.CTkFrame):
    """Vue d'accueil présentant la bannière et la grille 2x3 des cartes de navigation."""

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
        self.page_title.grid(row=0, column=0, padx=4, pady=(0, 8), sticky="ew")

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
        banner.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        banner.grid_columnconfigure(0, weight=1)

        self.banner_title = ctk.CTkLabel(
            banner,
            text=tr("welcome_banner_title"),
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="#FFFFFF",
        )
        self.banner_title.grid(row=0, column=0, padx=20, pady=(12, 4))

        self.banner_desc = ctk.CTkLabel(
            banner,
            text=tr("welcome_banner_desc"),
            font=ctk.CTkFont(size=12),
            text_color="#8B949E",
            justify="center",
        )
        self.banner_desc.grid(row=1, column=0, padx=20, pady=(0, 12))

    def _build_feature_cards(self) -> None:
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.grid(row=2, column=0, sticky="nsew")
        grid.grid_columnconfigure((0, 1), weight=1, uniform="feat_col")

        cards_data = [
            ("card_res_title", "card_res_desc", "resources", 0, 0),
            ("card_mod_title", "card_mod_desc", "mods", 0, 1),
            ("card_wf_title", "card_wf_desc", "warframes", 1, 0),
            ("card_wld_title", "card_wld_desc", "worlds", 1, 1),
            ("card_bnt_title", "card_bnt_desc", "bounties", 2, 0),
            ("card_duv_title", "card_duv_desc", "notifications", 2, 1),
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
        card.grid(row=r, column=c, padx=5, pady=5, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, padx=12, pady=(10, 4), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        title_lbl = ctk.CTkLabel(
            top,
            text=tr(t_key),
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#58A6FF",
            anchor="w",
        )
        title_lbl.grid(row=0, column=0, sticky="w")

        open_btn = ctk.CTkButton(
            top,
            text=tr("open_btn"),
            width=72,
            height=24,
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
            font=ctk.CTkFont(size=11),
            text_color="#8B949E",
            justify="left",
            anchor="w",
            wraplength=265,
        )
        desc_lbl.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")
        self.card_widgets.append((title_lbl, desc_lbl, open_btn, t_key, d_key))

    def _build_signature(self) -> None:
        sig_frame = ctk.CTkFrame(self, fg_color="transparent")
        sig_frame.grid(row=3, column=0, pady=(4, 0), sticky="e")

        self.created_lbl = ctk.CTkLabel(
            sig_frame,
            text=tr("created_by"),
            font=ctk.CTkFont(size=13),
            text_color="#7D8590",
        )
        self.created_lbl.grid(row=0, column=0)

        self.author_lbl = ctk.CTkLabel(
            sig_frame,
            text="Nyxo_17",
            font=ctk.CTkFont(size=14, weight="bold", slant="italic"),
            text_color="#F0F6FC",
        )
        self.author_lbl.grid(row=0, column=1)

    def update_language(self) -> None:
        self.page_title.configure(text=tr("welcome_page_title"))
        self.banner_title.configure(text=tr("welcome_banner_title"))
        self.banner_desc.configure(text=tr("welcome_banner_desc"))
        self.created_lbl.configure(text=tr("created_by"))
        for title_lbl, desc_lbl, open_btn, t_key, d_key in self.card_widgets:
            title_lbl.configure(text=tr(t_key))
            desc_lbl.configure(text=tr(d_key))
            open_btn.configure(text=tr("open_btn"))

    def apply_zoom(self, scale: float) -> None:
        self.page_title.configure(font=ctk.CTkFont(size=int(22 * scale), weight="bold"))
        self.banner_title.configure(font=ctk.CTkFont(size=int(19 * scale), weight="bold"))
        self.banner_desc.configure(font=ctk.CTkFont(size=int(12 * scale)))
        self.created_lbl.configure(font=ctk.CTkFont(size=int(13 * scale)))
        self.author_lbl.configure(font=ctk.CTkFont(size=int(14 * scale), weight="bold", slant="italic"))
        for title_lbl, desc_lbl, open_btn, _, _ in self.card_widgets:
            title_lbl.configure(font=ctk.CTkFont(size=int(13 * scale), weight="bold"))
            desc_lbl.configure(font=ctk.CTkFont(size=int(11 * scale)), wraplength=int(265 * scale))
            open_btn.configure(font=ctk.CTkFont(size=int(12 * scale), weight="bold"))
