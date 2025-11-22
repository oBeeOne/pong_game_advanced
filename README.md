# pong_game_advanced

Jeu Pong avancé construit avec Pyxel, comprenant un menu, un choix de difficulté et une IA améliorée.

## Installation

Prérequis: Python 3.8+ et `pyxel`.

Dans un environnement virtuel (recommandé):

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -U pip setuptools wheel
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

Ou installation directe:

```bash
python -m pip install pyxel
```

## Exécution

Depuis la racine du projet:

```bash
.venv/Scripts/python.exe pong.py
```

## Architecture

Le code est découpé pour améliorer la maintenabilité:

- `pong.py`: point d’entrée minimal (lance le jeu)
- `pong_game/`
	- `config.py`: constantes, dimensions, touches, vitesses
	- `entities.py`: entités du jeu (`Raquette`, `SmartComputer`, `Balle`)
	- `state.py`: logique du jeu, états, collisions, score, rendu
	- `sound.py`: création et configuration des sons Pyxel
	- `app.py`: initialisation Pyxel et boucle principale (`Application`)

## Contrôles (AZERTY)

- Joueur gauche: `Z`/`S`
- Joueur droit: `O`/`L`
- Valider: `Entrée` (ou `Espace` dans les menus)
- Pause: `P`
- Reset: `R`
- Menu/Quitter: `Q`


