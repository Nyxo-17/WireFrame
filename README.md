<div align="center">
  <img src="data/app_logo.png" alt="WireFrame Logo" width="115" />
  <h1>❖ WireFrame — Warframe Companion App ❖</h1>
  <p><b>Modern, fast and bilingual (EN / FR) desktop companion to track the Origin System in real time.</b></p>
  <p>Created by <a href="https://github.com/Nyxo-17"><b>Nyxo_17</b></a> • <a href="https://discord.gg/DhGwHPf82n">💬 Join the Discord Server</a></p>
  <p><a href="#-english-version"><b>🇬🇧 English Version</b></a> &nbsp;|&nbsp; <a href="#-version-française"><b>🇫🇷 Version Française</b></a></p>
</div>

---

# 🇬🇧 English Version

## ✨ Key Features

- 🌍 **Live Planet & Open-World Cycles**: Real-time second-by-second countdowns for **Plains of Eidolon / Cetus** (Day/Night), **Orb Vallis / Fortuna** (Warm/Cold), **Cambion Drift / Deimos** (Fass/Vome), and **Earth Forests** (4h Cycle) featuring official Star Chart planet renders.
- 🌀 **The Duviri Circuit & Incarnon Tracker**: Displays current week, next week, and full rotation schedule for both **Steel Path Incarnon Weapons** (8-week loop) and **Normal Circuit Warframes** (11-week loop).
- 🎯 **Bounty Rotations (A / B / C)**: Live reward pool tracking across Cetus, Fortuna, Deimos, Zariman Ten Zero, and Sanctum Anatomica with planet icons.
- 💠 **Void Trader (Baro Ki'Teer)**: Arrival/departure countdown, target Relay location, and full inventory display.
- 📚 **Complete Offline/Online Codex with Official Images**:
  - **120 Warframes** (Standard & Prime) with stats and component blueprint drop rates.
  - **239 Resources** with optimal farming locations.
  - **1,442 Mods** with max-rank stats and drop sources.
- 🔔 **Notification Center & Custom Sound Alerts**: Windows system tray notifications + in-app golden toast banners + custom sound alerts for every cycle change.
- 🌐 **Instant EN / FR Switcher & Center Zoom**: One-click language toggle (`FR | EN`) and independent zoom (`70%` to `140%`) on the central view.
- ⬇️ **Built-in GitHub Auto-Updater**: Checks and installs new releases from GitHub in 1 click without overwriting your personal settings.

---

## 🚀 1-Click Installation (For You & Your Friends)

### Prerequisites
- **Windows 10 / 11**
- **[Python 3.10+](https://www.python.org/downloads/)** *(make sure to check **"Add Python to PATH"** during Python installation)*

### Quick Start (No terminal required)
1. Click the green **`<> Code`** button at the top of this GitHub page, then click **`Download ZIP`**.
2. Extract the **`WireFrame-master`** folder anywhere on your PC (e.g., in `Documents`).
3. Double-click **`Lancer_WireFrame.bat`**:
   - It automatically creates the local Python environment and installs required packages,
   - Creates the **WireFrame** shortcut with its golden emblem directly on your **Windows Desktop**,
   - Launches the application!
4. Next time, simply open **WireFrame** from your Desktop icon. Whenever an update is released, click **`⬇️ Check Update`** at the bottom-left of the app!

---

# 🇫🇷 Version Française

## ✨ Fonctionnalités Principales

- 🌍 **Cycles des Planètes en Temps Réel** : Suivi à la seconde près pour **Cetus** (Jour/Nuit), **Vallée Orbis** (Chaud/Froid), **Puy de Cambion** (Fass/Vome) et les **Forêts de la Terre** (Cycle 4h) avec les vraies images officielles des planètes.
- 🌀 **Le Circuit de Duviri & Incarnon** : Affichage des Warframes et des Armes Incarnon (Route de l'Acier) de la semaine actuelle, de la semaine suivante et du calendrier complet des rotations.
- 🎯 **Rotations des Mises à Prix (A / B / C)** : Suivi en direct des rotations de récompenses pour Cetus, Fortuna, Deimos, le Zariman Ten Zero et le Sanctum Anatomica avec les images des planètes concernées.
- 💠 **Marchand du Néant (Baro Ki'Teer)** : Compte à rebours d'arrivée/départ, Relais de destination et inventaire complet.
- 📚 **Codex Complet avec Images Officielles** :
  - **120 Warframes** (Standard & Prime) avec statistiques et taux de drop des schémas.
  - **239 Ressources** avec lieux de farm optimisés.
  - **1 442 Mods** avec effets au rang max et sources d'obtention.
- 🔔 **Centre de Notifications & Alertes Sonores** : Notifications Windows + bannière dorée in-app + alerte sonore personnalisable pour chaque événement.
- 🌐 **Bilingue FR / EN & Zoom Central** : Bascule instantanée Français / Anglais et zoom dynamique (`70%` à `140%`) sur la vue centrale.
- ⬇️ **Mise à Jour Automatique (Auto-Updater GitHub)** : Vérifie et installe les nouvelles versions publiées sur GitHub en 1 clic sans perdre tes réglages.

---

## 🚀 Installation en 1 Clic (Pour toi et tes amis)

### Prérequis
- **Windows 10 / 11**
- **[Python 3.10+](https://www.python.org/downloads/)** *(cocher la case **"Add Python to PATH"** lors de l'installation de Python)*

### Méthode Rapide (Sans ligne de commande)
1. Clique sur le bouton vert **`<> Code`** en haut de cette page GitHub puis sur **`Download ZIP`**.
2. Extrais le dossier **`WireFrame-master`** où tu veux sur ton PC (par exemple dans `Documents`).
3. Double-clique sur **`Lancer_WireFrame.bat`** :
   - Le script installe automatiquement les bibliothèques requises,
   - Crée le raccourci **WireFrame** avec son icône dorée directement sur ton **Bureau Windows**,
   - Et lance l'application !
4. Pour les prochaines fois, ouvre simplement **WireFrame** depuis l'icône sur ton Bureau. Dès qu'une mise à jour est disponible, clique sur **`⬇️ Vérifier MAJ`** en bas à gauche dans l'application !

---

## 🗂️ Project Architecture / Architecture du Projet

```text
WireFrame/
├── main.py                  # Entry point / Point d'entrée de l'application
├── Lancer_WireFrame.bat     # 1-Click Installer, Desktop Shortcut Creator & Launcher
├── version.json             # Version metadata & changelog (GitHub Auto-Updater)
├── requirements.txt         # Python dependencies (customtkinter, requests, Pillow)
├── data/                    # JSON databases, official icons, planet renders & sounds
├── core/                    # Pure business logic (API, Timers, Duviri, Notifications, Updater)
└── ui/                      # CustomTkinter GUI (Sidebar, LivePanel, TitleBar & 7 Views)
```
