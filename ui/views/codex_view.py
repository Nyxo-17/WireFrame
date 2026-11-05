"""Module codex_view : Vue paginée avec images officielles et recherche (1442 Mods, 239 Ressources, 120 Warframes)."""

import math
import customtkinter as ctk
from PIL import Image
from core.codex_service import search_codex_items
from core.i18n import tr
from core.image_loader import fetch_item_image_async

ITEMS_PER_PAGE = 20


class CodexView(ctk.CTkFrame):
    """Encyclopédie interactive avec recherche instantanée, pagination et images officielles CDN."""

    def __init__(self, master: ctk.CTkBaseClass, category_key: str, title_tr_key: str) -> None:
        super().__init__(master, fg_color="transparent")
        self.category_key = category_key
        self.title_tr_key = title_tr_key
        self.current_scale: float = 1.0
        self.current_page: int = 1
        self.total_pages: int = 1
        self.filtered_items: list[dict[str, str]] = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_search_and_pagination()
        self._build_results_area()
        self.on_search_changed()

    def _build_header(self) -> None:
        self.title_lbl = ctk.CTkLabel(
            self,
            text=tr(self.title_tr_key),
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        self.title_lbl.grid(row=0, column=0, padx=4, pady=(0, 8), sticky="ew")

    def _build_search_and_pagination(self) -> None:
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        bar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            bar,
            placeholder_text=tr("search_placeholder"),
            height=36,
            corner_radius=8,
            fg_color="#131B2E",
            border_width=1,
            border_color="#2A3B5C",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13),
        )
        self.search_entry.grid(row=0, column=0, padx=(4, 8), sticky="ew")
        self.search_entry.bind("<KeyRelease>", lambda _e: self.on_search_changed())

        self.count_badge = ctk.CTkLabel(
            bar,
            text="0",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#58A6FF",
            fg_color="#141A29",
            corner_radius=6,
            padx=10,
            pady=5,
        )
        self.count_badge.grid(row=0, column=1, padx=4)

        # Contrôles de pagination [ ◀ ] Page X/Y [ ▶ ]
        self.prev_btn = ctk.CTkButton(
            bar,
            text="◀",
            width=32,
            height=30,
            corner_radius=6,
            fg_color="#161E31",
            hover_color="#233252",
            command=lambda: self.change_page(-1),
        )
        self.prev_btn.grid(row=0, column=2, padx=2)

        self.page_lbl = ctk.CTkLabel(
            bar, text="1 / 1", font=ctk.CTkFont(size=12, weight="bold"), text_color="#D0D7DE", width=64
        )
        self.page_lbl.grid(row=0, column=3, padx=4)

        self.next_btn = ctk.CTkButton(
            bar,
            text="▶",
            width=32,
            height=30,
            corner_radius=6,
            fg_color="#161E31",
            hover_color="#233252",
            command=lambda: self.change_page(1),
        )
        self.next_btn.grid(row=0, column=4, padx=(2, 4))

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

    def on_search_changed(self) -> None:
        """Recalcule la liste filtrée et revient à la page 1."""
        query = self.search_entry.get() if hasattr(self, "search_entry") else ""
        self.filtered_items = search_codex_items(self.category_key, query)
        self.total_pages = max(1, math.ceil(len(self.filtered_items) / ITEMS_PER_PAGE))
        self.current_page = 1
        self.render_current_page()

    def change_page(self, delta: int) -> None:
        new_page = max(1, min(self.total_pages, self.current_page + delta))
        if new_page != self.current_page:
            self.current_page = new_page
            self.render_current_page()

    def render_current_page(self) -> None:
        """Affiche les 20 éléments de la page active avec leurs images officielles."""
        for child in self.scroll.winfo_children():
            child.destroy()

        total = len(self.filtered_items)
        self.count_badge.configure(text=f"{total} objets")
        self.page_lbl.configure(text=f"{self.current_page} / {self.total_pages}")

        start = (self.current_page - 1) * ITEMS_PER_PAGE
        page_items = self.filtered_items[start : start + ITEMS_PER_PAGE]

        s = self.current_scale
        img_sz = max(44, int(56 * s))

        for idx, item in enumerate(page_items):
            card = ctk.CTkFrame(
                self.scroll, corner_radius=8, fg_color="#151C2E", border_width=1, border_color="#23304C"
            )
            card.grid(row=idx, column=0, padx=8, pady=5, sticky="ew")
            card.grid_columnconfigure(1, weight=1)

            # Vignette image officielle à gauche
            img_label = ctk.CTkLabel(card, text="", width=img_sz, height=img_sz)
            img_label.grid(row=0, column=0, rowspan=3, padx=(10, 8), pady=8, sticky="n")

            def _update_img(pil_img: Image.Image, lbl: ctk.CTkLabel = img_label, sz: int = img_sz) -> None:
                if lbl.winfo_exists():
                    lbl.configure(image=ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(sz, sz)))

            initial_pil = fetch_item_image_async(
                item.get("image", ""),
                img_sz,
                on_ready=lambda pil_img, cb=_update_img: self.after(0, lambda: cb(pil_img)),
            )
            _update_img(initial_pil)

            # Colonne de droite alignée au pixel près (Nom, Où trouver, Comment l'avoir)
            info_col = ctk.CTkFrame(card, fg_color="transparent")
            info_col.grid(row=0, column=1, rowspan=3, padx=(4, 12), pady=8, sticky="nsew")
            info_col.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                info_col,
                text=item.get("name", ""),
                font=ctk.CTkFont(size=int(15 * s), weight="bold"),
                text_color="#58A6FF",
                anchor="w",
                justify="left",
            ).grid(row=0, column=0, sticky="w")

            ctk.CTkLabel(
                info_col,
                text=item.get("category", ""),
                font=ctk.CTkFont(size=int(11 * s), weight="bold"),
                text_color="#E5C158",
                fg_color="#232016",
                corner_radius=5,
                padx=8,
                pady=2,
            ).grid(row=0, column=1, padx=(8, 0), sticky="e")

            ctk.CTkLabel(
                info_col,
                text=f"{tr('lbl_location')} {item.get('location', '')}",
                font=ctk.CTkFont(size=int(12 * s), weight="bold"),
                text_color="#D0D7DE",
                anchor="w",
                justify="left",
            ).grid(row=1, column=0, columnspan=2, pady=(3, 1), sticky="w")

            ctk.CTkLabel(
                info_col,
                text=f"{tr('lbl_drop_method')} {item.get('drop', '')}",
                font=ctk.CTkFont(size=int(11 * s)),
                text_color="#8B949E",
                anchor="w",
                justify="left",
                wraplength=int(480 * s),
            ).grid(row=2, column=0, columnspan=2, pady=(1, 0), sticky="w")

    def update_language(self) -> None:
        self.title_lbl.configure(text=tr(self.title_tr_key))
        self.search_entry.configure(placeholder_text=tr("search_placeholder"))
        self.render_current_page()

    def apply_zoom(self, scale: float) -> None:
        self.current_scale = scale
        self.title_lbl.configure(font=ctk.CTkFont(size=int(22 * scale), weight="bold"))
        self.search_entry.configure(font=ctk.CTkFont(size=int(13 * scale)))
        self.render_current_page()
