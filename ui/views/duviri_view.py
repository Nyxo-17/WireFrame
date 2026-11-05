"""Module duviri_view : Vue centrale du Circuit de Duviri bilingue FR/EN."""

import customtkinter as ctk
from core.i18n import tr
from core.timer_engine import get_formatted_timer


class DuviriView(ctk.CTkFrame):
    """Affiche les rotations actuelles, suivantes et le calendrier complet de Duviri."""

    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure((0, 1), weight=1, uniform="duv_col")
        self.grid_rowconfigure(2, weight=1)

        self.expiry_iso: str = ""
        self.last_duviri_state: dict = {}
        self._build_header()
        self._build_columns()

    def _build_header(self) -> None:
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2, padx=4, pady=(0, 12), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            top,
            text=tr("duviri_page_title"),
            font=ctk.CTkFont(size=22, weight="bold"),
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

    def _build_columns(self) -> None:
        self.inc_scroll = ctk.CTkScrollableFrame(
            self,
            label_text=tr("duviri_inc_col"),
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
            label_text=tr("duviri_wf_col"),
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
        self.last_duviri_state = duviri_state
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

            tag = tr("active_tag") if is_current else ""
            header_txt = f"{tr('week_label')} {idx}{tag}"
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

    def update_language(self) -> None:
        """Traduit tous les textes de la vue Duviri en FR ou EN."""
        self.title_lbl.configure(text=tr("duviri_page_title"))
        self.inc_scroll.configure(label_text=tr("duviri_inc_col"))
        self.wf_scroll.configure(label_text=tr("duviri_wf_col"))
        if self.last_duviri_state:
            self.load_state({}, self.last_duviri_state)

    def update_timers(self) -> None:
        txt = get_formatted_timer(self.expiry_iso, short=False)
        self.timer_badge.configure(text=f"{tr('duviri_reset_prefix')} {txt}")
