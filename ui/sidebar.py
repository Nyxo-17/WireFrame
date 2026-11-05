"""Module sidebar : Barre latérale gauche au style 'WireFrame by Nyxo_17'."""

from typing import Callable
import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    """Menu latéral contenant l'en-tête créateur Nyxo_17 et les sections de navigation."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Callable[[str], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__(master, width=220, corner_radius=0, fg_color="#0D111A")
        self.on_navigate = on_navigate
        self.on_refresh = on_refresh
        self.nav_buttons: dict[str, ctk.CTkButton] = {}

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(10, weight=1)

        self._build_creator_badge()
        self._build_navigation()
        self._build_footer()

    def _build_creator_badge(self) -> None:
        """Affiche l'encart 'Nyxo_17 - Créateur de WireFrame' en haut à gauche."""
        profile_box = ctk.CTkFrame(self, fg_color="transparent")
        profile_box.grid(row=0, column=0, padx=14, pady=(18, 12), sticky="ew")

        # Badge icône doré façon maîtrise Warframe
        emblem = ctk.CTkLabel(
            profile_box,
            text="❖",
            width=38,
            height=38,
            corner_radius=6,
            fg_color="#2A2415",
            text_color="#E5C158",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        emblem.grid(row=0, column=0, rowspan=2, padx=(0, 10))

        name_lbl = ctk.CTkLabel(
            profile_box,
            text="Nyxo_17",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        name_lbl.grid(row=0, column=1, sticky="w")

        role_lbl = ctk.CTkLabel(
            profile_box,
            text="Créateur de WireFrame",
            font=ctk.CTkFont(size=11),
            text_color="#7D8590",
            anchor="w",
        )
        role_lbl.grid(row=1, column=1, sticky="w")

    def _add_section_title(self, text: str, row: int) -> None:
        """Ajoute un petit titre de catégorie en majuscules grises."""
        lbl = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#6E7681",
            anchor="w",
        )
        lbl.grid(row=row, column=0, padx=18, pady=(12, 4), sticky="ew")

    def _build_navigation(self) -> None:
        """Construit les catégories et boutons de navigation."""
        self._add_section_title("ACCUEIL", row=1)
        self._create_nav_btn("welcome", "🏠   Bienvenue", row=2)

        self._add_section_title("CYCLES & ROTATIONS", row=3)
        nav_items = [
            ("worlds", "🌍   Temps des Planètes", 4),
            ("duviri", "⚔️   Circuit & Incarnon", 5),
            ("baro", "💎   Baro Ki'Teer", 6),
        ]
        for key, label, row_idx in nav_items:
            self._create_nav_btn(key, label, row=row_idx)

    def _create_nav_btn(self, key: str, text: str, row: int) -> None:
        """Crée un bouton de menu stylisé avec bordure bleue lorsqu'il est actif."""
        btn = ctk.CTkButton(
            self,
            text=text,
            anchor="w",
            height=38,
            corner_radius=7,
            border_width=1,
            border_color="#0D111A",
            fg_color="transparent",
            text_color="#B1BAC4",
            hover_color="#161E2E",
            font=ctk.CTkFont(size=13),
            command=lambda k=key: self.select_tab(k),
        )
        btn.grid(row=row, column=0, padx=12, pady=3, sticky="ew")
        self.nav_buttons[key] = btn

    def _build_footer(self) -> None:
        """Affiche la source des données et le bouton d'actualisation en bas."""
        self.status_label = ctk.CTkLabel(
            self,
            text="📡 Initialisation...",
            font=ctk.CTkFont(size=11),
            text_color="#7D8590",
            anchor="w",
        )
        self.status_label.grid(row=11, column=0, padx=16, pady=(4, 6), sticky="ew")

        refresh_btn = ctk.CTkButton(
            self,
            text="🔄  Actualiser en direct",
            height=36,
            corner_radius=7,
            fg_color="#161E31",
            border_width=1,
            border_color="#2A3B5C",
            hover_color="#1F2D4A",
            text_color="#58A6FF",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.on_refresh,
        )
        refresh_btn.grid(row=12, column=0, padx=12, pady=(0, 16), sticky="ew")

    def select_tab(self, active_key: str) -> None:
        """Illumine le bouton actif avec un contour bleu comme sur la maquette."""
        for key, btn in self.nav_buttons.items():
            if key == active_key:
                btn.configure(
                    fg_color="#17223B",
                    border_color="#3B82F6",
                    text_color="#FFFFFF",
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    border_color="#0D111A",
                    text_color="#B1BAC4",
                )
        self.on_navigate(active_key)

    def update_status(self, source_text: str) -> None:
        """Met à jour le texte de statut en bas de la barre latérale."""
        self.status_label.configure(text=f"📡 {source_text}")
