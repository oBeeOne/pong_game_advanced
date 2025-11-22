"""
Point d'entrée du jeu Pong.
Ce fichier importe l'application depuis le package `pong_game` afin de
garder un point d'exécution simple tout en séparant le code en modules.
"""

from pong_game.app import Application


if __name__ == "__main__":
    Application()