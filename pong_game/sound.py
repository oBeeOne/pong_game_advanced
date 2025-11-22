import pyxel

def creer_sons() -> None:
    # Sons individuels
    pyxel.sounds[0].set(notes="c2", tones="p", volumes="4", effects="n", speed=15)
    pyxel.sounds[1].set(notes="f2", tones="p", volumes="5", effects="s", speed=12)
    pyxel.sounds[2].set(notes="g3", tones="t", volumes="3", effects="n", speed=25)
    pyxel.sounds[3].set(notes="a1g1f1e1", tones="n", volumes="3210", effects="n", speed=20)
    pyxel.sounds[4].set(notes="c4", tones="p", volumes="2", effects="n", speed=10)
    pyxel.sounds[5].set(notes="c4e4g4", tones="ppp", volumes="345", effects="nnn", speed=8)
    pyxel.sounds[6].set(notes="c1", tones="n", volumes="7", effects="n", speed=30)
    pyxel.sounds[7].set(notes="a4b4c4", tones="ttt", volumes="234", effects="sss", speed=15)
    pyxel.sounds[8].set(notes="c4e4g4c4", tones="pppp", volumes="4567", effects="nnnn", speed=6)
    pyxel.sounds[9].set(notes="c3d3e3f3", tones="pppp", volumes="2234", effects="ssss", speed=12)

    # Sons composant la musique du menu
    pyxel.sounds[10].set(notes="c4c4g3g3a3a3g3 f3f3e3e3d3d3c3", tones="pppppppp pppppppp", volumes="43434343 43434343", effects="nnnnnnnn nnnnnnnn", speed=6)
    pyxel.sounds[11].set(notes="c3e3c3e3 f3a3f3a3 c3e3c3e3 f3a3f3a3", tones="tttttttt tttttttt tttttttt tttttttt", volumes="32323232 32323232 32323232 32323232", effects="nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn", speed=6)
    pyxel.sounds[12].set(notes="c2c2c2c2 f2f2f2f2 c2c2c2c2 f2f2f2f2", tones="ssssssss ssssssss ssssssss ssssssss", volumes="55555555 55555555 55555555 55555555", effects="nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn", speed=6)
    pyxel.sounds[13].set(notes="c3c3rc3 c3c3rc3 c3c3rc3 c3c3rc3", tones="nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn", volumes="71517151 71517151 71517151 71517151", effects="nnnnnnnn nnnnnnnn nnnnnnnn nnnnnnnn", speed=6)
    # Variations de fin de boucle menu
    pyxel.sounds[14].set(notes="g3a3g3e3 d3c3", tones="pppppp", volumes="444444", effects="nnnnnn", speed=6)
    pyxel.sounds[15].set(notes="e3c3e3c3 d3g2", tones="tttttt", volumes="333333", effects="nnnnnn", speed=6)
    pyxel.sounds[16].set(notes="rc2rc2g2", tones="ssssss", volumes="555555", effects="nnnnnn", speed=6)
    pyxel.sounds[17].set(notes="c3rc3rc3r", tones="nnnnnn", volumes="717171", effects="nnnnnn", speed=6)

    # Victoire (fanfare courte)
    # Remplacer c5 (hors plage acceptée) par c4 pour éviter erreur
    pyxel.sounds[18].set(notes="c4e4g4c4", tones="pppp", volumes="4567", effects="nnnn", speed=5)
    pyxel.sounds[19].set(notes="g3c4e4", tones="ttt", volumes="345", effects="nnn", speed=7)

    # Défaite (descente mineure)
    pyxel.sounds[20].set(notes="e4d4c4a3", tones="pppp", volumes="5432", effects="nnnn", speed=6)
    pyxel.sounds[21].set(notes="c3g2e2", tones="ttt", volumes="432", effects="nnn", speed=8)

    # Musique menu (index 0) avec variation terminale (loopée)
    pyxel.musics[0].set([10, 14], [11, 15], [12, 16], [13, 17])
    # Musique victoire (index 1, non loop)
    pyxel.musics[1].set([18], [19], [], [])
    # Musique défaite (index 2, non loop)
    pyxel.musics[2].set([20], [21], [], [])
    # Musique menu étendue (index 3) introduisant une deuxième boucle plus riche
    # Réutilise base + variation + reprise mélodie accélérée (sons existants réordonnés)
    pyxel.sounds[22].set(notes="c4e4g4e4 c4e4", tones="pppppp pppp", volumes="555555 5454", effects="nnnnnn nnnn", speed=5)
    pyxel.sounds[23].set(notes="c3g3c3g3 e3c3", tones="tttttt tttt", volumes="333333 3232", effects="nnnnnn nnnn", speed=5)
    pyxel.sounds[24].set(notes="c2r c2r g2r", tones="ssss sss sss", volumes="5555 555 555", effects="nnnn nnn nnn", speed=6)
    pyxel.sounds[25].set(notes="c3c3c3c3 c3c3", tones="nnnnnn nnnn", volumes="717171 7171", effects="nnnnnn nnnn", speed=6)
    pyxel.musics[3].set([10,22,14], [11,23,15], [12,24,16], [13,25,17])
    # Musique fade-out (index 4) volumes décroissants
    pyxel.sounds[26].set(notes="c4c4c4c4", tones="p p p p", volumes="4443", effects="n n n n", speed=8)
    pyxel.sounds[27].set(notes="g3g3g3g3", tones="t t t t", volumes="3332", effects="n n n n", speed=8)
    pyxel.musics[4].set([26], [27], [], [])
