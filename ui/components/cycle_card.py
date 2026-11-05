"""Module cycle_card : Composant réutilisable ('Moule à gâteau') pour un cycle de planète."""

import customtkinter as ctk
from core.timer_engine import get_formatted_timer


class CycleCard(ctk.CTkFrame):
    """Carte affichant l'icône, le nom, le sous-titre, l'état (Jour/Nuit) et le timer d'un monde."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        icon: str,
        title: str,
        subtitle: str,
        compact: bool = True,
    ) -> None:
        super().__init__(
            master,
            corner_radius=8,
            fg_color="#141A29",
            border_width=1,
            border_color="#232F46",
        )
        self.expiry_iso: str = ""
        self.compact = compact

        self.grid_columnconfigure(1, weight=1)

        # Icône de la planète à gauche
        self.icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=22 if compact else 28),
            width=32,
        )
        self.icon_label.grid(row=0, column=0, rowspan=2, padx=(10, 6), pady=(10, 4), sticky="n")

        # Nom de la planète (ex: Terre (Cetus))
        self.title_label = ctk.CTkLabel(
            self,
            text=title,
            font=ctk.CTkFont(size=12 if compact else 16, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        self.title_label.grid(row=0, column=1, padx=(0, 8), pady=(8, 0), sticky="ew")

        # Sous-titre (ex: Cycle Cetus)
        self.sub_label = ctk.CTkLabel(
            self,
            text=subtitle,
            font=ctk.CTkFont(size=10 if compact else 12),
            text_color="#7D8590",
            anchor="w",
        )
        self.sub_label.grid(row=1, column=1, padx=(0, 8), pady=(0, 6), sticky="ew")

        # Ligne du bas : État à gauche (en bleu clair) + Timer à droite (en blanc)
        bottom_row = ctk.CTkFrame(self, fg_color="transparent")
        bottom_row.grid(row=2, column=0, columnspan=2, padx=10, pady=(2, 8), sticky="ew")
        bottom_row.grid_columnconfigure(0, weight=1)

        self.state_label = ctk.CTkLabel(
            bottom_row,
            text="...",
            font=ctk.CTkFont(size=12 if compact else 15, weight="bold"),
            text_color="#4DA3FF",
            anchor="w",
        )
        self.state_label.grid(row=0, column=0, sticky="w")

        self.timer_label = ctk.CTkLabel(
            bottom_row,
            text="--m --s",
            font=ctk.CTkFont(size=12 if compact else 15, weight="bold"),
            text_color="#FFFFFF",
            anchor="e",
        )
        self.timer_label.grid(row=0, column=1, sticky="e")

    def set_data(self, state_text: str, expiry_iso: str) -> None:
        """Met à jour l'état (Jour/Nuit/Froid/Vome) et la date de fin."""
        self.expiry_iso = expiry_iso
        self.state_label.configure(text=state_text)
        self.refresh_timer()

    def refresh_timer(self) -> None:
        """Recalcule et affiche le compte à rebours chaque seconde."""
        timer_text = get_formatted_timer(self.expiry_iso, short=self.compact)
        self.timer_label.configure(text=timer_text)
