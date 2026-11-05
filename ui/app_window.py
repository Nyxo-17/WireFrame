"""Module app_window : Fenêtre principale avec Splash Screen, chargement in-app et 9 vues."""

import ctypes
from pathlib import Path
import threading
import customtkinter as ctk
from core.api_client import fetch_world_state
from core.duviri_calculator import get_current_duviri_rotation
from core.notification_manager import NotificationManager
from core.timer_engine import get_remaining_seconds
from ui.components.loading_screens import InAppLoader, SplashScreen
from ui.components.titlebar import CustomTitleBar
from ui.live_panel import LivePanel
from ui.sidebar import Sidebar
from ui.views.baro_view import BaroView
from ui.views.bounties_view import BountiesView
from ui.views.codex_view import CodexView
from ui.views.duviri_view import DuviriView
from ui.views.notifications_view import NotificationsView
from ui.views.welcome_view import WelcomeView
from ui.views.worlds_view import WorldsView

ICON_PATH = Path(__file__).resolve().parent.parent / "data" / "app_icon.ico"


class WireframeApp(ctk.CTk):
    """Fenêtre principale de WireFrame avec Splash Screen au lancement et InAppLoader."""

    def __init__(self, skip_splash: bool = False) -> None:
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("nyxo17.wireframe.v1")
        except Exception:
            pass
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("WireFrame")
        self.geometry("1280x740+100+60")
        self.minsize(1100, 640)
        self.configure(fg_color="#090C14")
        if ICON_PATH.exists():
            try:
                self.iconbitmap(str(ICON_PATH))
            except Exception:
                pass

        self.overrideredirect(True)

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self.world_state: dict = {}
        self.duviri_state: dict = {}
        self.current_view_key: str = "welcome"
        self._tick_counter: int = 0
        self._toast_frame: ctk.CTkFrame | None = None
        self._is_refreshing: bool = False

        self.notif_manager = NotificationManager(on_alert_callback=self.show_in_app_toast)
        self._sidebar_visible: bool = True

        # 0. Barre supérieure personnalisée
        self.titlebar = CustomTitleBar(
            self,
            app=self,
            on_lang_change=self.apply_language,
            on_zoom_change=self.apply_center_zoom,
            on_toggle_sidebar=self.toggle_sidebar,
        )
        self.titlebar.grid(row=0, column=0, columnspan=3, sticky="ew")

        # 1. Colonne gauche : Sidebar auto-rétractable au survol
        self.sidebar = Sidebar(
            self,
            on_navigate=self.show_view,
            on_refresh=lambda: self.refresh_all_data(show_overlay=True),
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew")

        # 2. Colonne centrale : Conteneur des Vues + InAppLoader
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

        self.in_app_loader = InAppLoader(self.center_container)

        # 3. Colonne droite : Panneau Live
        self.live_panel = LivePanel(self)
        self.live_panel.grid(row=1, column=2, sticky="nsew", padx=(4, 12), pady=12)

        self.views: dict[str, ctk.CTkFrame] = {
            "welcome": WelcomeView(self.center_container, on_navigate=self.sidebar.select_tab),
            "notifications": NotificationsView(self.center_container, self.notif_manager),
            "resources": CodexView(self.center_container, "resources", "res_page_title"),
            "mods": CodexView(self.center_container, "mods", "mod_page_title"),
            "warframes": CodexView(self.center_container, "warframes", "wf_page_title"),
            "worlds": WorldsView(self.center_container),
            "bounties": BountiesView(self.center_container),
            "duviri": DuviriView(self.center_container),
            "baro": BaroView(self.center_container),
        }

        if skip_splash:
            self.after(50, self._apply_native_dwm_rounding)
            self.refresh_all_data(show_overlay=False)
            self.sidebar.select_tab("welcome")
            self._tick_timers()
            self._check_sidebar_hover()
        else:
            # Masque la fenêtre principale pendant le Splash Screen de démarrage
            self.withdraw()
            self.splash = SplashScreen(self, on_complete=self._on_splash_finished)
            self._run_startup_sequence()

    def _run_startup_sequence(self) -> None:
        """Exécute la séquence de lancement animée et récupère l'API en tâche de fond."""
        self.after(150, lambda: self.splash.set_progress(0.25, "Chargement du Codex (1 442 Mods, 239 Ressources, 120 Warframes)..."))
        self.after(550, lambda: self.splash.set_progress(0.60, "Synchronisation en direct avec les serveurs Warframe..."))

        def _bg_init() -> None:
            w_state = fetch_world_state()
            d_state = get_current_duviri_rotation()
            self.after(950, lambda: self._finalize_startup(w_state, d_state))

        threading.Thread(target=_bg_init, daemon=True).start()

    def _finalize_startup(self, w_state: dict, d_state: dict) -> None:
        self._apply_fetched_data(w_state, d_state)
        self.sidebar.select_tab("welcome")
        self.splash.set_progress(1.0, "Prêt ! Ouverture de WireFrame...")

    def _on_splash_finished(self) -> None:
        """Affiche la fenêtre principale une fois le Splash Screen terminé."""
        self.deiconify()
        self.after(40, self._apply_native_dwm_rounding)
        self._tick_timers()
        self._check_sidebar_hover()

    def toggle_sidebar(self) -> None:
        """Bascule manuellement l'état déployé/rangé de la colonne de gauche."""
        self.sidebar.set_collapsed(not self.sidebar.is_collapsed)

    def _check_sidebar_hover(self) -> None:
        """Déploie la colonne de gauche quand la souris la survole, et la range dès qu'elle la quitte."""
        try:
            if self.state() == "normal":
                rel_x = self.winfo_pointerx() - self.winfo_rootx()
                rel_y = self.winfo_pointery() - self.winfo_rooty()
                win_h = self.winfo_height()
                threshold = 68 if self.sidebar.is_collapsed else 230
                inside_sidebar = (0 <= rel_x <= threshold) and (44 <= rel_y <= win_h)
                self.sidebar.set_collapsed(not inside_sidebar)
        except Exception:
            pass
        self.after(70, self._check_sidebar_hover)

    def _apply_native_dwm_rounding(self) -> None:
        try:
            dwmapi = ctypes.windll.dwmapi
            user32 = ctypes.windll.user32
            for hwnd in (self.winfo_id(), user32.GetParent(self.winfo_id())):
                if hwnd:
                    dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(corner_pref := ctypes.c_int(2)), 4)
                    dwmapi.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(ctypes.c_int(0x00462F23)), 4)
        except Exception:
            pass

    def show_view(self, view_key: str) -> None:
        self.current_view_key = view_key
        for key, frame in self.views.items():
            if key == view_key:
                frame.grid(row=0, column=0, sticky="nsew", padx=18, pady=18)
            else:
                frame.grid_forget()

    def show_in_app_toast(self, title: str, message: str) -> None:
        if self._toast_frame and self._toast_frame.winfo_exists():
            self._toast_frame.destroy()

        toast = ctk.CTkFrame(
            self.center_container, corner_radius=10, fg_color="#172542", border_width=2, border_color="#E5C158"
        )
        toast.place(relx=0.5, rely=0.03, anchor="n", relwidth=0.92)
        toast.lift()

        ctk.CTkLabel(
            toast, text=f"🔔  {title}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#E5C158", anchor="w"
        ).pack(fill="x", padx=16, pady=(8, 2))
        ctk.CTkLabel(
            toast, text=message, font=ctk.CTkFont(size=12), text_color="#FFFFFF", anchor="w"
        ).pack(fill="x", padx=16, pady=(0, 8))

        self._toast_frame = toast
        self.after(5000, lambda: toast.destroy() if toast.winfo_exists() else None)

    def apply_language(self) -> None:
        self.sidebar.update_language()
        self.live_panel.update_language()
        for view in self.views.values():
            if hasattr(view, "update_language"):
                view.update_language()

    def apply_center_zoom(self, scale: float) -> None:
        for view in self.views.values():
            if hasattr(view, "apply_zoom"):
                view.apply_zoom(scale)

    def refresh_all_data(self, show_overlay: bool = False) -> None:
        """Actualise les données en tâche de fond avec écran de chargement interne optionnel."""
        if self._is_refreshing:
            return
        self._is_refreshing = True

        if show_overlay:
            self.in_app_loader.show_loading("Synchronisation en direct avec Warframe...")

        def _worker() -> None:
            w_state = fetch_world_state()
            d_state = get_current_duviri_rotation()
            delay = 450 if show_overlay else 0
            self.after(delay, lambda: self._apply_fetched_data(w_state, d_state))

        threading.Thread(target=_worker, daemon=True).start()

    def _apply_fetched_data(self, w_state: dict, d_state: dict) -> None:
        self.world_state = w_state
        self.duviri_state = d_state
        self._is_refreshing = False
        self.in_app_loader.hide_loading()

        self.notif_manager.check_transitions(self.world_state, self.duviri_state)
        self.sidebar.update_status(self.world_state.get("source", "Live"))
        self.live_panel.load_state(self.world_state, self.duviri_state)

        for view in self.views.values():
            if hasattr(view, "load_state"):
                view.load_state(self.world_state, self.duviri_state)
            if hasattr(view, "refresh_history"):
                view.refresh_history()

    def _tick_timers(self) -> None:
        self.live_panel.update_timers()
        active_view = self.views.get(self.current_view_key)
        if active_view and hasattr(active_view, "update_timers"):
            active_view.update_timers()

        self._tick_counter += 1
        cetus_rem = get_remaining_seconds(self.world_state.get("cetus", {}).get("expiry", ""))
        vallis_rem = get_remaining_seconds(self.world_state.get("vallis", {}).get("expiry", ""))
        if self._tick_counter >= 60 or cetus_rem == 1 or vallis_rem == 1:
            self._tick_counter = 0
            self.after(1500, lambda: self.refresh_all_data(show_overlay=False))

        self.after(1000, self._tick_timers)
