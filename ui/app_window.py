"""Module app_window : Fenêtre principale aux coins arrondis, barre sombre et support FR/EN."""

import ctypes
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

TRANSPARENT_KEY = "#000001"


class WireframeApp(ctk.CTk):
    """Fenêtre principale de WireFrame V1 avec coins arrondis et traduction dynamique FR/EN."""

    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("WireFrame")
        self.geometry("1280x740+100+60")
        self.minsize(1100, 640)

        # Configuration sans bordure Windows + coins transparents pour le rendu arrondi
        self.overrideredirect(True)
        self.configure(fg_color=TRANSPARENT_KEY)
        self.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        self._enable_win11_rounded_corners()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Coquille principale aux coins arrondis (corner_radius=16) et fine bordure bleutée
        self.window_shell = ctk.CTkFrame(
            self,
            corner_radius=16,
            fg_color="#090C14",
            border_width=1,
            border_color="#232F46",
        )
        self.window_shell.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)
        self.window_shell.grid_columnconfigure(0, weight=0)
        self.window_shell.grid_columnconfigure(1, weight=1)
        self.window_shell.grid_columnconfigure(2, weight=0)
        self.window_shell.grid_rowconfigure(0, weight=0)
        self.window_shell.grid_rowconfigure(1, weight=1)

        self.world_state: dict = {}
        self.duviri_state: dict = {}
        self.current_view_key: str = "welcome"

        # 0. Barre supérieure personnalisée (avec sélecteur FR/EN actif)
        self.titlebar = CustomTitleBar(
            self.window_shell, app=self, on_lang_change=self.apply_language
        )
        self.titlebar.grid(row=0, column=0, columnspan=3, sticky="ew", padx=2, pady=(2, 0))

        # 1. Colonne gauche : Sidebar
        self.sidebar = Sidebar(
            self.window_shell,
            on_navigate=self.show_view,
            on_refresh=self.refresh_all_data,
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew", padx=(4, 0), pady=(0, 6))

        # 2. Colonne centrale : Conteneur des Vues
        self.center_container = ctk.CTkFrame(
            self.window_shell,
            corner_radius=10,
            fg_color="#0E131F",
            border_width=1,
            border_color="#1A2234",
        )
        self.center_container.grid(row=1, column=1, sticky="nsew", padx=(10, 8), pady=10)
        self.center_container.grid_columnconfigure(0, weight=1)
        self.center_container.grid_rowconfigure(0, weight=1)

        # 3. Colonne droite : Panneau Live 'Cycles & Événements'
        self.live_panel = LivePanel(self.window_shell)
        self.live_panel.grid(row=1, column=2, sticky="nsew", padx=(4, 12), pady=10)

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

    def _enable_win11_rounded_corners(self) -> None:
        """Active le lissage natif des coins arrondis Windows 11 via DWM API si disponible."""
        try:
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                hwnd, 33, ctypes.byref(ctypes.c_int(2)), 4
            )
        except Exception:
            pass

    def show_view(self, view_key: str) -> None:
        self.current_view_key = view_key
        for key, frame in self.views.items():
            if key == view_key:
                frame.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
            else:
                frame.grid_forget()

    def apply_language(self) -> None:
        """Propage instantanément le changement de langue (FR/EN) à tous les composants."""
        self.sidebar.update_language()
        self.live_panel.update_language()
        for view in self.views.values():
            if hasattr(view, "update_language"):
                view.update_language()

    def refresh_all_data(self) -> None:
        self.world_state = fetch_world_state()
        self.duviri_state = get_current_duviri_rotation()

        self.sidebar.update_status(self.world_state.get("source", "Live"))
        self.live_panel.load_state(self.world_state, self.duviri_state)

        for view in self.views.values():
            if hasattr(view, "load_state"):
                view.load_state(self.world_state, self.duviri_state)

    def _tick_timers(self) -> None:
        self.live_panel.update_timers()
        active_view = self.views.get(self.current_view_key)
        if active_view and hasattr(active_view, "update_timers"):
            active_view.update_timers()
        self.after(1000, self._tick_timers)
