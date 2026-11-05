"""Module sidebar : Barre latérale coulissante à 90 FPS avec alignement symétrique parfait (64px / 225px)."""

from pathlib import Path
from typing import Callable
import customtkinter as ctk
from PIL import Image
from core.i18n import tr

LOGO_PATH = Path(__file__).resolve().parent.parent / "data" / "app_logo.png"

EXPANDED_WIDTH = 225
COLLAPSED_WIDTH = 64
BTN_COLLAPSED_W = COLLAPSED_WIDTH - 16  # 48px (8px marge gauche + 48px bouton + 8px marge droite = 64px)
BTN_EXPANDED_W = EXPANDED_WIDTH - 16    # 209px

NAV_ITEMS_CONFIG = [
    ("welcome", "🏠", "nav_welcome", 2),
    ("notifications", "🔔", "nav_notifications", 3),
    ("resources", "💎", "nav_resources", 5),
    ("mods", "🃏", "nav_mods", 6),
    ("warframes", "⚡", "nav_warframes", 7),
    ("worlds", "🌍", "nav_worlds", 9),
    ("bounties", "🎯", "nav_bounties", 10),
    ("duviri", "🌀", "nav_duviri", 11),
    ("baro", "💠", "nav_baro", 12),
]


def _clean_label(raw_text: str) -> str:
    parts = raw_text.split("   ", 1)
    return parts[1].strip() if len(parts) > 1 else raw_text.strip()


