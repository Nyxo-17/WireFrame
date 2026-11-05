"""Module bounties_view : Vue centrale des Rotations A, B et C des Mises à Prix."""

import customtkinter as ctk
from core.codex_service import get_current_bounty_rotation
from core.i18n import tr
from core.timer_engine import get_formatted_timer


class BountiesView(ctk.CTkFrame):
    """Affiche en direct les rotations A, B et C des contrats de Mises à Prix par planète."""

    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.expiry_iso: str = ""
        self.current_scale: float = 1.0
        self._build_header()
        self._build_scroll()
        self.load_state({}, {})

    def _build_header(self) -> None:
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, padx=4, pady=(0, 12), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            top,
            text=tr("bounties_page_title"),
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        self.title_lbl.grid(row=0, column=0, sticky="w")

        self.timer_badge = ctk.CTkLabel(
            top,
            text="...",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4ADE80",
            fg_color="#141A29",
            corner_radius=8,
            padx=12,
            pady=6,
        )
        self.timer_badge.grid(row=0, column=1, sticky="e")

    def _build_scroll(self) -> None:
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="#111624",
            border_width=1,
            border_color="#1F293D",
            corner_radius=10,
        )
        self.scroll.grid(row=1, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

    def load_state(self, _world_state: dict, _duviri_state: dict) -> None:
        """Charge l'état actuel des rotations A/B/C et met en surbrillance la rotation active."""
        for child in self.scroll.winfo_children():
            child.destroy()

        bounty_state = get_current_bounty_rotation()
        self.expiry_iso = bounty_state.get("expiry", "")
        active_idx = bounty_state.get("rotation_index", 0)
        hubs = bounty_state.get("hubs", [])

        s = self.current_scale
        for idx, hub_data in enumerate(hubs):
            card = ctk.CTkFrame(
                self.scroll,
                corner_radius=10,
                fg_color="#141A29",
                border_width=1,
                border_color="#23304C",
            )
            card.grid(row=idx, column=0, padx=8, pady=6, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                card,
                text=hub_data.get("hub", ""),
                font=ctk.CTkFont(size=int(15 * s), weight="bold"),
                text_color="#58A6FF",
                anchor="w",
            ).grid(row=0, column=0, padx=12, pady=(10, 6), sticky="ew")

            rot_keys = [("Rotation A", "rot_a", 0), ("Rotation B", "rot_b", 1), ("Rotation C", "rot_c", 2)]
            for rot_name, key, r_idx in rot_keys:
                is_active = r_idx == active_idx
                row_frame = ctk.CTkFrame(
                    card,
                    corner_radius=6,
                    fg_color="#182744" if is_active else "transparent",
                    border_width=1 if is_active else 0,
                    border_color="#3B82F6",
                )
                row_frame.grid(row=r_idx + 1, column=0, padx=10, pady=2, sticky="ew")
                row_frame.grid_columnconfigure(1, weight=1)

                badge_txt = f"● {rot_name} (ACTUEL)" if is_active else f"   {rot_name}"
                ctk.CTkLabel(
                    row_frame,
                    text=badge_txt,
                    width=155,
                    font=ctk.CTkFont(size=int(12 * s), weight="bold"),
                    text_color="#4ADE80" if is_active else "#7D8590",
                    anchor="w",
                ).grid(row=0, column=0, padx=8, pady=4, sticky="w")

                ctk.CTkLabel(
                    row_frame,
                    text=hub_data.get(key, ""),
                    font=ctk.CTkFont(size=int(12 * s), weight="bold" if is_active else "normal"),
                    text_color="#FFFFFF" if is_active else "#8B949E",
                    anchor="w",
                ).grid(row=0, column=1, padx=8, pady=4, sticky="ew")

        self.update_timers()

    def update_language(self) -> None:
        self.title_lbl.configure(text=tr("bounties_page_title"))
        self.load_state({}, {})

    def apply_zoom(self, scale: float) -> None:
        self.current_scale = scale
        self.title_lbl.configure(font=ctk.CTkFont(size=int(20 * scale), weight="bold"))
        self.timer_badge.configure(font=ctk.CTkFont(size=int(14 * scale), weight="bold"))
        self.load_state({}, {})

    def update_timers(self) -> None:
        txt = get_formatted_timer(self.expiry_iso, short=False)
        self.timer_badge.configure(text=f"{tr('bounties_change_in')} {txt}")

