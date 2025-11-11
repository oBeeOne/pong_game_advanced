# PONG Pyxel - Avec menu de sélection du mode de jeu
# ------------------------------------------------------
# Pré-requis: pip install pyxel
# Lancer: python pong_avec_menu.py

import random
import pyxel


# =========================
# Constantes de configuration
# =========================
LARGEUR_ECRAN = 480  # 3x plus large
HAUTEUR_ECRAN = 360  # 3x plus haut
COULEUR_FOND = 0  # noir (palette Pyxel)

# Raquettes
RAQ_L = 8  # plus large pour être visible
RAQ_H = 60  # plus haute proportionnellement
VITESSE_RAQ = 4  # vitesse adaptée à la résolution

# Balle
BAL_TAILLE = 8  # plus grosse pour être bien visible
BAL_V_INIT = 3.2  # vitesse adaptée

# Scores
SCORE_MAX = 9

# Touches (AZERTY)
# Joueur gauche: Z (haut), S (bas)
# Joueur droit : O (haut), L (bas)
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


# =========================
# Modèle de données
# =========================
class Raquette:
    """
    Représente une raquette (gauche ou droite).

    Attributs:
        x (float) : abscisse de la raquette (coin haut-gauche)
        y (float) : ordonnée de la raquette (coin haut-gauche)
        w (int)   : largeur
        h (int)   : hauteur
        touche_haut (int) : code de la touche pour monter
        touche_bas  (int) : code de la touche pour descendre
    """

    def __init__(self, x: float, y: float, touche_haut: int, touche_bas: int):
        self.x = x
        self.y = y
        self.y_precedente = y  # Pour calculer le mouvement
        self.w = RAQ_L
        self.h = RAQ_H
        self.touche_haut = touche_haut
        self.touche_bas = touche_bas
        self.vitesse_mouvement = 0  # Vitesse actuelle de mouvement

    def maj(self) -> None:
        """Met à jour la position (entrée clavier + bornage)."""
        # Sauvegarder la position précédente
        self.y_precedente = self.y
        
        mouvement = 0
        if self.touche_haut and pyxel.btn(self.touche_haut):
            mouvement -= VITESSE_RAQ
        if self.touche_bas and pyxel.btn(self.touche_bas):
            mouvement += VITESSE_RAQ
            
        self.y += mouvement
        
        # Calculer la vitesse de mouvement pour les effets
        self.vitesse_mouvement = self.y - self.y_precedente

        # Bornage dans l'écran
        if self.y < 0:
            self.y = 0
        if self.y + self.h > HAUTEUR_ECRAN:
            self.y = HAUTEUR_ECRAN - self.h

    def dessiner(self) -> None:
        """Dessine la raquette."""
        pyxel.rect(self.x, self.y, self.w, self.h, 7)  # 7 = blanc

    def rect(self):
        """Retourne le rectangle collision (x1,y1,x2,y2)."""
        return (self.x, self.y, self.x + self.w, self.y + self.h)

# Raquette contrôlée par l'ordinateur avec IA avancée
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
        
        # Configuration selon le niveau
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
        else:  # pro
            self.vitesse_max = VITESSE_RAQ * 1.0
            self.precision = 0.9
            self.temps_reaction = 2
            self.anticipation = 0.8
            self.agressivite = 0.8

    def calculer_position_optimale(self, balle):
        """Calcule où l'IA devrait positionner sa raquette."""
        # Position basique : centre de la raquette vers centre de la balle
        position_basique = balle.y + balle.t/2 - self.h/2
        
        # Anticipation : prévoir où sera la balle
        if balle.vx > 0:  # La balle se dirige vers l'IA
            temps_impact = (self.x - balle.x) / balle.vx if balle.vx > 0 else float('inf')
            if temps_impact > 0 and temps_impact < 100:  # Anticipation raisonnable
                position_anticipee = balle.y + (balle.vy * temps_impact * self.anticipation)
                self.anticipation_active = True
                self.position_anticipee = position_anticipee
            else:
                self.anticipation_active = False
        else:
            self.anticipation_active = False
        
        # Stratégie offensive : viser des angles
        facteur_offensif = 1.0
        if self.agressivite > 0.5 and abs(balle.vx) > 1:
            # Essayer de renvoyer vers les coins
            if balle.y < HAUTEUR_ECRAN / 3:
                facteur_offensif = 0.7  # Viser vers le bas
            elif balle.y > HAUTEUR_ECRAN * 2/3:
                facteur_offensif = 1.3  # Viser vers le haut
        
        # Position finale
        if self.anticipation_active:
            position_optimale = (position_basique * (1-self.precision) + 
                               self.position_anticipee * self.precision) * facteur_offensif
        else:
            position_optimale = position_basique * facteur_offensif
            
        return position_optimale

    def maj(self, balle_y, balle=None) -> None:
        """IA avancée avec comportement humain."""
        if not balle:
            # Fallback vers l'ancienne méthode si pas d'objet balle
            super().maj()
            return
        
        # Sauvegarder la position précédente pour calculer le mouvement
        self.y_precedente = self.y
            
        # Détection du changement de direction de la balle
        if balle.x != self.derniere_balle_x:
            direction_actuelle = 1 if balle.vx > 0 else -1
            if direction_actuelle != self.derniere_direction_balle:
                self.temps_sans_action = self.temps_reaction
            self.derniere_direction_balle = direction_actuelle
        self.derniere_balle_x = balle.x
        
        # Temps de réaction (plus la balle change de direction, plus il faut du temps)
        if self.temps_sans_action > 0:
            self.temps_sans_action -= 1
            return  # Pas de mouvement pendant le temps de réaction
            
        # Calculer la position optimale
        self.position_cible = self.calculer_position_optimale(balle)
        
        # Ajouter du réalisme : erreurs et imprécisions
        erreur = random.uniform(-30, 30) * (1 - self.precision)
        self.position_cible += erreur
        
        # Mouvement vers la position cible avec vitesse variable
        difference = self.position_cible - (self.y + self.h/2)
        
        if abs(difference) > 5:  # Zone morte pour éviter les oscillations
            # Vitesse adaptative selon l'urgence
            distance_balle = abs(self.x - balle.x)
            urgence = max(0.3, 1 - (distance_balle / LARGEUR_ECRAN))
            vitesse = self.vitesse_max * urgence
            
            # Variation aléatoire de vitesse pour simuler l'hésitation
            variation = random.uniform(0.8, 1.2)
            vitesse *= variation
            
            if difference > 0:
                self.y += min(vitesse, abs(difference))
            else:
                self.y -= min(vitesse, abs(difference))
        
        # Comportement spécial selon le niveau
        if self.niveau == "debutant":
            # Parfois l'IA "panique" et fait des mouvements erratiques
            if random.random() < 0.05:  # 5% de chance
                self.y += random.uniform(-15, 15)
                
        elif self.niveau == "pro":
            # L'IA pro peut faire des mouvements préventifs
            if not self.anticipation_active and random.random() < 0.1:
                # Mouvement vers le centre par défaut
                centre = HAUTEUR_ECRAN / 2 - self.h / 2
                if abs(self.y - centre) > 30:
                    direction = 1 if centre > self.y else -1
                    self.y += direction * (self.vitesse_max * 0.3)

        # Bornage dans l'écran
        if self.y < 0:
            self.y = 0
        if self.y + self.h > HAUTEUR_ECRAN:
            self.y = HAUTEUR_ECRAN - self.h
            
        # Calculer la vitesse de mouvement pour les effets
        self.vitesse_mouvement = self.y - self.y_precedente


