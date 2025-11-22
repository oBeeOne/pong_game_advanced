import random
import pyxel

from .config import (
    LARGEUR_ECRAN,
    HAUTEUR_ECRAN,
    RAQ_L,
    RAQ_H,
    VITESSE_RAQ,
    BAL_TAILLE,
    BAL_V_INIT,
)


class Raquette:
    def __init__(self, x: float, y: float, touche_haut: int | None, touche_bas: int | None):
        self.x = x
        self.y = y
        self.y_precedente = y
        self.w = RAQ_L
        self.h = RAQ_H
        self.touche_haut = touche_haut
        self.touche_bas = touche_bas
        self.vitesse_mouvement = 0

    def maj(self) -> None:
        self.y_precedente = self.y

        mouvement = 0
        if self.touche_haut and pyxel.btn(self.touche_haut):
            mouvement -= VITESSE_RAQ
        if self.touche_bas and pyxel.btn(self.touche_bas):
            mouvement += VITESSE_RAQ

        self.y += mouvement
        self.vitesse_mouvement = self.y - self.y_precedente

        if self.y < 0:
            self.y = 0
        if self.y + self.h > HAUTEUR_ECRAN:
            self.y = HAUTEUR_ECRAN - self.h

    def dessiner(self) -> None:
        pyxel.rect(self.x, self.y, self.w, self.h, 7)

    def rect(self):
        return (self.x, self.y, self.x + self.w, self.y + self.h)


class SmartComputer(Raquette):
    def __init__(self, x: float, y: float, niveau: str = "amateur"):
        super().__init__(x, y, None, None)
        self.niveau = niveau
        self.position_cible = y
        self.vitesse_reaction = 0
        self.derniere_balle_x = 0
        self.anticipation_active = False
        self.position_anticipee = y
        self.temps_sans_action = 0
        self.derniere_direction_balle = 0

        if niveau == "debutant":
            self.vitesse_max = VITESSE_RAQ * 0.6
            self.precision = 0.4
            self.temps_reaction = 8
            self.anticipation = 0.1
            self.agressivite = 0.2
        elif niveau == "amateur":
            self.vitesse_max = VITESSE_RAQ * 0.8
            self.precision = 0.7
            self.temps_reaction = 4
            self.anticipation = 0.4
            self.agressivite = 0.5
        else:
            self.vitesse_max = VITESSE_RAQ * 1.0
            self.precision = 0.9
            self.temps_reaction = 2
            self.anticipation = 0.8
            self.agressivite = 0.8

    def calculer_position_optimale(self, balle):
        position_basique = balle.y + balle.t / 2 - self.h / 2

        if balle.vx > 0:
            temps_impact = (self.x - balle.x) / balle.vx if balle.vx > 0 else float("inf")
            if 0 < temps_impact < 100:
                position_anticipee = balle.y + (balle.vy * temps_impact * self.anticipation)
                self.anticipation_active = True
                self.position_anticipee = position_anticipee
            else:
                self.anticipation_active = False
        else:
            self.anticipation_active = False

        facteur_offensif = 1.0
        if self.agressivite > 0.5 and abs(balle.vx) > 1:
            if balle.y < HAUTEUR_ECRAN / 3:
                facteur_offensif = 0.7
            elif balle.y > HAUTEUR_ECRAN * 2 / 3:
                facteur_offensif = 1.3

        if self.anticipation_active:
            position_optimale = (
                (position_basique * (1 - self.precision) + self.position_anticipee * self.precision)
                * facteur_offensif
            )
        else:
            position_optimale = position_basique * facteur_offensif

        return position_optimale

    def maj(self, balle_y, balle=None) -> None:
        if not balle:
            super().maj()
            return

        self.y_precedente = self.y

        if balle.x != self.derniere_balle_x:
            direction_actuelle = 1 if balle.vx > 0 else -1
            if direction_actuelle != self.derniere_direction_balle:
                self.temps_sans_action = self.temps_reaction
            self.derniere_direction_balle = direction_actuelle
        self.derniere_balle_x = balle.x

        if self.temps_sans_action > 0:
            self.temps_sans_action -= 1
            return

        self.position_cible = self.calculer_position_optimale(balle)

        erreur = random.uniform(-30, 30) * (1 - self.precision)
        self.position_cible += erreur

        difference = self.position_cible - (self.y + self.h / 2)

        if abs(difference) > 5:
            distance_balle = abs(self.x - balle.x)
            urgence = max(0.3, 1 - (distance_balle / LARGEUR_ECRAN))
            vitesse = self.vitesse_max * urgence
            variation = random.uniform(0.8, 1.2)
            vitesse *= variation

            if difference > 0:
                self.y += min(vitesse, abs(difference))
            else:
                self.y -= min(vitesse, abs(difference))

        if self.niveau == "debutant":
            if random.random() < 0.05:
                self.y += random.uniform(-15, 15)
        elif self.niveau == "pro":
            if not self.anticipation_active and random.random() < 0.1:
                centre = HAUTEUR_ECRAN / 2 - self.h / 2
                if abs(self.y - centre) > 30:
                    direction = 1 if centre > self.y else -1
                    self.y += direction * (self.vitesse_max * 0.3)

        if self.y < 0:
            self.y = 0
        if self.y + self.h > HAUTEUR_ECRAN:
            self.y = HAUTEUR_ECRAN - self.h

        self.vitesse_mouvement = self.y - self.y_precedente


