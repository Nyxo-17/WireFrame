<div align="center">
  <img src="data/app_logo.png" alt="WireFrame Logo" width="110" />
  <h1>❖ WireFrame — Compagnon Warframe ❖</h1>
  <p><b>Application de bureau moderne, rapide et bilingue (FR / EN) pour suivre l'état du Système Origine en direct.</b></p>
  <p>Créé par <a href="https://github.com/Nyxo-17"><b>Nyxo_17</b></a> • <a href="https://discord.gg/DhGwHPf82n">💬 Rejoindre le serveur Discord</a></p>
</div>

---

## ✨ Fonctionnalités Principales

- 🌍 **Cycles des Planètes en Temps Réel** : Suivi à la seconde près pour **Cetus** (Jour/Nuit), **Vallée Orbis** (Chaud/Froid), **Puy de Cambion** (Fass/Vome) et les **Forêts de la Terre** (Cycle 4h) avec les vraies images officielles des planètes.
- 🌀 **Le Circuit de Duviri & Incarnon** : Affichage des Warframes et des Armes Incarnon (Route de l'Acier) de la semaine actuelle, de la semaine suivante et du calendrier complet des rotations.
- 🎯 **Rotations des Mises à Prix (A / B / C)** : Suivi en direct des rotations de récompenses pour Cetus, Fortuna, Deimos, le Zariman Ten Zero et le Sanctum Anatomica.
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

## 🗂️ Architecture du Projet

```text
WireFrame/
├── main.py                  # Point d'entrée de l'application
├── Lancer_WireFrame.bat     # Installateur + Créateur de raccourci Bureau + Lanceur 1-clic
├── version.json             # Numéro de version et notes de mise à jour (Auto-Updater)
├── requirements.txt         # Dépendances Python (customtkinter, requests, Pillow)
├── data/                    # Données JSON, icônes officielles, planètes et sons
├── core/                    # Logique métier pure (API, Timers, Duviri, Notifications, Updater)
└── ui/                      # Interface graphique CustomTkinter (Sidebar, LivePanel, 7 Vues)
```
