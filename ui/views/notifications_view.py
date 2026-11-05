"""Module notifications_view : Centre de configuration des alertes et journal des notifications."""

import customtkinter as ctk
from core.i18n import tr
from core.notification_manager import NotificationManager


class NotificationsView(ctk.CTkFrame):
    """Vue permettant d'activer/désactiver les 5 types de notifications et de voir l'historique."""

    def __init__(self, master: ctk.CTkBaseClass, notif_manager: NotificationManager) -> None:
        super().__init__(master, fg_color="transparent")
        self.notif_manager = notif_manager
        self.switches: dict[str, tuple[ctk.CTkSwitch, str]] = {}
        self.current_scale: float = 1.0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self._build_header()
        self._build_switches_panel()
        self._build_history_panel()
        self.refresh_history()

    def _build_header(self) -> None:
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, padx=4, pady=(0, 8), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        self.title_lbl = ctk.CTkLabel(
            top,
            text=tr("notif_page_title"),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        self.title_lbl.grid(row=0, column=0, sticky="w")

        self.test_btn = ctk.CTkButton(
            top,
            text=tr("notif_test_btn"),
            height=34,
            corner_radius=8,
            fg_color="#1F6FEB",
            hover_color="#388BFD",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._send_test_alert,
        )
        self.test_btn.grid(row=0, column=1, sticky="e")

        self.sub_lbl = ctk.CTkLabel(
            self,
            text=tr("notif_page_sub"),
            font=ctk.CTkFont(size=12),
            text_color="#8B949E",
            anchor="w",
        )
        self.sub_lbl.grid(row=1, column=0, padx=4, pady=(0, 12), sticky="ew")

    def _build_switches_panel(self) -> None:
        panel = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color="#131B2E",
            border_width=1,
            border_color="#23304C",
        )
        panel.grid(row=2, column=0, pady=(0, 14), sticky="ew")
        panel.grid_columnconfigure(0, weight=1)

        items = [
            ("notify_planets", "notif_sw_planets"),
            ("notify_baro", "notif_sw_baro"),
            ("notify_bounties", "notif_sw_bounties"),
            ("notify_incarnon", "notif_sw_incarnon"),
            ("notify_warframes", "notif_sw_warframes"),
            ("sound_enabled", "notif_sw_sound"),
        ]

        for idx, (setting_key, tr_key) in enumerate(items):
            sw = ctk.CTkSwitch(
                panel,
                text=tr(tr_key),
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#F0F6FC",
                progress_color="#3B82F6",
                button_color="#FFFFFF",
                button_hover_color="#D0D7DE",
                command=lambda k=setting_key: self._on_toggle(k),
            )
            if self.notif_manager.settings.get(setting_key, True):
                sw.select()
            else:
                sw.deselect()
            sw.grid(row=idx, column=0, padx=18, pady=7, sticky="w")
            self.switches[setting_key] = (sw, tr_key)

    def _build_history_panel(self) -> None:
        self.hist_scroll = ctk.CTkScrollableFrame(
            self,
            label_text=tr("notif_history_title"),
            label_font=ctk.CTkFont(size=14, weight="bold"),
            label_text_color="#58A6FF",
            fg_color="#111624",
            border_width=1,
            border_color="#1F293D",
            corner_radius=10,
        )
        self.hist_scroll.grid(row=3, column=0, sticky="nsew")
        self.hist_scroll.grid_columnconfigure(0, weight=1)

    def _on_toggle(self, setting_key: str) -> None:
        sw, _ = self.switches[setting_key]
        self.notif_manager.update_setting(setting_key, bool(sw.get()))

    def _send_test_alert(self) -> None:
        self.notif_manager.trigger_notification(
            "⚡ Test d'alerte WireFrame",
            "Les notifications en direct (Planètes, Baro, Mises à Prix, Duviri) sont opérationnelles !",
        )
        self.refresh_history()

    def refresh_history(self) -> None:
        """Met à jour la liste des alertes déclenchées."""
        for child in self.hist_scroll.winfo_children():
            child.destroy()

        s = self.current_scale
        if not self.notif_manager.history:
            ctk.CTkLabel(
                self.hist_scroll,
                text=tr("notif_empty_history"),
                font=ctk.CTkFont(size=int(12 * s)),
                text_color="#8B949E",
            ).grid(row=0, column=0, padx=16, pady=24)
            return

        for idx, entry in enumerate(self.notif_manager.history):
            row = ctk.CTkFrame(
                self.hist_scroll, corner_radius=7, fg_color="#151C2E", border_width=1, border_color="#23304C"
            )
            row.grid(row=idx, column=0, padx=8, pady=4, sticky="ew")
            row.grid_columnconfigure(1, weight=1)

            ctk.CTkLabel(
                row,
                text=f"🕒 {entry['time']}",
                font=ctk.CTkFont(size=int(11 * s), weight="bold"),
                text_color="#4ADE80",
            ).grid(row=0, column=0, padx=12, pady=(6, 2), sticky="w")

            ctk.CTkLabel(
                row,
                text=entry["title"],
                font=ctk.CTkFont(size=int(13 * s), weight="bold"),
                text_color="#58A6FF",
                anchor="w",
            ).grid(row=0, column=1, padx=8, pady=(6, 2), sticky="ew")

            ctk.CTkLabel(
                row,
                text=entry["message"],
                font=ctk.CTkFont(size=int(12 * s)),
                text_color="#D0D7DE",
                anchor="w",
            ).grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 6), sticky="ew")

    def update_language(self) -> None:
        self.title_lbl.configure(text=tr("notif_page_title"))
        self.sub_lbl.configure(text=tr("notif_page_sub"))
        self.test_btn.configure(text=tr("notif_test_btn"))
        self.hist_scroll.configure(label_text=tr("notif_history_title"))
        for sw, tr_key in self.switches.values():
            sw.configure(text=tr(tr_key))
        self.refresh_history()

    def apply_zoom(self, scale: float) -> None:
        self.current_scale = scale
        self.title_lbl.configure(font=ctk.CTkFont(size=int(22 * scale), weight="bold"))
        self.sub_lbl.configure(font=ctk.CTkFont(size=int(12 * scale)))
        for sw, _ in self.switches.values():
            sw.configure(font=ctk.CTkFont(size=int(13 * scale), weight="bold"))
        self.refresh_history()

