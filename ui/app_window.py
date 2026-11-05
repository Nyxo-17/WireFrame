"""Module app_window : Fenêtre principale CustomTkinter qui orchestre la Sidebar et les Vues."""

import customtkinter as ctk
from core.api_client import fetch_world_state
from core.duviri_calculator import get_current_duviri_rotation
from ui.sidebar import Sidebar


class WireframeApp(ctk.CTk):
    """Fenêtre principale de l'application Wireframe V1."""

    def __init__(self) -> None:
        super().__init__()

        # Configuration générale de la fenêtre
        ctk.set_appearance_mode("dark")
        self.title("Wireframe V1 — Dashboard des Timers Warframe")
        self.geometry("960x600")
        self.minsize(850, 520)
        self.configure(fg_color="#0D1017")

        # Grille principale : Colonne 0 = Sidebar (fixe), Colonne 1 = Contenu (extensible)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Données en mémoire (issues de core/)
        self.world_state: dict = {}
        self.duviri_state: dict = {}
        self.current_view_key: str = "worlds"
        self.views: dict[str, ctk.CTkFrame] = {}

        # 1. Création de la barre latérale à gauche
        self.sidebar = Sidebar(
            self,
            on_navigate=self.show_view,
            on_refresh=self.refresh_all_data,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # 2. Conteneur de droite où s'afficheront nos 3 vues
        self.content_container = ctk.CTkFrame(self, corner_radius=0, fg_color="#0D1017")
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=24, pady=24)
        self.content_container.grid_columnconfigure(0, weight=1)
        self.content_container.grid_rowconfigure(0, weight=1)

        # 3. Initialisation des vues et premier chargement des données
        self._init_views()
        self.refresh_all_data()
        self.sidebar.select_tab("worlds")

        # 4. Lancement de la boucle d'horloge (toutes les 1000 ms = 1 seconde)
        self._tick_timers()

    def _init_views(self) -> None:
        """Instancie les vues disponibles (ou un écran d'attente si non encore codées)."""
        for key, title in [
            ("worlds", "🌍 Mondes Ouverts"),
            ("duviri", "🌀 Circuit de Duviri"),
            ("baro", "💎 Baro Ki'Teer"),
        ]:
            placeholder = ctk.CTkFrame(self.content_container, fg_color="#141824", corner_radius=12)
            lbl = ctk.CTkLabel(
                placeholder,
                text=f"{title}\n\n(Vue prête à être branchée à l'étape suivante !)",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#D0D7DE",
            )
            lbl.pack(expand=True)
            self.views[key] = placeholder

    def show_view(self, view_key: str) -> None:
        """Affiche uniquement la vue demandée dans le conteneur de droite."""
        self.current_view_key = view_key
        for key, frame in self.views.items():
            if key == view_key:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_forget()

    def refresh_all_data(self) -> None:
        """Demande au dossier core/ les dernières données API et Duviri."""
        self.world_state = fetch_world_state()
        self.duviri_state = get_current_duviri_rotation()
        self.sidebar.update_status(self.world_state.get("source", "Inconnu"))

        # Si les vues possèdent une méthode load_state, on leur transmet les nouvelles données
        for view in self.views.values():
            if hasattr(view, "load_state"):
                view.load_state(self.world_state, self.duviri_state)

    def _tick_timers(self) -> None:
        """Appelé automatiquement toutes les secondes pour rafraîchir les comptes à rebours."""
        active_view = self.views.get(self.current_view_key)
        if active_view and hasattr(active_view, "update_timers"):
            active_view.update_timers()

        # Reprogramme le prochain tic d'horloge dans 1000 millisecondes (1 seconde)
        self.after(1000, self._tick_timers)
