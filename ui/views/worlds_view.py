"""Module worlds_view : Vue centrale détaillée des Cycles des Mondes Ouverts."""

import customtkinter as ctk
from ui.components.cycle_card import CycleCard


class WorldsView(ctk.CTkFrame):
    """Page centrale affichant en grand les 4 cycles planétaires et leurs détails de farm."""

    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure((0, 1), weight=1, uniform="w_col")

        self.cards: dict[str, CycleCard] = {}
        self._build_header()
        self._build_cards()

    def _build_header(self) -> None:
        """En-tête de la vue Temps des Planètes."""
        title = ctk.CTkLabel(
            self,
            text="🌍  Temps des Planètes & Mondes Ouverts",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        title.grid(row=0, column=0, columnspan=2, padx=4, pady=(0, 4), sticky="ew")

        sub = ctk.CTkLabel(
            self,
            text="Suivi en temps réel des cycles Jour/Nuit, Chaud/Froid et Fass/Vome synchronisés avec Warframe.",
            font=ctk.CTkFont(size=13),
            text_color="#8B949E",
            anchor="w",
        )
        sub.grid(row=1, column=0, columnspan=2, padx=4, pady=(0, 16), sticky="ew")

    def _build_cards(self) -> None:
        """Crée 4 grandes CycleCards (mode non-compact) en réutilisant notre composant."""
        planets = [
            (
                "cetus",
                "🌍",
                "Terre — Plaines d'Eidolon (Cetus)",
                "100m Jour • 50m Nuit (Chasse aux Eidolons la nuit)",
                2,
                0,
            ),
            (
                "vallis",
                "🪐",
                "Vénus — Vallée Orbis (Fortuna)",
                "6m 40s Chaud • 20m Froid (Poissons rares selon la température)",
                2,
                1,
            ),
            (
                "cambion",
                "☄️",
                "Deimos — Puy de Cambion (Necralisk)",
                "100m Fass (Chaos) • 50m Vome (Ordre) — Nechramechs & Iso-Vaults",
                3,
                0,
            ),
            (
                "earth",
                "🌲",
                "Terre — Missions en Forêt (Cycle 4h)",
                "4h Jour • 4h Nuit (Plantes pour l'Apothicaire du Bosquet d'Argent)",
                3,
                1,
            ),
        ]

        for key, icon, title, subtitle, r, c in planets:
            card = CycleCard(self, icon=icon, title=title, subtitle=subtitle, compact=False)
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            self.cards[key] = card

    def load_state(self, world_state: dict, _duviri_state: dict) -> None:
        """Met à jour les états et les dates d'expiration des 4 planètes."""
        for key, card in self.cards.items():
            info = world_state.get(key, {})
            card.set_data(info.get("state", "..."), info.get("expiry", ""))

    def update_timers(self) -> None:
        """Rafraîchit les comptes à rebours chaque seconde."""
        for card in self.cards.values():
            card.refresh_timer()

