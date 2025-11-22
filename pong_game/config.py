import pyxel

# =========================
# Constantes de configuration
# =========================
LARGEUR_ECRAN = 480
HAUTEUR_ECRAN = 360
COULEUR_FOND = 0

# Raquettes
RAQ_L = 8
RAQ_H = 60
VITESSE_RAQ = 4

# Balle
BAL_TAILLE = 8
BAL_V_INIT = 3.2

# Scores
SCORE_MAX = 9

# Touches (AZERTY)
TOUCHES = {
    "gauche_haut": pyxel.KEY_Z,
    "gauche_bas": pyxel.KEY_S,
    "droite_haut": pyxel.KEY_O,
    "droite_bas": pyxel.KEY_L,
    "reset": pyxel.KEY_R,
    "pause": pyxel.KEY_P,
    "quitter": pyxel.KEY_Q,
    "entree": pyxel.KEY_RETURN,
    "haut": pyxel.KEY_UP,
    "bas": pyxel.KEY_DOWN,
}
