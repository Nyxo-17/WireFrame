"""Module duviri_view : Vue centrale du Circuit de Duviri (Warframes & Armes Incarnon)."""

import customtkinter as ctk
from core.timer_engine import get_formatted_timer


class DuviriView(ctk.CTkFrame):
    """Affiche les rotations actuelles, suivantes et le calendrier complet de Duviri."""

    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure((0, 1), weight=1, uniform="duv_col")
        self.grid_rowconfigure(2, weight=1)

        self.expiry_iso: str = ""
        self._build_header()
        self._build_columns()

    def _build_header(self) -> None:
        """En-tête avec le titre et le compte à rebours avant le reset du lundi."""
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2, padx=4, pady=(0, 12), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top,
            text="⚔️  Le Circuit de Duviri — Calendrier des Rotations",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.timer_badge = ctk.CTkLabel(
            top,
            text="Reset dans : --j --h",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#4ADE80",
            fg_color="#141A29",
            corner_radius=8,
            padx=12,
            pady=6,
        )
        self.timer_badge.grid(row=0, column=1, sticky="e")

    def _build_columns(self) -> None:
        """Crée deux colonnes : Armes Incarnon (8 semaines) et Warframes (11 semaines)."""
        self.inc_scroll = ctk.CTkScrollableFrame(
            self,
            label_text="⚔️ Armes Incarnon (Route de l'Acier — 8 Semaines)",
            label_font=ctk.CTkFont(size=14, weight="bold"),
            label_text_color="#58A6FF",
            fg_color="#121826",
            border_width=1,
            border_color="#212C42",
            corner_radius=10,
        )
        self.inc_scroll.grid(row=2, column=0, padx=(0, 8), pady=4, sticky="nsew")
        self.inc_scroll.grid_columnconfigure(0, weight=1)

        self.wf_scroll = ctk.CTkScrollableFrame(
            self,
            label_text="🛡️ Warframes du Circuit (Normal — 11 Semaines)",
            label_font=ctk.CTkFont(size=14, weight="bold"),
            label_text_color="#58A6FF",
            fg_color="#121826",
            border_width=1,
            border_color="#212C42",
            corner_radius=10,
        )
        self.wf_scroll.grid(row=2, column=1, padx=(8, 0), pady=4, sticky="nsew")
        self.wf_scroll.grid_columnconfigure(0, weight=1)

    def load_state(self, _world_state: dict, duviri_state: dict) -> None:
        """Affiche toutes les semaines et met en surbrillance la semaine active."""
        self.expiry_iso = duviri_state.get("expiry", "")
        inc_active = duviri_state.get("incarnon_week_number", 1)
        wf_active = duviri_state.get("warframe_week_number", 1)

        self._populate_list(
            self.inc_scroll,
            duviri_state.get("all_incarnon_weeks", []),
            inc_active,
        )
        self._populate_list(
            self.wf_scroll,
            duviri_state.get("all_warframes_weeks", []),
            wf_active,
        )
        self.update_timers()

    def _populate_list(
        self, container: ctk.CTkScrollableFrame, weeks: list[list[str]], active_week: int
    ) -> None:
        """Remplit une colonne déroulante en illuminant la semaine actuelle en bleu/vert."""
        for child in container.winfo_children():
            child.destroy()

        for idx, items in enumerate(weeks, start=1):
            is_current = idx == active_week
            row_box = ctk.CTkFrame(
                container,
                corner_radius=8,
                fg_color="#172542" if is_current else "#141A29",
                border_width=1,
                border_color="#3B82F6" if is_current else "#1E2738",
            )
            row_box.grid(row=idx, column=0, padx=6, pady=4, sticky="ew")
            row_box.grid_columnconfigure(0, weight=1)

            tag = "  ● EN COURS" if is_current else ""
            header_txt = f"Semaine {idx}{tag}"
            ctk.CTkLabel(
                row_box,
                text=header_txt,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#4ADE80" if is_current else "#7D8590",
                anchor="w",
            ).grid(row=0, column=0, padx=10, pady=(6, 1), sticky="ew")

            ctk.CTkLabel(
                row_box,
                text=" • ".join(items),
                font=ctk.CTkFont(size=13, weight="bold" if is_current else "normal"),
                text_color="#FFFFFF" if is_current else "#B1BAC4",
                anchor="w",
            ).grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")

    def update_timers(self) -> None:
        """Met à jour le timer du reset hebdomadaire."""
        txt = get_formatted_timer(self.expiry_iso, short=False)
        self.timer_badge.configure(text=f"⏳ Reset dans : {txt}")