class Balle:
    """
    Représente la balle du jeu avec effets et physique améliorée.

    Attributs:
        x, y (float): position (coin haut-gauche du carré)
        vx, vy (float): vitesse en x et y (pixels/frame)
        t (int): taille (carré)
        effet_y (float): effet de spin vertical
        vitesse_max (float): vitesse maximale de la balle
        derniere_collision (int): temps depuis la dernière collision
    """

    def __init__(self):
        self.t = BAL_TAILLE
        self.effet_y = 0.0  # Effet de spin
        self.vitesse_max = BAL_V_INIT * 2.5  # Limite de vitesse
        self.derniere_collision = 0
        self.impact_force = 0.0  # Force du dernier impact pour les effets visuels
        self.reset(direction_aleatoire=True)

    def reset(self, direction_aleatoire: bool = False) -> None:
        """Replace la balle au centre et (ré)initialise la vitesse."""
        self.x = LARGEUR_ECRAN / 2 - self.t / 2
        self.y = HAUTEUR_ECRAN / 2 - self.t / 2
        # vx vers gauche ou droite
        vx = BAL_V_INIT * (1 if random.random() < 0.5 else -1)
        vy = BAL_V_INIT * random.choice([-0.6, -0.4, -0.2, 0.2, 0.4, 0.6])
        if not direction_aleatoire:
            vx = BAL_V_INIT
            vy = -0.4
        self.vx, self.vy = vx, vy
        self.effet_y = 0.0  # Reset de l'effet
        self.derniere_collision = 0
        self.impact_force = 0.0

    def maj(self) -> None:
        """Met à jour la position + gestion murs haut/bas avec effets."""
        # Appliquer l'effet au mouvement
        self.x += self.vx
        self.y += self.vy + self.effet_y
        
        # Diminuer l'effet avec le temps
        self.effet_y *= 0.98
        
        # Augmenter le compteur de collision
        self.derniere_collision += 1

        # Rebond murs haut/bas
        if self.y <= 0:
            self.y = 0
            self.vy = -self.vy
            # L'effet peut changer lors du rebond sur le mur
            self.effet_y *= -0.5
            # Son de collision avec le mur (son sec)
            pyxel.play(1, 2)
        elif self.y + self.t >= HAUTEUR_ECRAN:
            self.y = HAUTEUR_ECRAN - self.t
            self.vy = -self.vy
            # L'effet peut changer lors du rebond sur le mur
            self.effet_y *= -0.5
            # Son de collision avec le mur (son sec)
            pyxel.play(1, 2)

    def collision_raquette(self, raq: Raquette) -> bool:
        """Teste et gère le rebond sur une raquette avec physique réaliste."""
        # Calcul de la taille actuelle pour collision précise
        centre_terrain = LARGEUR_ECRAN / 2
        distance_centre = abs(self.x + self.t/2 - centre_terrain)
        distance_relative = distance_centre / (LARGEUR_ECRAN / 2)
        taille_min = self.t * 0.6
        taille_max = self.t * 1.4
        taille_actuelle = taille_max - (distance_relative * (taille_max - taille_min))
        
        # Ajustement de position pour collision
        offset = (self.t - taille_actuelle) / 2
        bx1, by1 = self.x + offset, self.y + offset
        bx2, by2 = bx1 + taille_actuelle, by1 + taille_actuelle
        rx1, ry1, rx2, ry2 = raq.rect()

        inter = not (bx2 < rx1 or bx1 > rx2 or by2 < ry1 or by1 > ry2)
        if inter and self.derniere_collision > 5:  # Éviter les collisions multiples
            
            # ===== CALCUL DE LA POSITION D'IMPACT =====
            # Position relative de l'impact sur la raquette (0 = haut, 1 = bas)
            centre_balle_y = by1 + taille_actuelle/2
            impact_relatif = (centre_balle_y - ry1) / raq.h
            impact_relatif = max(0.05, min(0.95, impact_relatif))  # Éviter les extrêmes
            
            # ===== REPOSITIONNEMENT DE LA BALLE =====
            if self.vx < 0:
                self.x = rx2 - offset
            else:
                self.x = rx1 - taille_actuelle - offset

            # ===== SAUVEGARDE DE L'ANGLE D'INCIDENCE =====
            angle_incidence = abs(self.vy / self.vx) if self.vx != 0 else 0
            vitesse_incidence = (self.vx**2 + self.vy**2)**0.5
            
            # ===== CALCUL DU NOUVEL ANGLE SELON LA PHYSIQUE =====
            
            # 1. Facteur de direction selon la zone d'impact
            if impact_relatif < 0.5:
                # Moitié supérieure : renvoi vers le haut
                direction_base = -1
                zone_factor = (0.5 - impact_relatif) * 2  # 0 à 1
            else:
                # Moitié inférieure : renvoi vers le bas  
                direction_base = 1
                zone_factor = (impact_relatif - 0.5) * 2  # 0 à 1
            
            # 2. Intensité de l'angle selon la distance du centre
            # Plus c'est loin du centre, plus l'angle est prononcé
            distance_centre = abs(impact_relatif - 0.5) * 2  # 0 à 1
            intensite_angle = distance_centre * 1.5  # Facteur d'amplification
            
            # 3. Influence de l'angle d'incidence (réflexion partielle)
            # Plus l'angle d'incidence est fort, plus il influence le renvoi
            influence_incidence = min(angle_incidence * 0.4, 0.6)
            
            # 4. Calcul de la nouvelle vitesse horizontale (avec accélération)
            vitesse_horizontale_base = abs(self.vx)
            nouvelle_vitesse_h = min(vitesse_horizontale_base * 1.08, self.vitesse_max)
            self.vx = -nouvelle_vitesse_h if self.vx > 0 else nouvelle_vitesse_h
            
            # 5. Calcul de la nouvelle vitesse verticale
            # Combinaison de la direction voulue et de l'angle d'incidence
            nouvel_angle_voulu = direction_base * intensite_angle * 3.0
            influence_ancienne_direction = self.vy * influence_incidence
            
            self.vy = nouvel_angle_voulu + influence_ancienne_direction
            
            # ===== AJOUT D'ALÉATOIRE POUR LA VARIANCE =====
            # Précision variable selon le type de joueur
            if isinstance(raq, SmartComputer):
                variance = (1 - raq.precision) * 1.5
            else:
                variance = 0.3  # Variance du joueur humain
            
            facteur_aleatoire = random.uniform(-variance, variance)
            self.vy += facteur_aleatoire
            
            # ===== EFFETS ET SPIN AVEC MOUVEMENT DE RAQUETTE =====
            # Effet selon la zone d'impact et la vitesse
            self.effet_y = (impact_relatif - 0.5) * 1.2 * vitesse_incidence * 0.1
            
            # Effet additionnel selon l'angle d'impact
            if distance_centre > 0.3:  # Impact sur les bords
                self.effet_y += direction_base * zone_factor * 0.8
            
            # ===== EFFET DU MOUVEMENT DE LA RAQUETTE =====
            # C'est ici qu'on ajoute la magie du ping-pong réel !
            mouvement_raquette = raq.vitesse_mouvement
            
            if abs(mouvement_raquette) > 0.1:  # La raquette bouge
                # Calculer l'effet selon la direction du mouvement
                if mouvement_raquette > 0:  # Raquette va vers le bas
                    if self.vy > 0:  # Balle va vers le bas - MÊME SENS = SPIN
                        effet_mouvement = mouvement_raquette * 2.0  # Amplification du spin
                        bonus_vitesse = mouvement_raquette * 0.5  # Bonus de vitesse
                    else:  # Balle va vers le haut - SENS INVERSE = SLICE/COUPÉ
                        effet_mouvement = mouvement_raquette * 1.5  # Slice
                        bonus_vitesse = -mouvement_raquette * 0.3  # Ralentissement
                else:  # Raquette va vers le haut
                    if self.vy < 0:  # Balle va vers le haut - MÊME SENS = SPIN
                        effet_mouvement = mouvement_raquette * 2.0  # Amplification du spin
                        bonus_vitesse = -mouvement_raquette * 0.5  # Bonus de vitesse
                    else:  # Balle va vers le bas - SENS INVERSE = SLICE/COUPÉ
                        effet_mouvement = mouvement_raquette * 1.5  # Slice
                        bonus_vitesse = mouvement_raquette * 0.3  # Ralentissement
                
                # Appliquer l'effet du mouvement
                self.effet_y += effet_mouvement
                self.vy += bonus_vitesse
                
                # Effet visuel spécial pour les coups avec mouvement
                if abs(mouvement_raquette) > 1.5:  # Mouvement rapide
                    self.impact_force = min(self.impact_force + 0.3, 1.0)
                    # Ajouter un effet de "smash" ou "slice" visuel
                    if mouvement_raquette * self.vy > 0:  # Même direction = smash
                        self.effet_y *= 1.5  # Effet renforcé
                    else:  # Direction opposée = slice
                        self.effet_y *= 0.7  # Effet atténué mais slice
            
            # ===== LIMITES PHYSIQUES =====
            # Limiter la vitesse verticale pour garder le jeu jouable
            vitesse_v_max = 5.5
            self.vy = max(-vitesse_v_max, min(vitesse_v_max, self.vy))
            
            # S'assurer que la vitesse totale reste raisonnable
            vitesse_totale = (self.vx**2 + self.vy**2)**0.5
            if vitesse_totale > self.vitesse_max:
                ratio = self.vitesse_max / vitesse_totale
                self.vx *= ratio
                self.vy *= ratio
            
            # ===== FEEDBACK SONORE SELON LE TYPE DE COUP =====
            vitesse_totale_finale = (self.vx**2 + self.vy**2)**0.5
            
            # Choisir le son selon l'intensité et le type d'effet
            if abs(mouvement_raquette) > 1.5:  # Mouvement rapide de raquette
                if mouvement_raquette * self.vy > 0:  # Même direction = SMASH
                    pyxel.play(2, 6)  # Son de smash puissant
                else:  # Direction opposée = SLICE
                    pyxel.play(2, 7)  # Son de slice/coupé
            elif abs(self.effet_y) > 1.0:  # Effet fort sans mouvement rapide
                pyxel.play(2, 1)  # Son de collision avec effet
            else:  # Collision normale
                pyxel.play(2, 0)  # Son de collision normale (bruit sourd)
            
            # Son d'accélération si la balle devient très rapide
            if vitesse_totale_finale > self.vitesse_max * 0.8:
                pyxel.play(3, 9)  # Son d'accélération
            
            # ===== FEEDBACK VISUEL =====
            # Plus l'impact est fort, plus l'effet visuel sera marqué
            self.impact_force = min(vitesse_totale_finale / self.vitesse_max, 1.0)
            
            self.derniere_collision = 0
            
        return inter

    def dessiner(self) -> None:
        """Dessine la balle avec effet visuel selon sa vitesse et ses effets."""
        # ===== CALCUL DE LA TAILLE VARIABLE (ILLUSION 3D) =====
        # Position relative par rapport au centre (filet)
        centre_terrain = LARGEUR_ECRAN / 2
        distance_centre = abs(self.x + self.t/2 - centre_terrain)
        distance_relative = distance_centre / (LARGEUR_ECRAN / 2)  # 0 à 1
        
        # Taille variable : plus grande au centre (proche de nous), plus petite sur les côtés
        taille_min = self.t * 0.6  # 60% de la taille normale sur les bords
        taille_max = self.t * 1.4  # 140% de la taille normale au centre
        taille_actuelle = taille_max - (distance_relative * (taille_max - taille_min))
        taille_actuelle = int(taille_actuelle)
        
        # Ajustement de position pour garder le centre de la balle au même endroit
        offset_x = (self.t - taille_actuelle) / 2
        offset_y = (self.t - taille_actuelle) / 2
        pos_x = self.x + offset_x
        pos_y = self.y + offset_y
        
        # ===== COULEURS ET EFFETS =====
        # Couleur variable selon la vitesse
        vitesse_totale = abs(self.vx) + abs(self.vy)
        
        # Couleur de base selon la vitesse
        if vitesse_totale > 7:
            couleur = 8  # Rouge pour vitesse très élevée
        elif vitesse_totale > 5:
            couleur = 10  # Jaune pour vitesse élevée
        elif vitesse_totale > 3:
            couleur = 9  # Orange pour vitesse moyenne
        else:
            couleur = 7  # Blanc pour vitesse normale
        
        # Effet visuel selon l'effet de spin
        effet_total = abs(self.effet_y)
        if effet_total > 0.5:
            if effet_total > 2.0:  # Effet très fort (smash/slice puissant)
                # Alternance rapide pour effet extrême
                if int(self.x + self.y) % 4 < 2:
                    couleur = 14 if self.effet_y > 0 else 12  # Rose pour spin down, bleu pour spin up
            elif effet_total > 1.0:  # Effet moyen
                if int(self.x + self.y) % 6 < 3:
                    couleur = 11  # Cyan pour effet de spin visible
            else:  # Effet léger
                if int(self.x + self.y) % 8 < 4:
                    couleur = 10  # Jaune pour effet léger
        
        # ===== OMBRE POUR EFFET 3D =====
        # Ombre plus prononcée quand la balle est "en l'air" (au centre)
        if taille_actuelle > self.t:  # Balle agrandie = proche
            intensite_ombre = (taille_actuelle - self.t) / (taille_max - self.t)
            taille_ombre = int(taille_actuelle * 0.8)
            pos_ombre_x = pos_x + 2
            pos_ombre_y = pos_y + 2
            couleur_ombre = 1  # Noir foncé
            pyxel.rect(pos_ombre_x, pos_ombre_y, taille_ombre, taille_ombre, couleur_ombre)
        
        # ===== BALLE PRINCIPALE =====
        pyxel.rect(pos_x, pos_y, taille_actuelle, taille_actuelle, couleur)
        
        # ===== EFFET DE BRILLANCE AU CENTRE =====
        if taille_actuelle > self.t * 1.1:  # Effet de brillance quand proche
            # Point brillant sur la balle
            centre_balle_x = pos_x + taille_actuelle // 2
            centre_balle_y = pos_y + taille_actuelle // 2
            pyxel.pset(centre_balle_x - 1, centre_balle_y - 1, 7)  # Point blanc
        
        # ===== TRAÎNÉE AVEC PERSPECTIVE =====
        if vitesse_totale > 5:
            # Calculer la taille de la traînée selon la position précédente
            trail_x = self.x - self.vx * 1.5
            trail_y = self.y - self.vy * 1.5 - self.effet_y * 3
            
            # Taille de la traînée selon sa position
            distance_centre_trail = abs(trail_x + self.t/2 - centre_terrain)
            distance_relative_trail = distance_centre_trail / (LARGEUR_ECRAN / 2)
            taille_trail = int((taille_max - (distance_relative_trail * (taille_max - taille_min))) * 0.5)
            
            if 0 <= trail_x < LARGEUR_ECRAN and 0 <= trail_y < HAUTEUR_ECRAN and taille_trail > 0:
                pyxel.rect(trail_x, trail_y, taille_trail, taille_trail, max(1, couleur-2))
        
        # ===== EFFETS D'IMPACT =====
        if self.derniere_collision < 3 and self.impact_force > 0.7:
            # Flash blanc pour impact puissant (adapté à la taille)
            pyxel.rect(pos_x-1, pos_y-1, taille_actuelle+2, taille_actuelle+2, 7)
            pyxel.rect(pos_x, pos_y, taille_actuelle, taille_actuelle, couleur)
        
        # ===== INDICATEURS D'EFFET DE SPIN AMÉLIORÉS =====
        if abs(self.effet_y) > 0.3:
            direction_effet = 1 if self.effet_y > 0 else -1
            intensite = min(abs(self.effet_y) / 3.0, 1.0)  # Normaliser l'intensité
            
            # Plusieurs points pour effet plus visible
            centre_balle_x = pos_x + taille_actuelle // 2
            centre_balle_y = pos_y + taille_actuelle // 2
            
            # Point principal d'effet
            offset_effet_y = direction_effet * int(taille_actuelle * 0.4 * intensite)
            couleur_effet = 13 if intensite > 0.7 else 5  # Violet intense ou gris
            pyxel.pset(centre_balle_x, centre_balle_y + offset_effet_y, couleur_effet)
            
            # Points secondaires pour effet très fort
            if intensite > 0.8:
                pyxel.pset(centre_balle_x - 1, centre_balle_y + offset_effet_y, couleur_effet)
                pyxel.pset(centre_balle_x + 1, centre_balle_y + offset_effet_y, couleur_effet)
                
                # Ligne d'effet pour smash/slice extrême
                if intensite > 1.5:
                    for i in range(-2, 3):
                        pyxel.pset(centre_balle_x + i, centre_balle_y + offset_effet_y, 8)  # Rouge