class Balle:
    def __init__(self):
        self.t = BAL_TAILLE
        self.effet_y = 0.0
        self.vitesse_max = BAL_V_INIT * 2.5
        self.derniere_collision = 0
        self.impact_force = 0.0
        self.reset(direction_aleatoire=True)

    def reset(self, direction_aleatoire: bool = False) -> None:
        self.x = LARGEUR_ECRAN / 2 - self.t / 2
        self.y = HAUTEUR_ECRAN / 2 - self.t / 2
        vx = BAL_V_INIT * (1 if random.random() < 0.5 else -1)
        vy = BAL_V_INIT * random.choice([-0.6, -0.4, -0.2, 0.2, 0.4, 0.6])
        if not direction_aleatoire:
            vx = BAL_V_INIT
            vy = -0.4
        self.vx, self.vy = vx, vy
        self.effet_y = 0.0
        self.derniere_collision = 0
        self.impact_force = 0.0

    def maj(self) -> None:
        self.x += self.vx
        self.y += self.vy + self.effet_y
        self.effet_y *= 0.98
        self.derniere_collision += 1

        if self.y <= 0:
            self.y = 0
            self.vy = -self.vy
            self.effet_y *= -0.5
            pyxel.play(1, 2)
        elif self.y + self.t >= HAUTEUR_ECRAN:
            self.y = HAUTEUR_ECRAN - self.t
            self.vy = -self.vy
            self.effet_y *= -0.5
            pyxel.play(1, 2)

    def collision_raquette(self, raq: Raquette) -> bool:
        centre_terrain = LARGEUR_ECRAN / 2
        distance_centre = abs(self.x + self.t / 2 - centre_terrain)
        distance_relative = distance_centre / (LARGEUR_ECRAN / 2)
        taille_min = self.t * 0.6
        taille_max = self.t * 1.4
        taille_actuelle = taille_max - (distance_relative * (taille_max - taille_min))

        offset = (self.t - taille_actuelle) / 2
        bx1, by1 = self.x + offset, self.y + offset
        bx2, by2 = bx1 + taille_actuelle, by1 + taille_actuelle
        rx1, ry1, rx2, ry2 = raq.rect()

        inter = not (bx2 < rx1 or bx1 > rx2 or by2 < ry1 or by1 > ry2)
        if inter and self.derniere_collision > 5:
            centre_balle_y = by1 + taille_actuelle / 2
            impact_relatif = (centre_balle_y - ry1) / raq.h
            impact_relatif = max(0.05, min(0.95, impact_relatif))

            if self.vx < 0:
                self.x = rx2 - offset
            else:
                self.x = rx1 - taille_actuelle - offset

            angle_incidence = abs(self.vy / self.vx) if self.vx != 0 else 0
            vitesse_incidence = (self.vx ** 2 + self.vy ** 2) ** 0.5

            if impact_relatif < 0.5:
                direction_base = -1
                zone_factor = (0.5 - impact_relatif) * 2
            else:
                direction_base = 1
                zone_factor = (impact_relatif - 0.5) * 2

            distance_centre = abs(impact_relatif - 0.5) * 2
            intensite_angle = distance_centre * 1.5
            influence_incidence = min(angle_incidence * 0.4, 0.6)

            vitesse_horizontale_base = abs(self.vx)
            nouvelle_vitesse_h = min(vitesse_horizontale_base * 1.08, self.vitesse_max)
            self.vx = -nouvelle_vitesse_h if self.vx > 0 else nouvelle_vitesse_h

            nouvel_angle_voulu = direction_base * intensite_angle * 3.0
            influence_ancienne_direction = self.vy * influence_incidence
            self.vy = nouvel_angle_voulu + influence_ancienne_direction

            if isinstance(raq, SmartComputer):
                variance = (1 - raq.precision) * 1.5
            else:
                variance = 0.3
            facteur_aleatoire = random.uniform(-variance, variance)
            self.vy += facteur_aleatoire

            self.effet_y = (impact_relatif - 0.5) * 1.2 * vitesse_incidence * 0.1
            if distance_centre > 0.3:
                self.effet_y += direction_base * zone_factor * 0.8

            mouvement_raquette = raq.vitesse_mouvement
            if abs(mouvement_raquette) > 0.1:
                if mouvement_raquette > 0:
                    if self.vy > 0:
                        effet_mouvement = mouvement_raquette * 2.0
                        bonus_vitesse = mouvement_raquette * 0.5
                    else:
                        effet_mouvement = mouvement_raquette * 1.5
                        bonus_vitesse = -mouvement_raquette * 0.3
                else:
                    if self.vy < 0:
                        effet_mouvement = mouvement_raquette * 2.0
                        bonus_vitesse = -mouvement_raquette * 0.5
                    else:
                        effet_mouvement = mouvement_raquette * 1.5
                        bonus_vitesse = mouvement_raquette * 0.3

                self.effet_y += effet_mouvement
                self.vy += bonus_vitesse

                if abs(mouvement_raquette) > 1.5:
                    self.impact_force = min(self.impact_force + 0.3, 1.0)
                    if mouvement_raquette * self.vy > 0:
                        self.effet_y *= 1.5
                    else:
                        self.effet_y *= 0.7

            vitesse_v_max = 5.5
            self.vy = max(-vitesse_v_max, min(vitesse_v_max, self.vy))

            vitesse_totale = (self.vx ** 2 + self.vy ** 2) ** 0.5
            if vitesse_totale > self.vitesse_max:
                ratio = self.vitesse_max / vitesse_totale
                self.vx *= ratio
                self.vy *= ratio

            vitesse_totale_finale = (self.vx ** 2 + self.vy ** 2) ** 0.5
            if abs(mouvement_raquette) > 1.5:
                if mouvement_raquette * self.vy > 0:
                    pyxel.play(2, 6)
                else:
                    pyxel.play(2, 7)
            elif abs(self.effet_y) > 1.0:
                pyxel.play(2, 1)
            else:
                pyxel.play(2, 0)

            if vitesse_totale_finale > self.vitesse_max * 0.8:
                pyxel.play(3, 9)

            self.impact_force = min(vitesse_totale_finale / self.vitesse_max, 1.0)
            self.derniere_collision = 0

        return inter

    def dessiner(self) -> None:
        centre_terrain = LARGEUR_ECRAN / 2
        distance_centre = abs(self.x + self.t / 2 - centre_terrain)
        distance_relative = distance_centre / (LARGEUR_ECRAN / 2)
        taille_min = self.t * 0.6
        taille_max = self.t * 1.4
        taille_actuelle = taille_max - (distance_relative * (taille_max - taille_min))
        taille_actuelle = int(taille_actuelle)

        offset_x = (self.t - taille_actuelle) / 2
        offset_y = (self.t - taille_actuelle) / 2
        pos_x = self.x + offset_x
        pos_y = self.y + offset_y

        vitesse_totale = abs(self.vx) + abs(self.vy)
        if vitesse_totale > 7:
            couleur = 8
        elif vitesse_totale > 5:
            couleur = 10
        elif vitesse_totale > 3:
            couleur = 9
        else:
            couleur = 7

        effet_total = abs(self.effet_y)
        if effet_total > 0.5:
            if effet_total > 2.0:
                if int(self.x + self.y) % 4 < 2:
                    couleur = 14 if self.effet_y > 0 else 12
            elif effet_total > 1.0:
                if int(self.x + self.y) % 6 < 3:
                    couleur = 11
            else:
                if int(self.x + self.y) % 8 < 4:
                    couleur = 10

        if taille_actuelle > self.t:
            taille_ombre = int(taille_actuelle * 0.8)
            pos_ombre_x = pos_x + 2
            pos_ombre_y = pos_y + 2
            pyxel.rect(pos_ombre_x, pos_ombre_y, taille_ombre, taille_ombre, 1)

        pyxel.rect(pos_x, pos_y, taille_actuelle, taille_actuelle, couleur)

        if taille_actuelle > self.t * 1.1:
            centre_balle_x = int(pos_x + taille_actuelle // 2)
            centre_balle_y = int(pos_y + taille_actuelle // 2)
            pyxel.pset(centre_balle_x - 1, centre_balle_y - 1, 7)

        if vitesse_totale > 5:
            trail_x = self.x - self.vx * 1.5
            trail_y = self.y - self.vy * 1.5 - self.effet_y * 3
            centre_terrain = LARGEUR_ECRAN / 2
            distance_centre_trail = abs(trail_x + self.t / 2 - centre_terrain)
            distance_relative_trail = distance_centre_trail / (LARGEUR_ECRAN / 2)
            taille_min = self.t * 0.6
            taille_max = self.t * 1.4
            taille_trail = int((taille_max - (distance_relative_trail * (taille_max - taille_min))) * 0.5)
            if 0 <= trail_x < LARGEUR_ECRAN and 0 <= trail_y < HAUTEUR_ECRAN and taille_trail > 0:
                pyxel.rect(trail_x, trail_y, taille_trail, taille_trail, max(1, couleur - 2))

        if self.derniere_collision < 3 and self.impact_force > 0.7:
            pyxel.rect(pos_x - 1, pos_y - 1, taille_actuelle + 2, taille_actuelle + 2, 7)
            pyxel.rect(pos_x, pos_y, taille_actuelle, taille_actuelle, couleur)

        if abs(self.effet_y) > 0.3:
            direction_effet = 1 if self.effet_y > 0 else -1
            intensite = min(abs(self.effet_y) / 3.0, 1.0)
            centre_balle_x = pos_x + taille_actuelle // 2
            centre_balle_y = pos_y + taille_actuelle // 2
            offset_effet_y = direction_effet * int(taille_actuelle * 0.4 * intensite)
            couleur_effet = 13 if intensite > 0.7 else 5
            pyxel.pset(int(centre_balle_x), int(centre_balle_y + offset_effet_y), couleur_effet)
            if intensite > 0.8:
                pyxel.pset(int(centre_balle_x - 1), int(centre_balle_y + offset_effet_y), couleur_effet)
                pyxel.pset(int(centre_balle_x + 1), int(centre_balle_y + offset_effet_y), couleur_effet)
