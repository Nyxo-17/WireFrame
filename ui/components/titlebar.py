"""Module titlebar : Barre de titre personnalisée sombre avec sélecteur FR/EN et zoom central."""

from typing import Callable
import webbrowser
import customtkinter as ctk
from core.i18n import get_lang, set_lang


class CustomTitleBar(ctk.CTkFrame):
    """Barre supérieure sombre avec titre WireFrame, boutons FR/EN, Zoom central, Discord et — ▢ ✕."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        app: ctk.CTk,
        on_lang_change: Callable[[], None],
        on_zoom_change: Callable[[float], None],
    ) -> None:
        super().__init__(
            master,
            height=44,
            corner_radius=0,
            fg_color="#0D111A",
            border_width=1,
            border_color="#1A2234",
        )
        self.app = app
        self.on_lang_change = on_lang_change
        self.on_zoom_change = on_zoom_change
        self.grid_propagate(False)
        self.grid_columnconfigure(1, weight=1)

        self._drag_x = 0
        self._drag_y = 0
        self._is_maximized = False
        self._normal_geometry = "1280x740+100+60"
        self._zoom_level = 100

        self._build_left_title()
        self._build_right_controls()
        self._bind_drag_events()

    def _build_left_title(self) -> None:
        self.title_lbl = ctk.CTkLabel(
            self,
            text="WireFrame",
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color="#F0F6FC",
        )
        self.title_lbl.grid(row=0, column=0, padx=18, pady=8, sticky="w")

        self.drag_space = ctk.CTkLabel(self, text="", fg_color="transparent")
        self.drag_space.grid(row=0, column=1, sticky="nsew")

    def _build_right_controls(self) -> None:
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=0, column=2, padx=(0, 8), pady=5, sticky="e")

        # 1. Sélecteur interactif [ 🌐 FR | EN ]
        lang_box = ctk.CTkFrame(
            right, fg_color="#131926", corner_radius=6, border_width=1, border_color="#232F46"
        )
        lang_box.grid(row=0, column=0, padx=5, pady=2)
        ctk.CTkLabel(lang_box, text="🌐", font=ctk.CTkFont(size=11), text_color="#58A6FF").grid(
            row=0, column=0, padx=(8, 2), pady=2
        )

        self.fr_btn = ctk.CTkButton(
            lang_box,
            text="FR",
            width=30,
            height=22,
            corner_radius=4,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._switch_language("fr"),
        )
        self.fr_btn.grid(row=0, column=1, padx=2, pady=3)

        self.en_btn = ctk.CTkButton(
            lang_box,
            text="EN",
            width=30,
            height=22,
            corner_radius=4,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=lambda: self._switch_language("en"),
        )
        self.en_btn.grid(row=0, column=2, padx=(2, 6), pady=3)
        self._refresh_lang_buttons()

        # 2. Sélecteur de zoom central [ 🔍- 100% 🔍+ ]
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
        ctk.CTkButton(
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
        ).grid(row=0, column=2, padx=(5, 10), pady=2)

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

    def _switch_language(self, lang_code: str) -> None:
        if get_lang() != lang_code:
            set_lang(lang_code)
            self._refresh_lang_buttons()
            self.on_lang_change()

    def _refresh_lang_buttons(self) -> None:
        is_fr = get_lang() == "fr"
        self.fr_btn.configure(
            fg_color="#253659" if is_fr else "transparent",
            text_color="#FFFFFF" if is_fr else "#7D8590",
            hover_color="#2D426B",
        )
        self.en_btn.configure(
            fg_color="#253659" if not is_fr else "transparent",
            text_color="#FFFFFF" if not is_fr else "#7D8590",
            hover_color="#2D426B",
        )

    def _bind_drag_events(self) -> None:
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
        self.app.geometry(f"+{event.x_root - self._drag_x}+{event.y_root - self._drag_y}")

    def _minimize_window(self) -> None:
        self.app.overrideredirect(False)
        self.app.iconify()
        self.app.bind("<Map>", self._restore_from_minimize)

    def _restore_from_minimize(self, _event) -> None:
        if self.app.state() == "normal":
            self.app.overrideredirect(True)
            self.app.unbind("<Map>")

    def _toggle_maximize(self) -> None:
        if not self._is_maximized:
            self._normal_geometry = self.app.geometry()
            w, h = self.app.winfo_screenwidth(), self.app.winfo_screenheight() - 40
            self.app.geometry(f"{w}x{h}+0+0")
            self._is_maximized = True
        else:
            self.app.geometry(self._normal_geometry)
            self.app.vertical_state = False
            self._is_maximized = False

    def _change_zoom(self, delta: int) -> None:
        """Modifie le zoom (70% à 140%) et l'applique uniquement au conteneur central."""
        self._zoom_level = max(70, min(140, self._zoom_level + delta))
        self.zoom_lbl.configure(text=f"{self._zoom_level}%")
        self.on_zoom_change(self._zoom_level / 100.0)
