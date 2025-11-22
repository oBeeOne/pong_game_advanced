import pyxel

from .config import LARGEUR_ECRAN, HAUTEUR_ECRAN
from .state import JeuPong
from .sound import creer_sons


class Application:
    def __init__(self):
        pyxel.init(LARGEUR_ECRAN, HAUTEUR_ECRAN, title="PONG - Avec menu de sélection")
        creer_sons()
        self.jeu = JeuPong()
        pyxel.run(self.jeu.maj, self.jeu.dessiner)