class JeuPong:
    """
    Orchestrateur du jeu (boucle Pyxel, états, collisions, score).

    Méthodes publiques:
        maj(): logique du jeu par frame
        dessiner(): rendu graphique par frame
    """

    def __init__(self):
        # État du jeu
        self.etat = "menu"  # "menu", "difficulte", "jeu", "pause"
        self.selection_menu = 0  # 0 = vs Ordinateur, 1 = vs Joueur, 2 = Quitter
        self.selection_difficulte = 0  # 0 = Débutant, 1 = Amateur, 2 = Pro
        self.pause = False
        self.score_g = 0
        self.score_d = 0
        self.mode_ordinateur = True
        self.niveau_ia = "debutant"  # "debutant", "amateur", "pro"
        self.musique_menu_active = False  # Flag pour la musique de menu

        # Les entités seront créées après la sélection du mode
        self.raq_g = None
        self.raq_d = None
        self.balle = None

    def creer_entites(self):
        """Crée les entités du jeu selon le mode choisi."""
        # Ajustement de la taille des raquettes selon la difficulté
        if self.mode_ordinateur:
            if self.niveau_ia == "debutant":
                taille_raquette = RAQ_H * 1.2  # Plus facile : raquettes plus grandes
            elif self.niveau_ia == "amateur":
                taille_raquette = RAQ_H  # Normal
            else:  # pro
                taille_raquette = RAQ_H * 0.7  # Plus difficile : raquettes plus petites
        else:
            taille_raquette = RAQ_H  # Normal pour joueur vs joueur
        
        # Raquette gauche (toujours contrôlée par le joueur)
        self.raq_g = Raquette(
            x=18,  # plus loin du bord
            y=HAUTEUR_ECRAN / 2 - taille_raquette / 2,
            touche_haut=TOUCHES["gauche_haut"],
            touche_bas=TOUCHES["gauche_bas"],
        )
        # Ajuster la taille
        self.raq_g.h = taille_raquette

        # Raquette droite selon le mode choisi
        if self.mode_ordinateur:
            self.raq_d = SmartComputer(
                x=LARGEUR_ECRAN - 18 - RAQ_L,  # plus loin du bord
                y=HAUTEUR_ECRAN / 2 - taille_raquette / 2,
                niveau=self.niveau_ia
            )
            # Ajuster la taille de l'IA aussi
            self.raq_d.h = taille_raquette
        else:
            self.raq_d = Raquette(
                x=LARGEUR_ECRAN - 18 - RAQ_L,  # plus loin du bord
                y=HAUTEUR_ECRAN / 2 - taille_raquette / 2,
                touche_haut=TOUCHES["droite_haut"],
                touche_bas=TOUCHES["droite_bas"],
            )
            # Ajuster la taille
            self.raq_d.h = taille_raquette

        self.balle = Balle()

    def gerer_musique_menu(self):
        """Gère le démarrage et l'arrêt de la musique de menu."""
        if self.etat in ["menu", "difficulte"]:
            # On est dans un menu
            if not self.musique_menu_active:
                # pyxel.playm(0, loop=True)  # Jouer la musique en boucle (désactivé temporairement)
                self.musique_menu_active = True
        else:
            # On n'est plus dans un menu
            if self.musique_menu_active:
                pyxel.stop()  # Arrêter toute la musique
                self.musique_menu_active = False

    def maj_menu(self):
        """Met à jour la logique du menu de sélection."""
        # Gérer la musique de menu
        self.gerer_musique_menu()
        
        # Navigation dans le menu
        if pyxel.btnp(TOUCHES["haut"]) or pyxel.btnp(TOUCHES["gauche_haut"]):
            self.selection_menu = (self.selection_menu - 1) % 3  # 3 options maintenant
            pyxel.play(0, 4)  # Son de navigation
        if pyxel.btnp(TOUCHES["bas"]) or pyxel.btnp(TOUCHES["gauche_bas"]):
            self.selection_menu = (self.selection_menu + 1) % 3  # 3 options maintenant
            pyxel.play(0, 4)  # Son de navigation
        
        # Validation du choix
        if pyxel.btnp(TOUCHES["entree"]) or pyxel.btnp(pyxel.KEY_SPACE):
            pyxel.play(0, 5)  # Son de sélection
            if self.selection_menu == 0:  # vs Ordinateur
                self.mode_ordinateur = True
                self.etat = "difficulte"  # Aller au menu de difficulté
            elif self.selection_menu == 1:  # vs Joueur
                self.mode_ordinateur = False
                self.creer_entites()
                self.etat = "jeu"
            elif self.selection_menu == 2:  # Quitter
                pyxel.quit()

        # Quitter depuis le menu (raccourci Q)
        if pyxel.btnp(TOUCHES["quitter"]):
            pyxel.quit()

    def maj_difficulte(self):
        """Met à jour la logique du menu de difficulté."""
        # Gérer la musique de menu
        self.gerer_musique_menu()
        
        # Navigation dans le menu de difficulté
        if pyxel.btnp(TOUCHES["haut"]) or pyxel.btnp(TOUCHES["gauche_haut"]):
            self.selection_difficulte = (self.selection_difficulte - 1) % 3
            pyxel.play(0, 4)  # Son de navigation
        if pyxel.btnp(TOUCHES["bas"]) or pyxel.btnp(TOUCHES["gauche_bas"]):
            self.selection_difficulte = (self.selection_difficulte + 1) % 3
            pyxel.play(0, 4)  # Son de navigation
        
        # Validation du choix de difficulté
        if pyxel.btnp(TOUCHES["entree"]) or pyxel.btnp(pyxel.KEY_SPACE):
            pyxel.play(0, 5)  # Son de sélection
            niveaux = ["debutant", "amateur", "pro"]
            self.niveau_ia = niveaux[self.selection_difficulte]
            self.creer_entites()
            self.etat = "jeu"
        
        # Retour au menu principal
        if pyxel.btnp(TOUCHES["quitter"]):
            self.etat = "menu"

    def maj_jeu(self):
        """Met à jour la logique du jeu."""
        # Gérer la musique (arrêter la musique de menu si on est en jeu)
        self.gerer_musique_menu()
        
        # Entrées globales
        if pyxel.btnp(TOUCHES["pause"]):
            self.pause = not self.pause
        if pyxel.btnp(TOUCHES["reset"]):
            self.reinitialiser()
        if pyxel.btnp(TOUCHES["quitter"]):
            self.etat = "menu"  # Retour au menu au lieu de quitter
            return

        if self.pause:
            return

        # Mouvements des raquettes
        self.raq_g.maj()
        # si la raquette droite est contrôlée par l'ordinateur
        if isinstance(self.raq_d, SmartComputer):
            self.raq_d.maj(self.balle.y, self.balle)
        else:
            self.raq_d.maj()

        # Mouvement de la balle
        self.balle.maj()

        # Collisions balle/raquettes
        self.balle.collision_raquette(self.raq_g)
        self.balle.collision_raquette(self.raq_d)

        # Buts (sortie à gauche/droite)
        if self.balle.x + self.balle.t < 0:
            self.score_d += 1
            pyxel.play(1, 3)  # Son étouffé de rebond au sol
            self.nouvelle_mise_en_jeu(a_droite=True)
        elif self.balle.x > LARGEUR_ECRAN:
            self.score_g += 1
            pyxel.play(1, 3)  # Son étouffé de rebond au sol
            self.nouvelle_mise_en_jeu(a_droite=False)
        
        # Vérifier victoire pour son spécial
        if self.score_g >= SCORE_MAX or self.score_d >= SCORE_MAX:
            if not hasattr(self, 'victoire_son_joue'):
                pyxel.play(0, 8)  # Mélodie de victoire
                self.victoire_son_joue = True

    # ---------- Logique ----------
    def maj(self) -> None:
        """Met à jour tout l'univers selon l'état actuel."""
        if self.etat == "menu":
            self.maj_menu()
        elif self.etat == "difficulte":
            self.maj_difficulte()
        elif self.etat == "jeu":
            self.maj_jeu()

    def reinitialiser(self) -> None:
        """Remet le score et les positions à zéro."""
        self.score_g = 0
        self.score_d = 0
        if self.raq_g and self.raq_d and self.balle:
            self.raq_g.y = HAUTEUR_ECRAN / 2 - RAQ_H / 2
            self.raq_d.y = HAUTEUR_ECRAN / 2 - RAQ_H / 2
            self.balle.reset(direction_aleatoire=True)
        self.pause = False
        # Reset du flag de victoire pour permettre le son à nouveau
        if hasattr(self, 'victoire_son_joue'):
            delattr(self, 'victoire_son_joue')

    def nouvelle_mise_en_jeu(self, a_droite: bool) -> None:
        """Replace la balle au centre, orientée vers le joueur qui vient d'encaisser."""
        self.balle.reset(direction_aleatoire=True)
        # Oriente la balle vers le camp de celui qui a pris le but
        self.balle.vx = BAL_V_INIT * (1 if a_droite else -1)

    # ---------- Affichage ----------
    def dessiner_difficulte(self) -> None:
        """Dessine le menu de sélection de difficulté."""
        pyxel.cls(COULEUR_FOND)
        
        # Titre
        pyxel.text(160, 60, "DIFFICULTE IA", 7)
        pyxel.text(120, 100, "Choisissez le niveau de l'IA :", 6)
        
        # Options de difficulté
        couleur_debutant = 8 if self.selection_difficulte == 0 else 7
        couleur_amateur = 8 if self.selection_difficulte == 1 else 7
        couleur_pro = 8 if self.selection_difficulte == 2 else 7
        
        pyxel.text(120, 150, "Debutant - Raquettes larges, IA lente", couleur_debutant)
        pyxel.text(120, 180, "Amateur - Raquettes normales, IA equilibree", couleur_amateur)
        pyxel.text(120, 210, "Pro - Raquettes petites, IA experte", couleur_pro)
        
        # Flèche de sélection
        fleche_y = 150 + (self.selection_difficulte * 30)
        pyxel.text(100, fleche_y, ">", 8)
        
        # Instructions
        pyxel.text(80, 280, "Z/S pour naviguer", 6)
        pyxel.text(80, 300, "Entree pour valider", 6)
        pyxel.text(80, 320, "Q pour retour menu principal", 6)

    def dessiner_menu(self) -> None:
        """Dessine le menu de sélection du mode de jeu."""
        pyxel.cls(COULEUR_FOND)
        
        # Titre plus grand et centré
        pyxel.text(200, 60, "P O N G", 7)
        pyxel.text(150, 100, "Choisissez votre mode :", 6)
        
        # Indicateur musique en haut à droite
        if self.musique_menu_active:
            # Petit indicateur musical qui clignote
            if pyxel.frame_count % 60 < 30:  # Clignote toutes les secondes
                pyxel.text(420, 20, "♪", 11)  # Note musicale cyan
        
        # Options du menu
        couleur_vs_ordi = 8 if self.selection_menu == 0 else 7
        couleur_vs_joueur = 8 if self.selection_menu == 1 else 7
        couleur_quitter = 8 if self.selection_menu == 2 else 7
        
        pyxel.text(120, 150, "Joueur vs Ordinateur", couleur_vs_ordi)
        pyxel.text(120, 180, "Joueur vs Joueur", couleur_vs_joueur)
        pyxel.text(120, 210, "Quitter", couleur_quitter)
        
        # Flèche de sélection
        fleche_y = 150 + (self.selection_menu * 30)  # 150, 180, ou 210
        pyxel.text(100, fleche_y, ">", 8)
        
        # Instructions
        pyxel.text(80, 280, "Z/S pour naviguer", 6)
        pyxel.text(80, 300, "Entree ou Espace pour valider", 6)
        pyxel.text(80, 320, "Q pour quitter rapidement", 6)
        """Dessine le menu de sélection du mode de jeu."""
        pyxel.cls(COULEUR_FOND)
        
        # Titre plus grand et centré
        pyxel.text(200, 60, "P O N G", 7)
        pyxel.text(150, 100, "Choisissez votre mode :", 6)
        
        # Options du menu
        couleur_vs_ordi = 8 if self.selection_menu == 0 else 7
        couleur_vs_joueur = 8 if self.selection_menu == 1 else 7
        couleur_quitter = 8 if self.selection_menu == 2 else 7
        
        pyxel.text(120, 150, "Joueur vs Ordinateur", couleur_vs_ordi)
        pyxel.text(120, 180, "Joueur vs Joueur", couleur_vs_joueur)
        pyxel.text(120, 210, "Quitter", couleur_quitter)
        
        # Flèche de sélection
        fleche_y = 150 + (self.selection_menu * 30)  # 150, 180, ou 210
        pyxel.text(100, fleche_y, ">", 8)
        
        # Instructions
        pyxel.text(80, 280, "Z/S pour naviguer", 6)
        pyxel.text(80, 300, "Entree ou Espace pour valider", 6)
        pyxel.text(80, 320, "Q pour quitter rapidement", 6)

    def dessiner_jeu(self) -> None:
        """Dessine l'intégralité de la scène de jeu."""
        pyxel.cls(COULEUR_FOND)

        # Filet central plus détaillé
        for y in range(0, HAUTEUR_ECRAN, 18):  # segments plus espacés
            pyxel.rect(LARGEUR_ECRAN // 2 - 2, y, 4, 9, 5)  # filet plus épais

        # Entités
        if self.raq_g and self.raq_d and self.balle:
            self.raq_g.dessiner()
            self.raq_d.dessiner()
            self.balle.dessiner()

        # Score plus grand et mieux positionné
        pyxel.text(LARGEUR_ECRAN // 2 - 60, 20, f"{self.score_g}", 7)
        pyxel.text(LARGEUR_ECRAN // 2 + 50, 20, f"{self.score_d}", 7)

        # Bandeau d'aide repositionné
        mode_text = f"vs Ordi ({self.niveau_ia.title()})" if self.mode_ordinateur else "vs Joueur"
        pyxel.text(10, HAUTEUR_ECRAN - 90, f"Mode: {mode_text} - Audio 8-bits actif", 6)
        pyxel.text(10, HAUTEUR_ECRAN - 70, "Effet 3D: Balle grandit au centre du terrain", 5)
        pyxel.text(10, HAUTEUR_ECRAN - 60, "Sons: Raquette sourd, Mur sec, Sol etouffe", 5)
        pyxel.text(10, HAUTEUR_ECRAN - 50, "Mouvement raquette: Meme sens = SPIN, Oppose = SLICE", 5)
        pyxel.text(10, HAUTEUR_ECRAN - 40, "Strategie: Haut raquette = renvoi vers haut", 5)
        pyxel.text(10, HAUTEUR_ECRAN - 30, "          Bas raquette = renvoi vers bas", 5)
        pyxel.text(10, HAUTEUR_ECRAN - 20, "Z/S  O/L  (P)ause  (R)eset  (Q)menu", 6)

        # Affichage pause
        if self.pause:
            pyxel.text(200, HAUTEUR_ECRAN // 2 - 10, "PAUSE", 8)

        # Fin de partie
        if self.score_g >= SCORE_MAX or self.score_d >= SCORE_MAX:
            gagnant = "GAUCHE" if self.score_g > self.score_d else "DROITE"
            self.pause = True
            pyxel.text(160, HAUTEUR_ECRAN // 2 - 10, f"VICTOIRE {gagnant} !", 8)
            pyxel.text(140, HAUTEUR_ECRAN // 2 + 20, "Appuie sur R pour rejouer", 13)

    def dessiner(self) -> None:
        """Dessine l'écran selon l'état actuel."""
        if self.etat == "menu":
            self.dessiner_menu()
        elif self.etat == "difficulte":
            self.dessiner_difficulte()
        elif self.etat == "jeu":
            self.dessiner_jeu()


# =========================
# Boucle Pyxel
# =========================
class Application:
    """
    Point d'entrée Pyxel.
    Sépare l'orchestration (JeuPong) de l'initialisation Pyxel.
    """

    def __init__(self):
        pyxel.init(LARGEUR_ECRAN, HAUTEUR_ECRAN, title="PONG - Avec menu de sélection")
        
        # ===== CRÉATION DES SONS 8-BITS =====
        self.creer_sons()
        
        self.jeu = JeuPong()
        pyxel.run(self.jeu.maj, self.jeu.dessiner)
    
    def creer_sons(self):
        """Crée tous les sons 8-bits du jeu."""
        
        # SON 0 : Collision raquette normale (bruit sourd)
        pyxel.sounds[0].set(
            notes="c2",      # Note grave pour son sourd
            tones="p",       # Pulse wave pour effet rétro
            volumes="4",     # Volume moyen
            effects="n",     # Pas d'effet spécial
            speed=15         # Rapide pour collision
        )
        
        # SON 1 : Collision raquette avec effet (son plus aigu)
        pyxel.sounds[1].set(
            notes="f2",      # Plus aigu pour effet
            tones="p",       # Pulse wave
            volumes="5",     # Plus fort
            effects="s",     # Slide pour effet
            speed=12
        )
        
        # SON 2 : Collision mur (son sec et court)
        pyxel.sounds[2].set(
            notes="g3",      # Aigu pour son sec
            tones="t",       # Triangle wave pour son plus sec
            volumes="3",     # Volume modéré
            effects="n",     # Pas d'effet
            speed=25         # Très rapide pour son sec
        )
        
        # SON 3 : Rebond au sol/hors limites (son étouffé terre battue)
        pyxel.sounds[3].set(
            notes="a1g1f1e1", # Descente rapide pour son étouffé
            tones="n",         # Noise pour texture terre battue
            volumes="3210",    # Volume qui diminue
            effects="n",
            speed=20
        )
        
        # SON 4 : Navigation menu (bip doux)
        pyxel.sounds[4].set(
            notes="c4",
            tones="p",
            volumes="2",
            effects="n",
            speed=10
        )
        
        # SON 5 : Sélection menu (confirmation)
        pyxel.sounds[5].set(
            notes="c4e4g4",   # Accord majeur
            tones="ppp",
            volumes="345",     # Crescendo
            effects="nnn",
            speed=8
        )
        
        # SON 6 : Smash puissant (impact fort)
        pyxel.sounds[6].set(
            notes="c1",       # Très grave
            tones="n",        # Noise pour impact
            volumes="7",      # Très fort
            effects="n",
            speed=30          # Très court
        )
        
        # SON 7 : Slice/coupé (son léger et fin)
        pyxel.sounds[7].set(
            notes="a4b4c4",   # Montée en restant dans les octaves valides
            tones="ttt",      # Triangle pour finesse
            volumes="234",
            effects="sss",    # Slide
            speed=15
        )
        
        # SON 8 : Victoire (mélodie de succès)
        pyxel.sounds[8].set(
            notes="c4e4g4c4",  # Accord sans aller trop haut
            tones="pppp",
            volumes="4567",
            effects="nnnn",
            speed=6
        )
        
        # SON 9 : Accélération balle (son qui monte)
        pyxel.sounds[9].set(
            notes="c3d3e3f3",
            tones="pppp",
            volumes="2234",
            effects="ssss",
            speed=12
        )
        
        # ===== MUSIQUE DE MENU (Canaux 10-13) =====
        
        # MÉLODIE PRINCIPALE (Canal 10) - Thème rétro entrainant
        pyxel.sounds[10].set(
            notes="c4c4g3g3a3a3g3 f3f3e3e3d3d3c3",  # Mélodie simple et reconnaissable
            tones="pppppppp pppppppp",                # Pulse wave pour mélodie
            volumes="43434343 43434343",              # Volume variable pour dynamisme
            effects="nnnnnnnn nnnnnnnn",
            speed=6
        )
        
        # HARMONIE (Canal 11) - Accompagnement
        pyxel.sounds[11].set(
            notes="c3e3c3e3 f3a3f3a3 c3e3c3e3 f3a3f3a3", # Harmonies simples
            tones="tttttttt tttttttt tttttttt tttttttt",     # Triangle pour harmonie
            volumes="32323232 32323232 32323232 32323232",
            effects="nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn",
            speed=6
        )
        
        # BASSE (Canal 12) - Ligne de basse
        pyxel.sounds[12].set(
            notes="c2c2c2c2 f2f2f2f2 c2c2c2c2 f2f2f2f2",  # Basse simple
            tones="ssssssss ssssssss ssssssss ssssssss",      # Square wave pour basse
            volumes="55555555 55555555 55555555 55555555",
            effects="nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn",
            speed=6
        )
        
        # PERCUSSION (Canal 13) - Rythme
        pyxel.sounds[13].set(
            notes="c3c3rc3 c3c3rc3 c3c3rc3 c3c3rc3",  # Rythme simple avec pauses
            tones="nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn",      # Noise pour percussion
            volumes="71517151 71517151 71517151 71517151",
            effects="nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn",
            speed=6
        )
        
        # ===== CRÉATION DE LA MUSIQUE COMPLÈTE =====
        # Note : musique désactivée temporairement car problème de syntaxe
        # pyxel.musics[0].set(
        #     ch0=[10],  # Mélodie principale
        #     ch1=[11],  # Harmonie
        #     ch2=[12],  # Basse
        #     ch3=[13]   # Percussion
        # )


# =========================
# Main
# =========================
if __name__ == "__main__":
    Application()