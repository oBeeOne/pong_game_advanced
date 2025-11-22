import pyxel

from .config import (
    LARGEUR_ECRAN,
    HAUTEUR_ECRAN,
    COULEUR_FOND,
    RAQ_H,
    SCORE_MAX,
    VITESSE_RAQ,
    BAL_V_INIT,
    TOUCHES,
)
from .entities import Raquette, SmartComputer, Balle


class JeuPong:
    def __init__(self):
        self.etat = "menu"
        self.selection_menu = 0
        self.selection_difficulte = 0
        self.pause = False
        self.score_g = 0
        self.score_d = 0
        self.mode_ordinateur = True
        self.niveau_ia = "debutant"
        self.musique_menu_active = False

        self.raq_g = None
        self.raq_d = None
        self.balle = None

    def creer_entites(self):
        if self.mode_ordinateur:
            if self.niveau_ia == "debutant":
                taille_raquette = RAQ_H * 1.2
            elif self.niveau_ia == "amateur":
                taille_raquette = RAQ_H
            else:
                taille_raquette = RAQ_H * 0.7
        else:
            taille_raquette = RAQ_H

        self.raq_g = Raquette(
            x=18,
            y=HAUTEUR_ECRAN / 2 - taille_raquette / 2,
            touche_haut=TOUCHES["gauche_haut"],
            touche_bas=TOUCHES["gauche_bas"],
        )
        self.raq_g.h = taille_raquette

        if self.mode_ordinateur:
            self.raq_d = SmartComputer(
                x=LARGEUR_ECRAN - 18 - self.raq_g.w,
                y=HAUTEUR_ECRAN / 2 - taille_raquette / 2,
                niveau=self.niveau_ia,
            )
            self.raq_d.h = taille_raquette
        else:
            self.raq_d = Raquette(
                x=LARGEUR_ECRAN - 18 - self.raq_g.w,
                y=HAUTEUR_ECRAN / 2 - taille_raquette / 2,
                touche_haut=TOUCHES["droite_haut"],
                touche_bas=TOUCHES["droite_bas"],
            )
            self.raq_d.h = taille_raquette

        self.balle = Balle()

    def gerer_musique_menu(self):
        if self.etat in ["menu", "difficulte"]:
            if not self.musique_menu_active:
                # pyxel.playm(0, loop=True)
                self.musique_menu_active = True
        else:
            if self.musique_menu_active:
                pyxel.stop()
                self.musique_menu_active = False

    def maj_menu(self):
        self.gerer_musique_menu()

        if pyxel.btnp(TOUCHES["haut"]) or pyxel.btnp(TOUCHES["gauche_haut"]):
            self.selection_menu = (self.selection_menu - 1) % 3
            pyxel.play(0, 4)
        if pyxel.btnp(TOUCHES["bas"]) or pyxel.btnp(TOUCHES["gauche_bas"]):
            self.selection_menu = (self.selection_menu + 1) % 3
            pyxel.play(0, 4)

        if pyxel.btnp(TOUCHES["entree"]) or pyxel.btnp(pyxel.KEY_SPACE):
            pyxel.play(0, 5)
            if self.selection_menu == 0:
                self.mode_ordinateur = True
                self.etat = "difficulte"
            elif self.selection_menu == 1:
                self.mode_ordinateur = False
                self.creer_entites()
                self.etat = "jeu"
            elif self.selection_menu == 2:
                pyxel.quit()

        if pyxel.btnp(TOUCHES["quitter"]):
            pyxel.quit()

    def maj_difficulte(self):
        self.gerer_musique_menu()

        if pyxel.btnp(TOUCHES["haut"]) or pyxel.btnp(TOUCHES["gauche_haut"]):
            self.selection_difficulte = (self.selection_difficulte - 1) % 3
            pyxel.play(0, 4)
        if pyxel.btnp(TOUCHES["bas"]) or pyxel.btnp(TOUCHES["gauche_bas"]):
            self.selection_difficulte = (self.selection_difficulte + 1) % 3
            pyxel.play(0, 4)

        if pyxel.btnp(TOUCHES["entree"]) or pyxel.btnp(pyxel.KEY_SPACE):
            pyxel.play(0, 5)
            niveaux = ["debutant", "amateur", "pro"]
            self.niveau_ia = niveaux[self.selection_difficulte]
            self.creer_entites()
            self.etat = "jeu"

        if pyxel.btnp(TOUCHES["quitter"]):
            self.etat = "menu"

    def maj_jeu(self):
        self.gerer_musique_menu()

        if pyxel.btnp(TOUCHES["pause"]):
            self.pause = not self.pause
        if pyxel.btnp(TOUCHES["reset"]):
            self.reinitialiser()
        if pyxel.btnp(TOUCHES["quitter"]):
            self.etat = "menu"
            return

        if self.pause:
            return

        self.raq_g.maj()
        if isinstance(self.raq_d, SmartComputer):
            self.raq_d.maj(self.balle.y, self.balle)
        else:
            self.raq_d.maj()

        self.balle.maj()
        self.balle.collision_raquette(self.raq_g)
        self.balle.collision_raquette(self.raq_d)

        if self.balle.x + self.balle.t < 0:
            self.score_d += 1
            pyxel.play(1, 3)
            self.nouvelle_mise_en_jeu(a_droite=True)
        elif self.balle.x > LARGEUR_ECRAN:
            self.score_g += 1
            pyxel.play(1, 3)
            self.nouvelle_mise_en_jeu(a_droite=False)

        if self.score_g >= SCORE_MAX or self.score_d >= SCORE_MAX:
            if not hasattr(self, "victoire_son_joue"):
                pyxel.play(0, 8)
                self.victoire_son_joue = True

    def maj(self) -> None:
        if self.etat == "menu":
            self.maj_menu()
        elif self.etat == "difficulte":
            self.maj_difficulte()
        elif self.etat == "jeu":
            self.maj_jeu()

    def reinitialiser(self) -> None:
        self.score_g = 0
        self.score_d = 0
        if self.raq_g and self.raq_d and self.balle:
            self.raq_g.y = HAUTEUR_ECRAN / 2 - RAQ_H / 2
            self.raq_d.y = HAUTEUR_ECRAN / 2 - RAQ_H / 2
            self.balle.reset(direction_aleatoire=True)
        self.pause = False
        if hasattr(self, "victoire_son_joue"):
            delattr(self, "victoire_son_joue")

    def nouvelle_mise_en_jeu(self, a_droite: bool) -> None:
        self.balle.reset(direction_aleatoire=True)
        self.balle.vx = BAL_V_INIT * (1 if a_droite else -1)

    def dessiner_difficulte(self) -> None:
        pyxel.cls(COULEUR_FOND)
        pyxel.text(160, 60, "DIFFICULTE IA", 7)
        pyxel.text(120, 100, "Choisissez le niveau de l'IA :", 6)

        couleur_debutant = 8 if self.selection_difficulte == 0 else 7
        couleur_amateur = 8 if self.selection_difficulte == 1 else 7
        couleur_pro = 8 if self.selection_difficulte == 2 else 7

        pyxel.text(120, 150, "Debutant - Raquettes larges, IA lente", couleur_debutant)
        pyxel.text(120, 180, "Amateur - Raquettes normales, IA equilibree", couleur_amateur)
        pyxel.text(120, 210, "Pro - Raquettes petites, IA experte", couleur_pro)

        fleche_y = 150 + (self.selection_difficulte * 30)
        pyxel.text(100, fleche_y, ">", 8)

        pyxel.text(80, 280, "Z/S pour naviguer", 6)
        pyxel.text(80, 300, "Entree pour valider", 6)
        pyxel.text(80, 320, "Q pour retour menu principal", 6)

    def dessiner_menu(self) -> None:
        pyxel.cls(COULEUR_FOND)
        pyxel.text(200, 60, "P O N G", 7)
        pyxel.text(150, 100, "Choisissez votre mode :", 6)

        if self.musique_menu_active:
            if pyxel.frame_count % 60 < 30:
                pyxel.text(420, 20, "♪", 11)

        couleur_vs_ordi = 8 if self.selection_menu == 0 else 7
        couleur_vs_joueur = 8 if self.selection_menu == 1 else 7
        couleur_quitter = 8 if self.selection_menu == 2 else 7

        pyxel.text(120, 150, "Joueur vs Ordinateur", couleur_vs_ordi)
        pyxel.text(120, 180, "Joueur vs Joueur", couleur_vs_joueur)
        pyxel.text(120, 210, "Quitter", couleur_quitter)

        fleche_y = 150 + (self.selection_menu * 30)
        pyxel.text(100, fleche_y, ">", 8)

        pyxel.text(80, 280, "Z/S pour naviguer", 6)
        pyxel.text(80, 300, "Entree ou Espace pour valider", 6)
        pyxel.text(80, 320, "Q pour quitter rapidement", 6)

    def dessiner_jeu(self) -> None:
        pyxel.cls(COULEUR_FOND)
        for y in range(0, HAUTEUR_ECRAN, 18):
            pyxel.rect(LARGEUR_ECRAN // 2 - 2, y, 4, 9, 5)

        if self.raq_g and self.raq_d and self.balle:
            self.raq_g.dessiner()
            self.raq_d.dessiner()
            self.balle.dessiner()

        pyxel.text(LARGEUR_ECRAN // 2 - 60, 20, f"{self.score_g}", 7)
        pyxel.text(LARGEUR_ECRAN // 2 + 50, 20, f"{self.score_d}", 7)

        mode_text = f"vs Ordi ({self.niveau_ia.title()})" if self.mode_ordinateur else "vs Joueur"
        pyxel.text(10, HAUTEUR_ECRAN - 90, f"Mode: {mode_text} - Audio 8-bits actif", 6)
        pyxel.text(10, HAUTEUR_ECRAN - 70, "Effet 3D: Balle grandit au centre du terrain", 5)
        pyxel.text(10, HAUTEUR_ECRAN - 60, "Sons: Raquette sourd, Mur sec, Sol etouffe", 5)
        pyxel.text(10, HAUTEUR_ECRAN - 50, "Mouvement raquette: Meme sens = SPIN, Oppose = SLICE", 5)
        pyxel.text(10, HAUTEUR_ECRAN - 40, "Strategie: Haut raquette = renvoi vers haut", 5)
        pyxel.text(10, HAUTEUR_ECRAN - 30, "          Bas raquette = renvoi vers bas", 5)
        pyxel.text(10, HAUTEUR_ECRAN - 20, "Z/S  O/L  (P)ause  (R)eset  (Q)menu", 6)

        if self.pause:
            pyxel.text(200, HAUTEUR_ECRAN // 2 - 10, "PAUSE", 8)

        if self.score_g >= SCORE_MAX or self.score_d >= SCORE_MAX:
            gagnant = "GAUCHE" if self.score_g > self.score_d else "DROITE"
            self.pause = True
            pyxel.text(160, HAUTEUR_ECRAN // 2 - 10, f"VICTOIRE {gagnant} !", 8)
            pyxel.text(140, HAUTEUR_ECRAN // 2 + 20, "Appuie sur R pour rejouer", 13)

    def dessiner(self) -> None:
        if self.etat == "menu":
            self.dessiner_menu()
        elif self.etat == "difficulte":
            self.dessiner_difficulte()
        elif self.etat == "jeu":
            self.dessiner_jeu()
