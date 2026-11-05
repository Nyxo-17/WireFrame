"""Module loading_screens : Splash Screen de lancement et Overlay de chargement interne."""

import ctypes
from pathlib import Path
from typing import Callable
import customtkinter as ctk
from PIL import Image

LOGO_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "app_logo.png"


class SplashScreen(ctk.CTkToplevel):
    """Écran de démarrage animé avec le logo doré WireFrame et barre de progression."""

    def __init__(self, master: ctk.CTk, on_complete: Callable[[], None]) -> None:
        super().__init__(master)
        self.on_complete = on_complete

        # Dimensions et centrage parfait au milieu de l'écran Windows
        width, height = 480, 310
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color="#090C14")
        self.after(30, self._apply_dwm_rounding)

        # Cadre principal avec bordure dorée/bleutée
        card = ctk.CTkFrame(
            self,
            corner_radius=14,
            fg_color="#0E131F",
            border_width=1,
            border_color="#2A3B5C",
        )
        card.pack(fill="both", expand=True, padx=2, pady=2)

        # Logo officiel au centre
        if LOGO_PATH.exists():
            pil_img = Image.open(LOGO_PATH)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(88, 88))
            ctk.CTkLabel(card, text="", image=ctk_img).pack(pady=(28, 10))
        else:
            ctk.CTkLabel(
                card, text="❖", font=ctk.CTkFont(size=48, weight="bold"), text_color="#E5C158"
            ).pack(pady=(28, 10))

        ctk.CTkLabel(
            card,
            text="WIREFRAME",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#F0F6FC",
        ).pack(pady=(0, 2))

        ctk.CTkLabel(
            card,
            text="Compagnon Warframe • Créé par Nyxo_17",
            font=ctk.CTkFont(size=12),
            text_color="#E5C158",
        ).pack(pady=(0, 22))

        self.step_label = ctk.CTkLabel(
            card,
            text="Initialisation des systèmes...",
            font=ctk.CTkFont(size=12),
            text_color="#8B949E",
        )
        self.step_label.pack(pady=(0, 8))

        self.progress = ctk.CTkProgressBar(
            card,
            width=360,
            height=8,
            corner_radius=4,
            fg_color="#161E31",
            progress_color="#3B82F6",
        )
        self.progress.pack(pady=(0, 20))
        self.progress.set(0.05)

    def _apply_dwm_rounding(self) -> None:
        try:
            dwmapi = ctypes.windll.dwmapi
            user32 = ctypes.windll.user32
            for hwnd in (self.winfo_id(), user32.GetParent(self.winfo_id())):
                if hwnd:
                    dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(ctypes.c_int(2)), 4)
                    dwmapi.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(ctypes.c_int(0x005C3B2A)), 4)
        except Exception:
            pass

    def set_progress(self, value: float, status_text: str) -> None:
        """Met à jour la barre de progression (0.0 à 1.0) et le texte d'étape."""
        if not self.winfo_exists():
            return
        self.progress.set(value)
        self.step_label.configure(text=status_text)
        if value >= 1.0:
            self.after(250, self._finish)

    def _finish(self) -> None:
        if self.winfo_exists():
            self.destroy()
        self.on_complete()


class InAppLoader(ctk.CTkFrame):
    """Écran de chargement superposé dans le cadre central lors d'une synchronisation."""

    def __init__(self, master: ctk.CTkBaseClass) -> None:
        super().__init__(
            master,
            corner_radius=12,
            fg_color="#111726",
            border_width=1,
            border_color="#3B82F6",
        )
        inner = ctk.CTkFrame(self, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")

        if LOGO_PATH.exists():
            pil_img = Image.open(LOGO_PATH)
            ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(54, 54))
            ctk.CTkLabel(inner, text="", image=ctk_img).pack(pady=(16, 8))

        self.msg_label = ctk.CTkLabel(
            inner,
            text="Synchronisation en direct avec Warframe...",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F0F6FC",
        )
        self.msg_label.pack(padx=28, pady=(0, 10))

        self.bar = ctk.CTkProgressBar(
            inner,
            width=240,
            height=6,
            corner_radius=3,
            fg_color="#1A243B",
            progress_color="#3B82F6",
            mode="indeterminate",
        )
        self.bar.pack(padx=28, pady=(0, 18))

    def show_loading(self, text: str = "Synchronisation en direct avec Warframe...") -> None:
        """Affiche l'overlay au centre de la vue active et démarre l'animation."""
        self.msg_label.configure(text=text)
        self.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.55, relheight=0.34)
        self.lift()
        self.bar.start()

    def hide_loading(self) -> None:
        """Arrête l'animation et masque l'overlay."""
        self.bar.stop()
        self.place_forget()

