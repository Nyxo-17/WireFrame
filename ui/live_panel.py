"""Module live_panel : Panneau latéral droit 'Cycles & Événements En direct' complet."""

import customtkinter as ctk
from core.codex_service import get_current_bounty_rotation
from core.i18n import tr
from core.timer_engine import get_formatted_timer
from ui.components.cycle_card import CycleCard


class LivePanel(ctk.CTkFrame):
    """Colonne de droite affichant les Cycles des Mondes, Duviri, Mises à Prix et Baro."""

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
        self.bounty_expiry: str = ""
        self.baro_target_iso: str = ""
        self.last_world_state: dict = {}
        self.last_duviri_state: dict = {}
        self.world_cards: dict[str, CycleCard] = {}

        self._build_header()
        self._build_worlds_grid()
        self._build_duviri_section()
        self._build_bounty_card()
        self._build_baro_card()

    def _build_header(self) -> None:
        header = ctk.CTkFrame(self, fg_color="#141A29", corner_radius=8, height=34)
        header.grid(row=0, column=0, padx=12, pady=(10, 8), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        self.badge_lbl = ctk.CTkLabel(
            header, text=tr("live_badge"), font=ctk.CTkFont(size=12, weight="bold"), text_color="#F0F6FC"
        )
        self.badge_lbl.grid(row=0, column=0, padx=8, pady=5, sticky="w")

        self.live_lbl = ctk.CTkLabel(
            header, text=tr("live_tag"), font=ctk.CTkFont(size=11), text_color="#8A94A6"
        )
        self.live_lbl.grid(row=0, column=1, padx=10, pady=5, sticky="e")

    def _build_worlds_grid(self) -> None:
        self.worlds_sec_lbl = ctk.CTkLabel(
            self, text=tr("live_worlds_title"), font=ctk.CTkFont(size=13, weight="bold"), text_color="#D0D7DE"
        )
        self.worlds_sec_lbl.grid(row=1, column=0, padx=14, pady=(0, 4), sticky="w")

        grid_frame = ctk.CTkFrame(self, fg_color="transparent")
        grid_frame.grid(row=2, column=0, padx=10, pady=(0, 6), sticky="ew")
        grid_frame.grid_columnconfigure((0, 1), weight=1, uniform="world_col")

        specs = [
            ("cetus", "🌍", "w_cetus_short", "w_cetus_sub", 0, 0, "earth.png"),
            ("vallis", "🪐", "w_vallis_short", "w_vallis_sub", 0, 1, "venus.png"),
            ("cambion", "☄️", "w_cambion_short", "w_cambion_sub", 1, 0, "deimos.png"),
            ("earth", "🌲", "w_earth_short", "w_earth_sub", 1, 1, "earth.png"),
        ]
        for key, icon, t_key, s_key, r, c, p_img in specs:
            card = CycleCard(
                grid_frame, icon=icon, title_key=t_key, sub_key=s_key, compact=True, planet_img=p_img
            )
            card.grid(row=r, column=c, padx=4, pady=3, sticky="nsew")
            self.world_cards[key] = card

    def _build_duviri_section(self) -> None:
        self.duv_sec_lbl = ctk.CTkLabel(
            self, text=tr("live_duviri_title"), font=ctk.CTkFont(size=13, weight="bold"), text_color="#D0D7DE"
        )
        self.duv_sec_lbl.grid(row=3, column=0, padx=14, pady=(2, 4), sticky="w")

        self.inc_title_lbl, self.inc_timer, self.inc_cur, self.inc_next = self._make_duviri_box(
            row=4, title_key="live_inc_title"
        )
        self.wf_title_lbl, self.wf_timer, self.wf_cur, self.wf_next = self._make_duviri_box(
            row=5, title_key="live_wf_title"
        )

    def _make_duviri_box(self, row: int, title_key: str) -> tuple:
        box = ctk.CTkFrame(
            self, corner_radius=8, fg_color="#141A29", border_width=1, border_color="#232F46"
        )
        box.grid(row=row, column=0, padx=12, pady=3, sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(box, fg_color="transparent")
        top.grid(row=0, column=0, padx=10, pady=(6, 1), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        title_lbl = ctk.CTkLabel(
            top, text=tr(title_key), font=ctk.CTkFont(size=12, weight="bold"), text_color="#60A5FA"
        )
        title_lbl.grid(row=0, column=0, sticky="w")

        timer_lbl = ctk.CTkLabel(
            top, text="3j 8h", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4ADE80"
        )
        timer_lbl.grid(row=0, column=1, sticky="e")

        cur_lbl = ctk.CTkLabel(
            box, text="...", font=ctk.CTkFont(size=11, weight="bold"), text_color="#F0F6FC", anchor="w"
        )
        cur_lbl.grid(row=1, column=0, padx=10, pady=0, sticky="ew")

        nxt_lbl = ctk.CTkLabel(
            box, text="...", font=ctk.CTkFont(size=10), text_color="#7D8590", anchor="w"
        )
        nxt_lbl.grid(row=2, column=0, padx=10, pady=(0, 6), sticky="ew")
        return title_lbl, timer_lbl, cur_lbl, nxt_lbl

    def _build_bounty_card(self) -> None:
        """Carte en direct des rotations A/B/C des Mises à Prix."""
        box = ctk.CTkFrame(
            self, corner_radius=8, fg_color="#141A29", border_width=1, border_color="#232F46"
        )
        box.grid(row=6, column=0, padx=12, pady=3, sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(box, fg_color="transparent")
        top.grid(row=0, column=0, padx=10, pady=(6, 1), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        self.bounty_title_lbl = ctk.CTkLabel(
            top, text=tr("live_bounty_title"), font=ctk.CTkFont(size=12, weight="bold"), text_color="#60A5FA"
        )
        self.bounty_title_lbl.grid(row=0, column=0, sticky="w")

        self.bounty_timer = ctk.CTkLabel(
            top, text="1h 27m", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4ADE80"
        )
        self.bounty_timer.grid(row=0, column=1, sticky="e")

        self.bounty_info = ctk.CTkLabel(
            box, text="...", font=ctk.CTkFont(size=11, weight="bold"), text_color="#F0F6FC", anchor="w"
        )
        self.bounty_info.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="ew")

    def _build_baro_card(self) -> None:
        box = ctk.CTkFrame(
            self, corner_radius=8, fg_color="#141A29", border_width=1, border_color="#232F46"
        )
        box.grid(row=7, column=0, padx=12, pady=(3, 10), sticky="ew")
        box.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(box, fg_color="transparent")
        top.grid(row=0, column=0, padx=10, pady=(6, 1), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        self.baro_title_lbl = ctk.CTkLabel(
            top, text=tr("live_baro_title"), font=ctk.CTkFont(size=12, weight="bold"), text_color="#60A5FA"
        )
        self.baro_title_lbl.grid(row=0, column=0, sticky="w")

        self.baro_timer = ctk.CTkLabel(
            top, text="--j --h", font=ctk.CTkFont(size=12, weight="bold"), text_color="#4ADE80"
        )
        self.baro_timer.grid(row=0, column=1, sticky="e")

        self.baro_info = ctk.CTkLabel(
            box, text="...", font=ctk.CTkFont(size=11, weight="bold"), text_color="#F0F6FC", anchor="w"
        )
        self.baro_info.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="ew")

    def load_state(self, world_state: dict, duviri_state: dict) -> None:
        self.last_world_state = world_state
        self.last_duviri_state = duviri_state

        for key, card in self.world_cards.items():
            info = world_state.get(key, {})
            card.set_data(info.get("state", "..."), info.get("expiry", ""))

        self.duviri_expiry = duviri_state.get("expiry", "")
        inc_now = ", ".join(duviri_state.get("incarnon_weapons", []))
        inc_nxt = ", ".join(duviri_state.get("next_incarnon_weapons", []))
        wf_now = " • ".join(duviri_state.get("warframes", []))
        wf_nxt = " • ".join(duviri_state.get("next_warframes", []))

        self.inc_cur.configure(text=f"{tr('lbl_current')} : {inc_now}")
        self.inc_next.configure(text=f"{tr('lbl_next')} : {inc_nxt}")
        self.wf_cur.configure(text=f"{tr('lbl_current')} : {wf_now}")
        self.wf_next.configure(text=f"{tr('lbl_next')} : {wf_nxt}")

        bounty = get_current_bounty_rotation()
        self.bounty_expiry = bounty.get("expiry", "")
        b_cur = bounty.get("current_rotation", "Rotation A")
        b_nxt = bounty.get("next_rotation", "Rotation B")
        self.bounty_info.configure(text=f"{tr('lbl_current')} : {b_cur}  ➔  {tr('lbl_next')} : {b_nxt}")

        baro = world_state.get("baro", {})
        is_here = baro.get("active", False)
        self.baro_target_iso = baro.get("expiry", "") if is_here else baro.get("activation", "")
        status_prefix = tr("baro_present") if is_here else tr("baro_arrives")
        self.baro_info.configure(text=f"{status_prefix} ➔ {baro.get('location', 'Relais')}")
        self.update_timers()

    def update_language(self) -> None:
        self.badge_lbl.configure(text=tr("live_badge"))
        self.live_lbl.configure(text=tr("live_tag"))
        self.worlds_sec_lbl.configure(text=tr("live_worlds_title"))
        self.duv_sec_lbl.configure(text=tr("live_duviri_title"))
        self.inc_title_lbl.configure(text=tr("live_inc_title"))
        self.wf_title_lbl.configure(text=tr("live_wf_title"))
        self.bounty_title_lbl.configure(text=tr("live_bounty_title"))
        self.baro_title_lbl.configure(text=tr("live_baro_title"))
        for card in self.world_cards.values():
            card.update_language()
        if self.last_world_state and self.last_duviri_state:
            self.load_state(self.last_world_state, self.last_duviri_state)

    def update_timers(self) -> None:
        for card in self.world_cards.values():
            card.refresh_timer()
        duv_txt = get_formatted_timer(self.duviri_expiry, short=True)
        self.inc_timer.configure(text=duv_txt)
        self.wf_timer.configure(text=duv_txt)
        self.bounty_timer.configure(text=get_formatted_timer(self.bounty_expiry, short=True))
        self.baro_timer.configure(text=get_formatted_timer(self.baro_target_iso, short=True))
