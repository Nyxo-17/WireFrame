"""Module live_panel : Panneau latéral droit 'Cycles & Événements En direct'."""

import customtkinter as ctk
from core.timer_engine import get_formatted_timer
from ui.components.cycle_card import CycleCard


class LivePanel(ctk.CTkFrame):
    """Colonne de droite affichant en permanence les Cycles des Mondes, Duviri et Baro."""

    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(
            master,
            width=320,
            corner_radius=10,
            fg_color="#0F1420",
            border_width=1,
            border_color="#1E2738",
        )
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self.duviri_expiry: str = ""
        self.baro_target_iso: str = ""
        self.world_cards: dict[str, CycleCard] = {}

        self._build_header()
        self._build_worlds_grid()
        self._build_duviri_section()
        self._build_baro_card()

    def _build_header(self) -> None:
        """Bandeau supérieur [ ● Cycles & Événements ] | [ En direct ]."""
        header = ctk.CTkFrame(self, fg_color="#141A29", corner_radius=8, height=36)
        header.grid(row=0, column=0, padx=12, pady=(12, 10), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        badge = ctk.CTkLabel(
            header,
            text="  ● Cycles & Événements",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#F0F6FC",
        )
        badge.grid(row=0, column=0, padx=8, pady=6, sticky="w")

        self.live_lbl = ctk.CTkLabel(
            header,
            text="📡 En direct",
            font=ctk.CTkFont(size=11),
            text_color="#8A94A6",
        )
        self.live_lbl.grid(row=0, column=1, padx=10, pady=6, sticky="e")

    def _build_worlds_grid(self) -> None:
        """Grille 2x2 des 4 Cycles des Mondes utilisant notre composant CycleCard."""
        sec_title = ctk.CTkLabel(
            self,
            text="Cycles des Mondes",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#D0D7DE",
        )
        sec_title.grid(row=1, column=0, padx=14, pady=(2, 6), sticky="w")

        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
        grid_frame.grid_columnconfigure((0, 1), weight=1, uniform="world_col")

        specs = [
            ("cetus", "🌍", "Terre (Cetus)", "Cycle Cetus", 0, 0),
            ("vallis", "🪐", "Orb Vallis", "Vénus", 0, 1),
            ("cambion", "☄️", "Cambion Drift", "Deimos", 1, 0),
            ("earth", "🌲", "Terre (Forêts)", "Cycle 4h", 1, 1),
        ]
        for key, icon, title, sub, r, c in specs:
            card = CycleCard(grid_frame, icon=icon, title=title, subtitle=sub, compact=True)
            card.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
            self.world_cards[key] = card

    def _build_duviri_section(self) -> None:
        """Section 'Le Circuit // Duviri' (Incarnon Acier + Warframes Circuit)."""
        sec_title = ctk.CTkLabel(
            self,
            text="Le Circuit // Duviri",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#D0D7DE",
        )
        sec_title.grid(row=3, column=0, padx=14, pady=(4, 6), sticky="w")

        # Carte 1 : Incarnon (Acier)
        self.inc_card, self.inc_timer, self.inc_cur, self.inc_next = self._make_duviri_box(
            row=4, title="⚔️  Incarnon (Acier)"
        )
        # Carte 2 : Warframes (Circuit)
        self.wf_card, self.wf_timer, self.wf_cur, self.wf_next = self._make_duviri_box(
            row=5, title="🛡️  Warframes (Circuit)"
        )

    def _make_duviri_box(self, row: int, title: str) -> tuple:
        """Crée une boîte Duviri avec Titre, Timer vert, ligne Actuel et ligne Suivant."""
        box = ctk.CTkFrame(
            self, corner_radius=8, fg_color="#141A29", border_width=1, border_color="#232F46"
        )
        box.grid(row=row, column=0, padx=12, pady=4, sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(box, fg_color="transparent")
        top.grid(row=0, column=0, padx=10, pady=(8, 2), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top, text=title, font=ctk.CTkFont(size=12, weight="bold"), text_color="#60A5FA"
        ).grid(row=0, column=0, sticky="w")

        timer_lbl = ctk.CTkLabel(
            top, text="3j 8h", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4ADE80"
        )
        timer_lbl.grid(row=0, column=1, sticky="e")

        cur_lbl = ctk.CTkLabel(
            box, text="Actuel : ...", font=ctk.CTkFont(size=12, weight="bold"), text_color="#F0F6FC", anchor="w"
        )
        cur_lbl.grid(row=1, column=0, padx=10, pady=1, sticky="ew")

        nxt_lbl = ctk.CTkLabel(
            box, text="Suivant : ...", font=ctk.CTkFont(size=11), text_color="#7D8590", anchor="w"
        )
        nxt_lbl.grid(row=2, column=0, padx=10, pady=(0, 8), sticky="ew")
        return box, timer_lbl, cur_lbl, nxt_lbl

    def _build_baro_card(self) -> None:
        """Carte résumée pour Baro Ki'Teer en bas du panneau."""
        box = ctk.CTkFrame(
            self, corner_radius=8, fg_color="#141A29", border_width=1, border_color="#232F46"
        )
        box.grid(row=6, column=0, padx=12, pady=(8, 12), sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(box, fg_color="transparent")
        top.grid(row=0, column=0, padx=10, pady=(8, 2), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top, text="💎  Baro Ki'Teer (Néant)", font=ctk.CTkFont(size=12, weight="bold"), text_color="#60A5FA"
        ).grid(row=0, column=0, sticky="w")

        self.baro_timer = ctk.CTkLabel(
            top, text="--j --h", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4ADE80"
        )
        self.baro_timer.grid(row=0, column=1, sticky="e")

        self.baro_info = ctk.CTkLabel(
            box, text="Relais : ...", font=ctk.CTkFont(size=12, weight="bold"), text_color="#F0F6FC", anchor="w"
        )
        self.baro_info.grid(row=1, column=0, padx=10, pady=(1, 8), sticky="ew")

    def load_state(self, world_state: dict, duviri_state: dict) -> None:
        """Alimente toutes les cartes du panneau droit avec les données fraîches."""
        for key, card in self.world_cards.items():
            info = world_state.get(key, {})
            card.set_data(info.get("state", "..."), info.get("expiry", ""))

        self.duviri_expiry = duviri_state.get("expiry", "")
        inc_now = ", ".join(duviri_state.get("incarnon_weapons", []))
        inc_nxt = ", ".join(duviri_state.get("next_incarnon_weapons", []))
        wf_now = " • ".join(duviri_state.get("warframes", []))
        wf_nxt = " • ".join(duviri_state.get("next_warframes", []))

        self.inc_cur.configure(text=f"Actuel : {inc_now}")
        self.inc_next.configure(text=f"Suivant : {inc_nxt}")
        self.wf_cur.configure(text=f"Actuel : {wf_now}")
        self.wf_next.configure(text=f"Suivant : {wf_nxt}")

        baro = world_state.get("baro", {})
        is_here = baro.get("active", False)
        self.baro_target_iso = baro.get("expiry", "") if is_here else baro.get("activation", "")
        status_prefix = "Présent" if is_here else "Arrive"
        self.baro_info.configure(text=f"{status_prefix} ➔ {baro.get('location', 'Relais')}")
        self.update_timers()

    def update_timers(self) -> None:
        """Rafraîchit tous les timers du panneau droit chaque seconde."""
        for card in self.world_cards.values():
            card.refresh_timer()

        duv_txt = get_formatted_timer(self.duviri_expiry, short=True)
        self.inc_timer.configure(text=duv_txt)
        self.wf_timer.configure(text=duv_txt)
        self.baro_timer.configure(text=get_formatted_timer(self.baro_target_iso, short=True))
