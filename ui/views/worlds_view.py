"""Module worlds_view : Vue centrale détaillée des Cycles des Mondes Ouverts bilingue FR/EN."""

import customtkinter as ctk
from core.i18n import tr
from ui.components.cycle_card import CycleCard


class WorldsView(ctk.CTkFrame):
    """Page centrale affichant en grand les 4 cycles planétaires."""

    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure((0, 1), weight=1, uniform="w_col")

        self.cards: dict[str, CycleCard] = {}
        self._build_header()
        self._build_cards()

    def _build_header(self) -> None:
        self.title_lbl = ctk.CTkLabel(
            self,
            text=tr("worlds_page_title"),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        self.title_lbl.grid(row=0, column=0, columnspan=2, padx=4, pady=(0, 4), sticky="ew")

        self.sub_lbl = ctk.CTkLabel(
            self,
            text=tr("worlds_page_sub"),
            font=ctk.CTkFont(size=13),
            text_color="#8B949E",
            anchor="w",
        )
        self.sub_lbl.grid(row=1, column=0, columnspan=2, padx=4, pady=(0, 16), sticky="ew")

    def _build_cards(self) -> None:
        planets = [
            ("cetus", "🌍", "w_cetus_long", "w_cetus_desc", 2, 0),
            ("vallis", "🪐", "w_vallis_long", "w_vallis_desc", 2, 1),
            ("cambion", "☄️", "w_cambion_long", "w_cambion_desc", 3, 0),
            ("earth", "🌲", "w_earth_long", "w_earth_desc", 3, 1),
        ]

        for key, icon, t_key, s_key, r, c in planets:
            card = CycleCard(self, icon=icon, title_key=t_key, sub_key=s_key, compact=False)
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            self.cards[key] = card

    def load_state(self, world_state: dict, _duviri_state: dict) -> None:
        for key, card in self.cards.items():
            info = world_state.get(key, {})
            card.set_data(info.get("state", "..."), info.get("expiry", ""))

    def update_language(self) -> None:
        """Traduit la page Temps des Planètes et ses 4 cartes en FR ou EN."""
        self.title_lbl.configure(text=tr("worlds_page_title"))
        self.sub_lbl.configure(text=tr("worlds_page_sub"))
        for card in self.cards.values():
            card.update_language()

    def update_timers(self) -> None:
        for card in self.cards.values():
            card.refresh_timer()
