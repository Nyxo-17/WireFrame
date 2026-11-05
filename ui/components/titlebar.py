"""Module titlebar : Barre de titre personnalisée sombre (sans la barre blanche Windows)."""

import webbrowser
import customtkinter as ctk


class CustomTitleBar(ctk.CTkFrame):
    """Barre supérieure sombre avec titre WireFrame, FR/EN, Zoom, Discord et boutons — ▢ ✕."""

    def __init__(self, master: ctk.CTk) -> None:
        super().__init__(
            master,
            height=44,
            corner_radius=0,
            fg_color="#0D111A",
            border_width=1,
            border_color="#1A2234",
        )
        self.app = master
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        # Variables pour le déplacement de la fenêtre à la souris et l'état agrandi/zoom
        self._drag_x = 0
        self._drag_y = 0
        self._is_maximized = False
        self._normal_geometry = "1280x720+100+80"
        self._zoom_level = 100

        self._build_left_title()
        self._build_right_controls()
        self._bind_drag_events()

    def _build_left_title(self) -> None:
        """Affiche le titre 'WireFrame' à gauche de la barre."""
        self.title_lbl = ctk.CTkLabel(
            self,
            text="WireFrame",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#F0F6FC",
        )
        self.title_lbl.grid(row=0, column=0, padx=18, pady=8, sticky="w")

        # Zone vide centrale qui permet de déplacer la fenêtre à la souris
        self.drag_space = ctk.CTkLabel(self, text="", fg_color="transparent")
        self.drag_space.grid(row=0, column=1, sticky="nsew")

    def _build_right_controls(self) -> None:
        """Construit les capsules [FR|EN], [🔍 100%], [Discord] et les boutons [— ▢ ✕]."""
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=2, padx=(0, 6), pady=5, sticky="e")

        # 1. Sélecteur [ 🌐 FR | EN ]
        lang_box = ctk.CTkFrame(
            right, fg_color="#131926", corner_radius=6, border_width=1, border_color="#232F46"
        )
        lang_box.grid(row=0, column=0, padx=5, pady=2)
        ctk.CTkLabel(lang_box, text="🌐", font=ctk.CTkFont(size=11), text_color="#58A6FF").grid(
            row=0, column=0, padx=(8, 4), pady=3
        )
        ctk.CTkLabel(
            lang_box,
            text="FR",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#FFFFFF",
            fg_color="#1F2D48",
            corner_radius=4,
            padx=6,
            pady=1,
        ).grid(row=0, column=1, padx=2, pady=3)
        ctk.CTkLabel(
            lang_box, text="EN", font=ctk.CTkFont(size=11, weight="bold"), text_color="#7D8590"
        ).grid(row=0, column=2, padx=(4, 8), pady=3)

        # 2. Sélecteur de zoom [ 🔍- 100% 🔍+ ]
        zoom_box = ctk.CTkFrame(
            right, fg_color="#131926", corner_radius=6, border_width=1, border_color="#232F46"
        )
        zoom_box.grid(row=0, column=1, padx=5, pady=2)
        ctk.CTkButton(
            zoom_box,
            text="🔍-",
            width=28,
            height=24,
            fg_color="transparent",
            hover_color="#1F2D48",
            text_color="#8B949E",
            font=ctk.CTkFont(size=11),
            command=lambda: self._change_zoom(-10),
        ).grid(row=0, column=0, padx=(4, 2), pady=2)

        self.zoom_lbl = ctk.CTkLabel(
            zoom_box,
            text="100%",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#FFFFFF",
            width=38,
        )
        self.zoom_lbl.grid(row=0, column=1, padx=2, pady=2)

        ctk.CTkButton(
            zoom_box,
            text="🔍+",
            width=28,
            height=24,
            fg_color="transparent",
            hover_color="#1F2D48",
            text_color="#8B949E",
            font=ctk.CTkFont(size=11),
            command=lambda: self._change_zoom(10),
        ).grid(row=0, column=2, padx=(2, 4), pady=2)

        # 3. Bouton [ 💬 Discord ]
        discord_btn = ctk.CTkButton(
            right,
            text="💬  Discord",
            width=92,
            height=28,
            corner_radius=6,
            fg_color="#131926",
            border_width=1,
            border_color="#232F46",
            hover_color="#1F2D48",
            text_color="#D0D7DE",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: webbrowser.open("https://github.com/Nyxo-17"),
        )
        discord_btn.grid(row=0, column=2, padx=(5, 10), pady=2)

        # 4. Boutons fenêtre Windows : — (Réduire), ▢ (Agrandir), ✕ (Fermer)
        for col, txt, hover_bg, cmd in [
            (3, "—", "#1F2937", self._minimize_window),
            (4, "▢", "#1F2937", self._toggle_maximize),
            (5, "✕", "#DA3633", self.app.destroy),
        ]:
            ctk.CTkButton(
                right,
                text=txt,
                width=34,
                height=28,
                corner_radius=5,
                fg_color="transparent",
                hover_color=hover_bg,
                text_color="#8B949E",
                font=ctk.CTkFont(size=13),
                command=cmd,
            ).grid(row=0, column=col, padx=1)

    def _bind_drag_events(self) -> None:
        """Permet de déplacer la fenêtre en maintenant le clic gauche sur la barre du haut."""
        for widget in (self, self.title_lbl, self.drag_space):
            widget.bind("<ButtonPress-1>", self._start_move)
            widget.bind("<B1-Motion>", self._do_move)
            widget.bind("<Double-Button-1>", lambda _e: self._toggle_maximize())

    def _start_move(self, event) -> None:
        self._drag_x = event.x_root - self.app.winfo_x()
        self._drag_y = event.y_root - self.app.winfo_y()

    def _do_move(self, event) -> None:
        if self._is_maximized:
            return
        new_x = event.x_root - self._drag_x
        new_y = event.y_root - self._drag_y
        self.app.geometry(f"+{new_x}+{new_y}")

    def _minimize_window(self) -> None:
        """Réduit temporairement la fenêtre dans la barre des tâches Windows."""
        self.app.overrideredirect(False)
        self.app.iconify()
        self.app.bind("<Map>", self._restore_from_minimize)

    def _restore_from_minimize(self, _event) -> None:
        if self.app.state() == "normal":
            self.app.overrideredirect(True)
            self.app.unbind("<Map>")

    def _toggle_maximize(self) -> None:
        """Bascule entre le mode plein écran fenêtré et la taille normale."""
        if not self._is_maximized:
            self._normal_geometry = self.app.geometry()
            w, h = self.app.winfo_screenwidth(), self.app.winfo_screenheight() - 40
            self.app.geometry(f"{w}x{h}+0+0")
            self._is_maximized = True
        else:
            self.app.geometry(self._normal_geometry)
            self._is_maximized = False

    def _change_zoom(self, delta: int) -> None:
        """Ajuste le niveau de zoom global de l'interface entre 80% et 120%."""
        self._zoom_level = max(80, min(120, self._zoom_level + delta))
        self.zoom_lbl.configure(text=f"{self._zoom_level}%")
        ctk.set_widget_scaling(self._zoom_level / 100.0)
