"""Module welcome_view : Page centrale d'accueil ('Bienvenue dans WireFrame !')."""

from typing import Callable
import customtkinter as ctk


class WelcomeView(ctk.CTkFrame):
    """Vue d'accueil présentant la bannière et la grille de cartes de navigation rapide."""

    def __init__(self, master: ctk.CTkBaseClass, on_navigate: Callable[[str], None]) -> None:
        super().__init__(master, fg_color="transparent")
        self.on_navigate = on_navigate

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Titre de la page en haut
        page_title = ctk.CTkLabel(
            self,
            text="Bienvenue sur WireFrame",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        page_title.grid(row=0, column=0, padx=4, pady=(0, 12), sticky="ew")

        self._build_hero_banner()
        self._build_feature_cards()
        self._build_signature()

    def _build_hero_banner(self) -> None:
        """Crée la grande bannière supérieure 'BIENVENUE DANS WIREFRAME !'."""
        banner = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color="#131B2E",
            border_width=1,
            border_color="#23304C",
        )
        banner.grid(row=1, column=0, pady=(0, 14), sticky="ew")
        banner.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            banner,
            text="BIENVENUE DANS WIREFRAME !",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF",
        )
        title.grid(row=0, column=0, padx=20, pady=(18, 6))

        desc = ctk.CTkLabel(
            banner,
            text=(
                "Ton compagnon Warframe minimaliste et fluide pour suivre en direct les cycles des planètes,\n"
                "les rotations du Circuit de Duviri (Warframes & Incarnon) et le marchand Baro Ki'Teer."
            ),
            font=ctk.CTkFont(size=12),
            text_color="#8B949E",
            justify="center",
        )
        desc.grid(row=1, column=0, padx=20, pady=(0, 18))

    def _build_feature_cards(self) -> None:
        """Crée la grille 2x2 des cartes de fonctionnalités avec bouton 'Ouvrir ➔'."""
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.grid(row=2, column=0, sticky="nsew")
        grid.grid_columnconfigure((0, 1), weight=1, uniform="feat_col")

        cards_data = [
            (
                "🌍  1. Temps des Planètes",
                "Suivi en temps réel des cycles Jour/Nuit, Chaud/Froid et Fass/Vome pour Cetus, Orb Vallis, Cambion Drift et les Forêts de la Terre.",
                "worlds",
                0,
                0,
            ),
            (
                "⚔️  2. Armes Incarnon (Route de l'Acier)",
                "Calendrier complet en direct des 8 semaines de rotation des adaptateurs Incarnon à débloquer dans le Circuit Route de l'Acier.",
                "duviri",
                0,
                1,
            ),
            (
                "🛡️  3. Warframes du Circuit (Duviri)",
                "Calendrier en direct des 11 semaines de rotation des Warframes disponibles dans le Circuit normal de Duviri (Actuel + Suivant).",
                "duviri",
                1,
                0,
            ),
            (
                "💎  4. Marchand du Néant (Baro Ki'Teer)",
                "Compte à rebours avant l'arrivée ou le départ de Baro Ki'Teer, son Relais de destination et la liste de ses offres en Ducats.",
                "baro",
                1,
                1,
            ),
        ]

        for title, text, target_key, r, c in cards_data:
            self._make_card(grid, title, text, target_key, r, c)

    def _make_card(
        self, parent: ctk.CTkFrame, title: str, desc: str, target_key: str, r: int, c: int
    ) -> None:
        """Construit une carte de présentation individuelle avec son bouton Ouvrir ➔."""
        card = ctk.CTkFrame(
            parent,
            corner_radius=10,
            fg_color="#121826",
            border_width=1,
            border_color="#212C42",
        )
        card.grid(row=r, column=c, padx=6, pady=6, sticky="nsew")
        card.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, padx=14, pady=(14, 6), sticky="ew")
        top.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            top,
            text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#58A6FF",
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        open_btn = ctk.CTkButton(
            top,
            text="Ouvrir ➔",
            width=76,
            height=26,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#1C273E",
            text_color="#D0D7DE",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda k=target_key: self.on_navigate(k),
        )
        open_btn.grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(
            card,
            text=desc,
            font=ctk.CTkFont(size=12),
            text_color="#8B949E",
            justify="left",
            anchor="w",
            wraplength=260,
        ).grid(row=1, column=0, padx=14, pady=(0, 16), sticky="ew")

    def _build_signature(self) -> None:
        """Affiche la signature 'Créé par : Nyxo_17' en bas à droite."""
        sig_frame = ctk.CTkFrame(self, fg_color="transparent")
        sig_frame.grid(row=3, column=0, pady=(8, 0), sticky="e")

        ctk.CTkLabel(
            sig_frame,
            text="Créé par : ",
            font=ctk.CTkFont(size=13),
            text_color="#7D8590",
        ).grid(row=0, column=0)

        ctk.CTkLabel(
            sig_frame,
            text="Nyxo_17",
            font=ctk.CTkFont(size=14, weight="bold", slant="italic"),
            text_color="#F0F6FC",
        ).grid(row=0, column=1)