class Sidebar(ctk.CTkFrame):
    """Menu latéral en surcouche avec boutons 48x36 fermés en mode réduit et glissement Ease-Out."""

    def __init__(
        self,
        master: ctk.CTkBaseClass,
        on_navigate: Callable[[str], None],
        on_refresh: Callable[[], None],
    ) -> None:
        super().__init__(
            master,
            width=COLLAPSED_WIDTH,
            corner_radius=0,
            fg_color="#0D111A",
            border_width=1,
            border_color="#1A2234",
        )
        self.grid_propagate(False)
        self.pack_propagate(False)

        self.on_navigate = on_navigate
        self.on_refresh = on_refresh
        self.is_collapsed: bool = True
        self.active_key: str = "welcome"

        self._current_w: float = float(COLLAPSED_WIDTH)
        self._target_w: float = float(COLLAPSED_WIDTH)
        self._anim_running: bool = False
        self._headers_visible: bool = False

        # Conteneur interne fixe pour éviter tout recalcul de hauteur de ligne
        self.inner = ctk.CTkFrame(self, width=EXPANDED_WIDTH, corner_radius=0, fg_color="transparent")
        self.inner.place(x=0, y=2, relheight=0.99)
        self.inner.grid_propagate(False)
        self.inner.grid_columnconfigure(0, weight=1)
        self.inner.grid_rowconfigure(15, weight=1)

        self.nav_rows: dict[str, ctk.CTkFrame] = {}
        self.nav_labels: dict[str, tuple[ctk.CTkLabel, str]] = {}

        self._build_creator_badge()
        self._build_navigation()
        self._build_footer()

    def _build_creator_badge(self) -> None:
        self.profile_box = ctk.CTkFrame(self.inner, fg_color="transparent")
        # 12px gauche + 40px logo + 14px écart = le texte commence à x=66px (invisible quand replié à 64px)
        self.profile_box.grid(row=0, column=0, padx=(12, 8), pady=(12, 8), sticky="ew")
        self.profile_box.grid_columnconfigure(1, weight=1)

        if LOGO_PATH.exists():
            pil_logo = Image.open(LOGO_PATH)
            ctk_logo = ctk.CTkImage(light_image=pil_logo, dark_image=pil_logo, size=(40, 40))
            self.emblem = ctk.CTkLabel(
                self.profile_box, text="", image=ctk_logo, width=40, height=40
            )
        else:
            self.emblem = ctk.CTkLabel(
                self.profile_box,
                text="❖",
                width=40,
                height=40,
                corner_radius=6,
                fg_color="#2A2415",
                text_color="#E5C158",
                font=ctk.CTkFont(size=20, weight="bold"),
            )
        self.emblem.grid(row=0, column=0, rowspan=2, padx=(0, 14), sticky="w")

        self.name_lbl = ctk.CTkLabel(
            self.profile_box,
            text="Nyxo_17",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#F0F6FC",
            anchor="w",
        )
        self.name_lbl.grid(row=0, column=1, sticky="ew")

        self.role_lbl = ctk.CTkLabel(
            self.profile_box,
            text=tr("creator_role"),
            font=ctk.CTkFont(size=11),
            text_color="#7D8590",
            anchor="w",
        )
        self.role_lbl.grid(row=1, column=1, sticky="ew")

    def _build_navigation(self) -> None:
        self.sec_home_lbl = self._make_section_header("sec_home", row=1)
        self.sec_inv_lbl = self._make_section_header("sec_inventory", row=4)
        self.sec_cycles_lbl = self._make_section_header("sec_cycles", row=8)

        for key, icon, tr_key, row_idx in NAV_ITEMS_CONFIG:
            self._create_aligned_nav_item(key, icon, tr_key, row_idx)

    def _make_section_header(self, tr_key: str, row: int) -> ctk.CTkLabel:
        lbl = ctk.CTkLabel(
            self.inner,
            text=tr(tr_key),
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#0D111A",  # Masqué par défaut en mode réduit (même couleur que le fond)
            anchor="w",
        )
        lbl.grid(row=row, column=0, padx=14, pady=(10, 2), sticky="w")
        return lbl

    def _create_aligned_nav_item(self, key: str, icon: str, tr_key: str, row: int) -> None:
        item_frame = ctk.CTkFrame(
            self.inner,
            width=BTN_COLLAPSED_W,
            height=36,
            corner_radius=7,
            border_width=1,
            border_color="#0D111A",
            fg_color="transparent",
            cursor="hand2",
        )
        item_frame.grid(row=row, column=0, padx=8, pady=2, sticky="w")
        item_frame.grid_propagate(False)
        item_frame.grid_columnconfigure(0, minsize=46, weight=0)
        item_frame.grid_columnconfigure(1, weight=1)
        item_frame.grid_rowconfigure(0, weight=1)

        icon_lbl = ctk.CTkLabel(
            item_frame,
            text=icon,
            width=46,
            font=ctk.CTkFont(size=14),
            text_color="#B1BAC4",
            anchor="center",
        )
        icon_lbl.grid(row=0, column=0, padx=(1, 1), sticky="ns")

        # Le texte commence à x = 8 + 48 + 8 = 64px (totalement hors du bouton de 48px quand replié)
        text_lbl = ctk.CTkLabel(
            item_frame,
            text=_clean_label(tr(tr_key)),
            font=ctk.CTkFont(size=13),
            text_color="#B1BAC4",
            anchor="w",
        )
        text_lbl.grid(row=0, column=1, padx=(8, 8), sticky="nsew")

        for widget in (item_frame, icon_lbl, text_lbl):
            widget.bind("<Button-1>", lambda _e, k=key: self.select_tab(k))
            widget.bind("<Enter>", lambda _e, k=key: self._on_hover(k, True))
            widget.bind("<Leave>", lambda _e, k=key: self._on_hover(k, False))

        self.nav_rows[key] = item_frame
        self.nav_labels[key] = (text_lbl, tr_key)

    def _on_hover(self, key: str, entering: bool) -> None:
        frame = self.nav_rows.get(key)
        if not frame or key == self.active_key:
            return
        frame.configure(fg_color="#161E2E" if entering else "transparent")

    def _build_footer(self) -> None:
        self.status_label = ctk.CTkLabel(
            self.inner,
            text="📡 ...",
            font=ctk.CTkFont(size=11),
            text_color="#0D111A",
            anchor="w",
        )
        self.status_label.grid(row=16, column=0, padx=14, pady=(4, 4), sticky="w")

        # Bouton Actualiser construit avec la même grille 2 colonnes (48px fermé / 209px ouvert)
        self.refresh_frame = ctk.CTkFrame(
            self.inner,
            width=BTN_COLLAPSED_W,
            height=36,
            corner_radius=7,
            fg_color="#161E31",
            border_width=1,
            border_color="#2A3B5C",
            cursor="hand2",
        )
        self.refresh_frame.grid(row=17, column=0, padx=8, pady=(0, 56), sticky="w")
        self.refresh_frame.grid_propagate(False)
        self.refresh_frame.grid_columnconfigure(0, minsize=46, weight=0)
        self.refresh_frame.grid_columnconfigure(1, weight=1)
        self.refresh_frame.grid_rowconfigure(0, weight=1)

        self.refresh_icon_lbl = ctk.CTkLabel(
            self.refresh_frame,
            text="🔄",
            width=46,
            font=ctk.CTkFont(size=13),
            text_color="#58A6FF",
            anchor="center",
        )
        self.refresh_icon_lbl.grid(row=0, column=0, padx=(1, 1), sticky="ns")

        clean_ref = tr("btn_refresh").replace("🔄", "").strip()
        self.refresh_text_lbl = ctk.CTkLabel(
            self.refresh_frame,
            text=clean_ref,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#58A6FF",
            anchor="w",
        )
        self.refresh_text_lbl.grid(row=0, column=1, padx=(8, 8), sticky="nsew")

        for w in (self.refresh_frame, self.refresh_icon_lbl, self.refresh_text_lbl):
            w.bind("<Button-1>", lambda _e: self.on_refresh())
            w.bind("<Enter>", lambda _e: self.refresh_frame.configure(fg_color="#1F2D4A"))
            w.bind("<Leave>", lambda _e: self.refresh_frame.configure(fg_color="#161E31"))

    def _set_headers_visibility(self, visible: bool) -> None:
        if self._headers_visible == visible:
            return
        self._headers_visible = visible
        sec_col = "#6E7681" if visible else "#0D111A"
        stat_col = "#7D8590" if visible else "#0D111A"
        self.sec_home_lbl.configure(text_color=sec_col)
        self.sec_inv_lbl.configure(text_color=sec_col)
        self.sec_cycles_lbl.configure(text_color=sec_col)
        self.status_label.configure(text_color=stat_col)

    def set_collapsed(self, collapsed: bool) -> None:
        """Lance l'animation fluide vers la largeur cible (64px ou 225px)."""
        if self.is_collapsed == collapsed:
            return
        self.is_collapsed = collapsed
        self._target_w = float(COLLAPSED_WIDTH if collapsed else EXPANDED_WIDTH)
        if not collapsed:
            self.lift()
            # Étend les cadres inactifs immédiatement pour le survol souris
            for k, f in self.nav_rows.items():
                if k != self.active_key:
                    f.configure(width=BTN_EXPANDED_W)
        if not self._anim_running:
            self._anim_running = True
            self._animate_step()

    def _animate_step(self) -> None:
        """Interpolation Ease-Out à ~90 FPS avec bordures de boutons toujours fermées."""
        diff = self._target_w - self._current_w
        if abs(diff) <= 1.5:
            self._current_w = self._target_w
            w_int = int(self._current_w)
            btn_w = max(BTN_COLLAPSED_W, w_int - 16)
            self.configure(width=w_int)
            for f in self.nav_rows.values():
                f.configure(width=btn_w)
            self.refresh_frame.configure(width=btn_w)
            self._set_headers_visibility(w_int >= 135)
            self._anim_running = False
            return

        self._current_w += diff * 0.38
        w_int = int(self._current_w)
        btn_w = max(BTN_COLLAPSED_W, w_int - 16)

        self.configure(width=w_int)
        # Pendant le mouvement, seuls le bouton actif et le bouton actualiser ont une bordure visible
        active_frame = self.nav_rows.get(self.active_key)
        if active_frame:
            active_frame.configure(width=btn_w)
        self.refresh_frame.configure(width=btn_w)
        self._set_headers_visibility(w_int >= 135)

        self.after(11, self._animate_step)

    def select_tab(self, active_key: str) -> None:
        self.active_key = active_key
        btn_w = max(BTN_COLLAPSED_W, int(self._current_w) - 16)
        for key, frame in self.nav_rows.items():
            text_lbl, _ = self.nav_labels[key]
            if key == active_key:
                frame.configure(fg_color="#17223B", border_color="#3B82F6", width=btn_w)
                text_lbl.configure(
                    text_color="#FFFFFF", font=ctk.CTkFont(size=13, weight="bold")
                )
            else:
                frame.configure(fg_color="transparent", border_color="#0D111A", width=btn_w)
                text_lbl.configure(
                    text_color="#B1BAC4", font=ctk.CTkFont(size=13, weight="normal")
                )
        self.on_navigate(active_key)

    def update_status(self, source_text: str) -> None:
        self.status_label.configure(text=f"📡 {source_text}")

    def update_language(self) -> None:
        self.role_lbl.configure(text=tr("creator_role"))
        self.sec_home_lbl.configure(text=tr("sec_home"))
        self.sec_inv_lbl.configure(text=tr("sec_inventory"))
        self.sec_cycles_lbl.configure(text=tr("sec_cycles"))
        clean_ref = tr("btn_refresh").replace("🔄", "").strip()
        self.refresh_text_lbl.configure(text=clean_ref)
        for key, (text_lbl, tr_key) in self.nav_labels.items():
            text_lbl.configure(text=_clean_label(tr(tr_key)))
