"""Module app_window : Fenêtre principale sans bordure Windows (TitleBar + 3 colonnes)."""

import customtkinter as ctk
from core.api_client import fetch_world_state
from core.duviri_calculator import get_current_duviri_rotation
from ui.components.titlebar import CustomTitleBar
from ui.live_panel import LivePanel
from ui.sidebar import Sidebar
from ui.views.baro_view import BaroView
from ui.views.duviri_view import DuviriView
from ui.views.welcome_view import WelcomeView
from ui.views.worlds_view import WorldsView


class WireframeApp(ctk.CTk):
    """Fenêtre principale de WireFrame V1 avec barre supérieure sombre et 3 colonnes."""

    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("WireFrame")
        self.geometry("1280x740+100+60")
        self.minsize(1100, 640)
        self.configure(fg_color="#090C14")

        # Supprime la barre de titre blanche de Windows pour utiliser notre CustomTitleBar
        self.overrideredirect(True)

        # Grille : Ligne 0 = CustomTitleBar, Ligne 1 = Les 3 colonnes principales
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.world_state: dict = {}
        self.duviri_state: dict = {}
        self.current_view_key: str = "welcome"

        # 0. Barre supérieure personnalisée (sur toute la largeur)
        self.titlebar = CustomTitleBar(self)
        self.titlebar.grid(row=0, column=0, columnspan=3, sticky="ew")

        # 1. Colonne gauche : Sidebar
        self.sidebar = Sidebar(
            self,
            on_navigate=self.show_view,
            on_refresh=self.refresh_all_data,
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew")

        # 2. Colonne centrale : Conteneur des Vues
        self.center_container = ctk.CTkFrame(
            self,
            corner_radius=10,
            fg_color="#0E131F",
            border_width=1,
            border_color="#1A2234",
        )
        self.center_container.grid(row=1, column=1, sticky="nsew", padx=(12, 8), pady=12)
        self.center_container.grid_columnconfigure(0, weight=1)
        self.center_container.grid_rowconfigure(0, weight=1)

        # 3. Colonne droite : Panneau Live 'Cycles & Événements'
        self.live_panel = LivePanel(self)
        self.live_panel.grid(row=1, column=2, sticky="nsew", padx=(4, 12), pady=12)

        # Instanciation des 4 vues centrales
        self.views: dict[str, ctk.CTkFrame] = {
            "welcome": WelcomeView(self.center_container, on_navigate=self.sidebar.select_tab),
            "worlds": WorldsView(self.center_container),
            "duviri": DuviriView(self.center_container),
            "baro": BaroView(self.center_container),
        }

        self.refresh_all_data()
        self.sidebar.select_tab("welcome")
        self._tick_timers()

    def show_view(self, view_key: str) -> None:
        """Affiche la vue demandée dans la zone centrale."""
        self.current_view_key = view_key
        for key, frame in self.views.items():
            if key == view_key:
                frame.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
            else:
                frame.grid_forget()

    def refresh_all_data(self) -> None:
        """Récupère les données depuis core/ et alimente le LivePanel et toutes les vues."""
        self.world_state = fetch_world_state()
        self.duviri_state = get_current_duviri_rotation()

        self.sidebar.update_status(self.world_state.get("source", "En direct"))
        self.live_panel.load_state(self.world_state, self.duviri_state)

        for view in self.views.values():
            if hasattr(view, "load_state"):
                view.load_state(self.world_state, self.duviri_state)

    def _tick_timers(self) -> None:
        """Met à jour chaque seconde le panneau de droite ET la vue centrale active."""
        self.live_panel.update_timers()

        active_view = self.views.get(self.current_view_key)
        if active_view and hasattr(active_view, "update_timers"):
            active_view.update_timers()

        self.after(1000, self._tick_timers)
