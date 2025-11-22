import pyxel

def creer_sons() -> None:
    # SON 0 : Collision raquette normale (bruit sourd)
    pyxel.sounds[0].set(
        notes="c2",
        tones="p",
        volumes="4",
        effects="n",
        speed=15,
    )

    # SON 1 : Collision raquette avec effet (son plus aigu)
    pyxel.sounds[1].set(
        notes="f2",
        tones="p",
        volumes="5",
        effects="s",
        speed=12,
    )

    # SON 2 : Collision mur (son sec et court)
    pyxel.sounds[2].set(
        notes="g3",
        tones="t",
        volumes="3",
        effects="n",
        speed=25,
    )

    # SON 3 : Rebond au sol/hors limites (son étouffé terre battue)
    pyxel.sounds[3].set(
        notes="a1g1f1e1",
        tones="n",
        volumes="3210",
        effects="n",
        speed=20,
    )

    # SON 4 : Navigation menu (bip doux)
    pyxel.sounds[4].set(
        notes="c4",
        tones="p",
        volumes="2",
        effects="n",
        speed=10,
    )

    # SON 5 : Sélection menu (confirmation)
    pyxel.sounds[5].set(
        notes="c4e4g4",
        tones="ppp",
        volumes="345",
        effects="nnn",
        speed=8,
    )

    # SON 6 : Smash puissant (impact fort)
    pyxel.sounds[6].set(
        notes="c1",
        tones="n",
        volumes="7",
        effects="n",
        speed=30,
    )

    # SON 7 : Slice/coupé (son léger et fin)
    pyxel.sounds[7].set(
        notes="a4b4c4",
        tones="ttt",
        volumes="234",
        effects="sss",
        speed=15,
    )

    # SON 8 : Victoire (mélodie de succès)
    pyxel.sounds[8].set(
        notes="c4e4g4c4",
        tones="pppp",
        volumes="4567",
        effects="nnnn",
        speed=6,
    )

    # SON 9 : Accélération balle (son qui monte)
    pyxel.sounds[9].set(
        notes="c3d3e3f3",
        tones="pppp",
        volumes="2234",
        effects="ssss",
        speed=12,
    )

    # Musique de menu (désactivée pour l’instant)
    # pyxel.musics[0].set(ch0=[10], ch1=[11], ch2=[12], ch3=[13])
