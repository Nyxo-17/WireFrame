"""Module codex_view : Vue réutilisable avec recherche instantanée (Ressources, Mods, Warframes)."""

import customtkinter as ctk
from core.codex_service import search_codex_items
from core.i18n import tr


class CodexView(ctk.CTkFrame):
    """Encyclopédie interactive filtrable en temps réel pour Ressources, Mods ou Warframes."""

    def __init__(self, master: ctk.CTkBaseClass, category_key: str, title_tr_key: str) -> None:
        super().__init__(master, fg_color="transparent")
        self.category_key = category_key
        self.title_tr_key = title_tr_key
        self.current_scale: float = 1.0

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_search_bar()
        self._build_results_area()
        self.refresh_results()

    def _build_header(self) -> None:
        self.title_lbl = ctk.CTkLabel(
            self,
            text=tr(self.title_tr_key),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        self.title_lbl.grid(row=0, column=0, padx=4, pady=(0, 10), sticky="ew")

    def _build_search_bar(self) -> None:
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.grid(row=1, column=0, pady=(0, 12), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=tr("search_placeholder"),
            height=38,
            corner_radius=8,
            fg_color="#131B2E",
            border_width=1,
            border_color="#2A3B5C",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13),
        )
        self.search_entry.grid(row=0, column=0, padx=(4, 8), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda _e: self.refresh_results())

        self.count_badge = ctk.CTkLabel(
            search_frame,
            text="0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#58A6FF",
            fg_color="#141A29",
            corner_radius=6,
            padx=10,
            pady=6,
        )
        self.count_badge.grid(row=0, column=1, padx=4)

    def _build_results_area(self) -> None:
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="#111624",
            border_width=1,
            border_color="#1F293D",
            corner_radius=10,
        )
        self.scroll.grid(row=2, column=0, sticky="nsew")
        self.scroll.grid_columnconfigure(0, weight=1)

    def refresh_results(self) -> None:
        """Filtre les éléments selon la saisie dans la barre de recherche et construit les cartes."""
        for child in self.scroll.winfo_children():
            child.destroy()

        query = self.search_entry.get() if hasattr(self, "search_entry") else ""
        items = search_codex_items(self.category_key, query)
        self.count_badge.configure(text=f"{len(items)} résultats")

        s = self.current_scale
        for idx, item in enumerate(items):
            card = ctk.CTkFrame(
                self.scroll,
                corner_radius=8,
                fg_color="#151C2E",
                border_width=1,
                border_color="#23304C",
            )
            card.grid(row=idx, column=0, padx=8, pady=5, sticky="ew")
            card.grid_columnconfigure(0, weight=1)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.grid(row=0, column=0, padx=12, pady=(8, 2), sticky="ew")
            top.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                top,
                text=item.get("name", ""),
                font=ctk.CTkFont(size=int(15 * s), weight="bold"),
                text_color="#58A6FF",
                anchor="w",
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                top,
                text=item.get("category", ""),
                font=ctk.CTkFont(size=int(11 * s), weight="bold"),
                text_color="#E5C158",
                fg_color="#232016",
                corner_radius=5,
                padx=8,
                pady=2,
            ).grid(row=0, column=1, sticky="e")

            loc_txt = f"{tr('lbl_location')} {item.get('location', '')}"
            ctk.CTkLabel(
                card,
                text=loc_txt,
                font=ctk.CTkFont(size=int(12 * s), weight="bold"),
                text_color="#D0D7DE",
                anchor="w",
            ).grid(row=1, column=0, padx=12, pady=1, sticky="ew")

            drop_txt = f"{tr('lbl_drop_method')} {item.get('drop', '')}"
            ctk.CTkLabel(
                card,
                text=drop_txt,
                font=ctk.CTkFont(size=int(12 * s)),
                text_color="#8B949E",
                anchor="w",
                justify="left",
                wraplength=int(560 * s),
            ).grid(row=2, column=0, padx=12, pady=(1, 8), sticky="ew")

    def update_language(self) -> None:
        self.title_lbl.configure(text=tr(self.title_tr_key))
        self.search_entry.configure(placeholder_text=tr("search_placeholder"))
        self.refresh_results()

    def apply_zoom(self, scale: float) -> None:
        self.current_scale = scale
        self.title_lbl.configure(font=ctk.CTkFont(size=int(22 * scale), weight="bold"))
        self.search_entry.configure(font=ctk.CTkFont(size=int(13 * scale)))
        self.refresh_results()
