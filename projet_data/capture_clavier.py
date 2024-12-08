from pynput import keyboard
import time
import pandas as pd

# Variables pour capturer les événements
key_press_times = []
key_release_times = []
keys_pressed = []


# Fonctions pour capturer les événements de frappe
def on_press(key):
    try:
        key_press_times.append(time.time())
        keys_pressed.append(key.char)  # Récupérer le caractère saisi
        print(f"Touche pressée : {key.char}, Timestamp : {key_press_times[-1]}")
    except AttributeError:
        keys_pressed.append(str(key))  # Pour les touches spéciales
        print(f"Touche spéciale pressée : {key}, Timestamp : {key_press_times[-1]}")


def on_release(key):
    key_release_times.append(time.time())
    print(f"Touche relâchée : {key}, Timestamp : {key_release_times[-1]}")
    if key == keyboard.Key.esc:
        # Arrête le listener en appuyant sur Échap
        return False


# Fonction pour afficher le chronogramme
def display_chronogram(keys, hold_times, dd_times=None, ud_times=None):
    print("\nChronogramme des trois premières touches :")
    max_time = max(
        hold_times + [time for time in (dd_times + ud_times) if time is not None],
        default=0.001,
    )

    for i, key in enumerate(keys):
        print(f"Touche {key}:")
        print(f"  H (Hold Time):  {'█' * int((hold_times[i] / max_time) * 50)}")
        if i < len(dd_times) and len(dd_times) > 0:  # Éviter les accès hors limites
            print(f"  DD (Press-to-Press): {'█' * int((dd_times[i] / max_time) * 50)}")
            print(
                f"  UD (Release-to-Press): {'█' * int((ud_times[i] / max_time) * 50)}"
            )
        print()


# Fonction principale
def main():
    print("Saisissez une séquence de touches (appuyez sur Échap pour terminer) :")

    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    # Vérification si au moins 3 touches ont été saisies
    if len(keys_pressed) < 3:
        print("Moins de trois touches saisies. Veuillez recommencer.")
        return

    # Calcul des métriques H, DD, et UD pour les trois premières touches
    hold_times = [
        key_release_times[i] - key_press_times[i] for i in range(len(keys_pressed))
    ]
    dd_times = [None] + [
        key_press_times[i + 1] - key_press_times[i]
        for i in range(len(keys_pressed) - 1)
    ]
    ud_times = [None] + [
        key_press_times[i + 1] - key_release_times[i]
        for i in range(len(keys_pressed) - 1)
    ]

    # Affichage du tableau des résultats
    data = {
        "Key": keys_pressed[:3],
        "H (Hold Time)": hold_times[:3],
        "DD (Press to Press)": dd_times[:3],  # Inclut None pour la première touche
        "UD (Release to Press)": ud_times[:3],  # Inclut None pour la première touche
    }
    df = pd.DataFrame(data)

    print("\nRésultats pour les trois premières touches :")
    print(df.to_string(index=False))

    # Affichage du chronogramme
    display_chronogram(keys_pressed[:1], hold_times[:1], [], [])
    display_chronogram(keys_pressed[1:3], hold_times[1:3], dd_times[1:3], ud_times[1:3])


# Exécution du script
if __name__ == "__main__":
    main()
