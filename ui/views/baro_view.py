"""Module baro_view : Vue centrale dédiée au marchand du Néant Baro Ki'Teer."""

import customtkinter as ctk
from core.timer_engine import get_formatted_timer


class BaroView(ctk.CTkFrame):
    """Affiche le statut de Baro Ki'Teer, son Relais, son compte à rebours et ses offres."""

    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(master, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.target_iso: str = ""
        self.is_active: bool = False

        self._build_header()
        self._build_status_banner()
        self._build_inventory_box()

    def _build_header(self) -> None:
        """Titre principal de la vue Baro Ki'Teer."""
        ctk.CTkLabel(
            self,
            text="💎  Marchand du Néant — Baro Ki'Teer",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        ).grid(row=0, column=0, padx=4, pady=(0, 12), sticky="ew")

    def _build_status_banner(self) -> None:
        """Carte supérieure résumant la présence, le Relais et le compte à rebours."""
        banner = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color="#131B2E",
            border_width=1,
            border_color="#23304C",
        )
        banner.grid(row=1, column=0, pady=(0, 14), sticky="ew")
        banner.grid_columnconfigure(0, weight=1)

        self.status_title = ctk.CTkLabel(
            banner,
            text="Chargement du statut de Baro Ki'Teer...",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#58A6FF",
            anchor="w",
        )
        self.status_title.grid(row=0, column=0, padx=18, pady=(16, 4), sticky="ew")

        self.relay_label = ctk.CTkLabel(
            banner,
            text="📍 Destination : ...",
            font=ctk.CTkFont(size=14),
            text_color="#D0D7DE",
            anchor="w",
        )
        self.relay_label.grid(row=1, column=0, padx=18, pady=(0, 16), sticky="ew")

        self.timer_label = ctk.CTkLabel(
            banner,
            text="--j --h --m --s",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#4ADE80",
        )
        self.timer_label.grid(row=0, column=1, rowspan=2, padx=20, pady=16, sticky="e")

    def _build_inventory_box(self) -> None:
        """Zone déroulante pour l'inventaire de Baro Ki'Teer."""
        self.inv_scroll = ctk.CTkScrollableFrame(
            self,
            label_text="📦 Inventaire du Néant (Mods Accrus, Armes Prisma & Cosmétiques)",
            label_font=ctk.CTkFont(size=14, weight="bold"),
            label_text_color="#58A6FF",
            fg_color="#121826",
            border_width=1,
            border_color="#212C42",
            corner_radius=10,
        )
        self.inv_scroll.grid(row=2, column=0, sticky="nsew")
        self.inv_scroll.grid_columnconfigure(0, weight=1)

    def load_state(self, world_state: dict, _duviri_state: dict) -> None:
        """Met à jour les informations de Baro Ki'Teer."""
        baro = world_state.get("baro", {})
        self.is_active = bool(baro.get("active", False))
        location = baro.get("location", "Relais inconnu")
        self.target_iso = baro.get("expiry", "") if self.is_active else baro.get("activation", "")

        if self.is_active:
            self.status_title.configure(text="🟢 Baro Ki'Teer est PRÉSENT sur le Relais !", text_color="#4ADE80")
        else:
            self.status_title.configure(text="⏳ Baro Ki'Teer voyage dans le Néant (Absent)", text_color="#58A6FF")

        self.relay_label.configure(text=f"📍 Destination : {location}")
        self._populate_inventory(baro.get("inventory", []))
        self.update_timers()

    def _populate_inventory(self, items: list[dict]) -> None:
        """Remplit la liste des objets vendus par Baro (ou affiche un message s'il est absent)."""
        for child in self.inv_scroll.winfo_children():
            child.destroy()

        if not items:
            msg = (
                "Baro Ki'Teer n'est pas encore arrivé.\n"
                "Son inventaire s'affichera automatiquement ici dès son arrivée le vendredi à 13h00 UTC !"
            )
            ctk.CTkLabel(
                self.inv_scroll,
                text=msg,
                font=ctk.CTkFont(size=13),
                text_color="#8B949E",
                justify="center",
            ).grid(row=0, column=0, padx=20, pady=40)
            return

        for idx, item in enumerate(items):
            row = ctk.CTkFrame(self.inv_scroll, fg_color="#141A29", corner_radius=6)
            row.grid(row=idx, column=0, padx=8, pady=3, sticky="ew")
            row.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                row,
                text=item.get("item", "Objet"),
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#F0F6FC",
                anchor="w",
            ).grid(row=0, column=0, padx=12, pady=8, sticky="w")

            price = f"🪙 {item.get('ducats', 0)} Ducats   •   💳 {item.get('credits', 0):,} Crédits"
            ctk.CTkLabel(
                row,
                text=price,
                font=ctk.CTkFont(size=12),
                text_color="#E5C158",
            ).grid(row=0, column=1, padx=12, pady=8, sticky="e")

    def update_timers(self) -> None:
        """Met à jour le compte à rebours d'arrivée ou de départ."""
        prefix = "Départ dans :" if self.is_active else "Arrivée dans :"
        self.timer_label.configure(text=f"{prefix} {get_formatted_timer(self.target_iso)}")

