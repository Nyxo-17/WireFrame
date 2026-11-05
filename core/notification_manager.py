"""Module notification_manager : Surveillance des cycles et envoi de notifications Windows & UI."""

from datetime import datetime
from pathlib import Path
import subprocess
import threading
from typing import Any, Callable
import winsound
from core.codex_service import get_current_bounty_rotation
from data.data_manager import load_notification_settings, save_notification_settings

DEFAULT_SOUND_FILE = (
    Path(__file__).resolve().parent.parent / "data" / "sounds" / "default_notify.wav"
)


class NotificationManager:
    """Détecte les changements de rotations/cycles et déclenche les alertes configurées."""

    def __init__(self, on_alert_callback: Callable[[str, str], None] | None = None) -> None:
        self.settings: dict[str, bool] = load_notification_settings()
        self.on_alert_callback = on_alert_callback
        self.history: list[dict[str, str]] = []
        self._prev_snapshot: dict[str, Any] = {}

    def update_setting(self, key: str, value: bool) -> None:
        """Met à jour une préférence de notification et la sauvegarde dans settings.json."""
        self.settings[key] = bool(value)
        save_notification_settings(self.settings)

    def check_transitions(self, world_state: dict[str, Any], duviri_state: dict[str, Any]) -> None:
        """Compare l'état actuel avec l'état précédent pour détecter tout changement de cycle."""
        bounty_state = get_current_bounty_rotation()
        current_snap = {
            "cetus": world_state.get("cetus", {}).get("state", ""),
            "vallis": world_state.get("vallis", {}).get("state", ""),
            "cambion": world_state.get("cambion", {}).get("state", ""),
            "earth": world_state.get("earth", {}).get("state", ""),
            "baro_active": bool(world_state.get("baro", {}).get("active", False)),
            "baro_loc": world_state.get("baro", {}).get("location", ""),
            "bounty_rot": bounty_state.get("current_rotation", ""),
            "incarnon_week": duviri_state.get("incarnon_week_number", 0),
            "incarnon_list": ", ".join(duviri_state.get("incarnon_weapons", [])),
            "wf_week": duviri_state.get("warframe_week_number", 0),
            "wf_list": " • ".join(duviri_state.get("warframes", [])),
        }

        if not self._prev_snapshot:
            self._prev_snapshot = current_snap
            return

        # 1. Cycles des Planètes (Jour/Nuit, Chaud/Froid, Fass/Vome)
        if self.settings.get("notify_planets", True):
            planet_names = {
                "cetus": "Terre (Cetus)",
                "vallis": "Orb Vallis (Vénus)",
                "cambion": "Cambion Drift (Deimos)",
                "earth": "Terre (Forêts)",
            }
            for key, label in planet_names.items():
                old_val = self._prev_snapshot.get(key)
                new_val = current_snap.get(key)
                if old_val and new_val and old_val != new_val:
                    self.trigger_notification(
                        f"🌍 Cycle {label}",
                        f"Nouveau cycle en cours : {new_val} (précédent : {old_val})",
                    )

        # 2. Arrivée / Départ du marchand Baro Ki'Teer
        if self.settings.get("notify_baro", True):
            old_baro = self._prev_snapshot.get("baro_active")
            new_baro = current_snap.get("baro_active")
            if old_baro != new_baro:
                if new_baro:
                    self.trigger_notification(
                        "💎 Baro Ki'Teer est arrivé !",
                        f"Le marchand du Néant est présent sur : {current_snap['baro_loc']}",
                    )
                else:
                    self.trigger_notification(
                        "💎 Départ de Baro Ki'Teer",
                        "Baro Ki'Teer vient de repartir dans le Néant.",
                    )

        # 3. Nouvelle rotation des Mises à Prix (A, B, C)
        if self.settings.get("notify_bounties", True):
            old_bnt = self._prev_snapshot.get("bounty_rot")
            new_bnt = current_snap.get("bounty_rot")
            if old_bnt and new_bnt and old_bnt != new_bnt:
                self.trigger_notification(
                    "🎯 Nouvelle Rotation Mises à Prix",
                    f"Les contrats des planètes passent en {new_bnt} !",
                )

        # 4. Nouvelle rotation des Armes Incarnon de Duviri
        if self.settings.get("notify_incarnon", True):
            if self._prev_snapshot.get("incarnon_week") != current_snap.get("incarnon_week"):
                self.trigger_notification(
                    "⚔️ Rotation Incarnon (Duviri)",
                    f"Semaine {current_snap['incarnon_week']} : {current_snap['incarnon_list']}",
                )

        # 5. Nouvelle rotation des Warframes de Duviri
        if self.settings.get("notify_warframes", True):
            if self._prev_snapshot.get("wf_week") != current_snap.get("wf_week"):
                self.trigger_notification(
                    "🛡️ Rotation Warframes (Duviri)",
                    f"Semaine {current_snap['wf_week']} : {current_snap['wf_list']}",
                )

        self._prev_snapshot = current_snap

    def play_notification_sound(self) -> None:
        """Joue le fichier WAV par défaut de façon asynchrone sans bloquer l'interface."""
        if not self.settings.get("sound_enabled", True):
            return
        try:
            if DEFAULT_SOUND_FILE.exists():
                winsound.PlaySound(
                    str(DEFAULT_SOUND_FILE),
                    winsound.SND_FILENAME | winsound.SND_ASYNC,
                )
            else:
                winsound.MessageBeep(winsound.MB_ICONASTERISK)
        except Exception:
            pass

    def trigger_notification(self, title: str, message: str) -> None:
        """Enregistre l'alerte, joue le son .wav, affiche la bannière UI et le Toast Windows."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.history.insert(0, {"time": timestamp, "title": title, "message": message})
        self.history = self.history[:30]

        self.play_notification_sound()

        if self.on_alert_callback:
            self.on_alert_callback(title, message)

        threading.Thread(
            target=self._send_windows_balloon, args=(title, message), daemon=True
        ).start()

    @staticmethod
    def _send_windows_balloon(title: str, message: str) -> None:
        """Envoie une notification native dans la barre système Windows via PowerShell."""
        safe_title = title.replace("'", " ").replace('"', " ")
        safe_msg = message.replace("'", " ").replace('"', " ")
        ps_script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "$n = New-Object System.Windows.Forms.NotifyIcon; "
            "$n.Icon = [System.Drawing.SystemIcons]::Information; "
            "$n.Visible = $true; "
            f"$n.ShowBalloonTip(5000, 'WireFrame — {safe_title}', '{safe_msg}', "
            "[System.Windows.Forms.ToolTipIcon]::Info); "
            "Start-Sleep -Seconds 5; $n.Dispose()"
        )
        try:
            subprocess.run(
                ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_script],
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=8,
            )
        except Exception:
            pass
