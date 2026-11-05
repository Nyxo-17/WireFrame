"""Module sidebar : Barre latérale de navigation gauche (Composant CTkFrame)."""

from typing import Callable
import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    """Menu latéral contenant les boutons de changement de vue et le bouton Actualiser."""

    def __init__(
        self,
        master: ctk.CTk,
        on_navigate: Callable[[str], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__(master, width=230, corner_radius=0, fg_color="#141824")
        self.on_navigate = on_navigate
        self.on_refresh = on_refresh
        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        # Empêche la barre latérale de rétrécir
        self.grid_propagate(False)
        self.grid_rowconfigure(5, weight=1)

        self._build_header()
        self._build_nav_buttons()
        self._build_footer()

    def _build_header(self) -> None:
        """Affiche le titre et le sous-titre de l'application en haut du menu."""
        title_lbl = ctk.CTkLabel(
            self,
            text="⚡ WIREFRAME",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#D4AF37",  # Doré Orokin
        )
        title_lbl.grid(row=0, column=0, padx=20, pady=(25, 2), sticky="w")

        subtitle_lbl = ctk.CTkLabel(
            self,
            text="Dashboard Tenno • V1.0",
            font=ctk.CTkFont(size=12),
            text_color="#8A94A6",
        )
        subtitle_lbl.grid(row=1, column=0, padx=20, pady=(0, 25), sticky="w")

    def _build_nav_buttons(self) -> None:
        """Crée les 3 boutons de navigation principaux."""
        items = [
            ("worlds", "🌍  Mondes Ouverts", 2),
            ("duviri", "🌀  Circuit de Duviri", 3),
            ("baro", "💎  Baro Ki'Teer", 4),
        ]

        for view_key, label_text, row_idx in items:
            btn = ctk.CTkButton(
                self,
                text=label_text,
                anchor="w",
                height=42,
                corner_radius=8,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="transparent",
                text_color="#D0D7DE",
                hover_color="#232A3E",
                command=lambda key=view_key: self.select_tab(key),
            )
            btn.grid(row=row_idx, column=0, padx=14, pady=5, sticky="ew")
            self.nav_buttons[view_key] = btn

    def _build_footer(self) -> None:
        """Crée l'indicateur de statut réseau et le bouton d'actualisation en bas."""
        self.status_label = ctk.CTkLabel(
            self,
            text="📡 Source : Initialisation...",
            font=ctk.CTkFont(size=11),
            text_color="#8A94A6",
            wraplength=190,
            justify="left",
        )
        self.status_label.grid(row=6, column=0, padx=16, pady=(10, 8), sticky="w")

        self.refresh_btn = ctk.CTkButton(
            self,
            text="🔄 Actualiser l'API",
            height=38,
            corner_radius=8,
            fg_color="#1F6FEB",
            hover_color="#388BFD",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.on_refresh,
        )
        self.refresh_btn.grid(row=7, column=0, padx=16, pady=(0, 20), sticky="ew")

    def select_tab(self, active_key: str) -> None:
        """Met en surbrillance l'onglet sélectionné et déclenche la navigation."""
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(fg_color="#28324E", text_color="#D4AF37")
            else:
                btn.configure(fg_color="transparent", text_color="#D0D7DE")
        self.on_navigate(active_key)

    def update_status(self, source_text: str) -> None:
        """Met à jour le texte indiquant si les données viennent de l'API ou du cache."""
        self.status_label.configure(text=f"📡 {source_text}")
