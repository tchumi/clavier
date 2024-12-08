import tkinter as tk
from tkinter import Menu, messagebox
import time
from pynput import keyboard
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import pandas as pd

debug = True
MOTDEPASSE = "aze\r" if debug else ".tie5Roanl\r"
ESSAIS = 2 if debug else 10
SUBJECTS = "MMM"
SESSIONS = 1


def process_shift_times(keys_pressed, key_press_times, key_release_times):
    """
    Fusionne les temps de 'Shift' avec la touche suivante.
    Conserve le plus petit temps d'appui et le plus grand temps de relâchement.
    """
    # return keys_pressed, key_press_times, key_release_times
    print(keys_pressed)
    print(f"len(keys_pressed): {len(keys_pressed)}")
    print(key_press_times)
    print(f"len(key_press_times): {len(key_press_times)}")
    print(key_release_times)
    print(f"len(key_release_times): {len(key_release_times)}")

    processed_keys = []
    processed_press_times = []
    processed_release_times = []

    i = 0
    while i < len(keys_pressed):
        if keys_pressed[i] == "Shift":
            if i + 1 < len(keys_pressed) and keys_pressed[i + 1] != "Shift":
                # Traiter la touche suivante après Shift
                next_key = keys_pressed[i + 1].upper()
                press_time = min(key_press_times[i], key_press_times[i + 1])
                release_time = max(key_release_times[i], key_release_times[i + 1])

                processed_keys.append(next_key)
                processed_press_times.append(press_time)
                processed_release_times.append(release_time)
                i += 2  # Passer à la touche après la suivante
            else:
                # Si la touche suivante est aussi Shift ou n'existe pas
                i += 1
        else:
            processed_keys.append(keys_pressed[i])
            processed_press_times.append(key_press_times[i])
            processed_release_times.append(key_release_times[i])
            i += 1

    return processed_keys, processed_press_times, processed_release_times


class KeyPressCaptureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Application de reconnaissance par traitement biodynamique")
        self.menu = Menu(root)
        self.root.config(menu=self.menu)

        # # Chronogramme Canvas (pour suppression et mise à jour)
        self.chronogram_canvas = None

        # Variables de stockage
        self.key_press_times = []
        self.key_release_times = []
        self.keys_pressed = []
        self.shift_pressed = False
        self.attempts = 0
        self.max_attempts = ESSAIS
        self.password = MOTDEPASSE
        self.data = []
        self.data_counter = 0

        file_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Quitter", command=self.quit_application)

        self.capture_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Capture", menu=self.capture_menu)
        self.capture_menu.add_command(
            label="Lancer Capture", command=self.lancer_capture
        )

        self.demo_menu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="Démo", menu=self.demo_menu)
        self.demo_menu.add_command(label="Lancer Démo", command=self.lancer_demo)

        self.menu.add_command(label="Visu_code", command=self.show_code)
        self.menu.add_command(label="Aide", command=self.show_help)
        self.result_text = None

    def quit_application(self):
        """Quitter proprement l'application."""
        self.root.quit()
        self.root.destroy()

    def nettoyer_tkinter(self):
        # Fonction pour nettoyer tous les objets Tkinter de la fenêtre principale sauf le menu
        for widget in self.root.winfo_children():
            if widget != self.menu:
                widget.destroy()

    def lancer_capture(self):
        # Nettoyer tous les objets Tkinter et lancer la fonction foo_capture
        print("Lancement de la capture des touches de claviers")
        self.capture_menu.entryconfig("Lancer Capture", state=tk.DISABLED)
        print("Gel de la capture des touches de claviers")
        self.nettoyer_tkinter()
        self.foo_capture()

    def lancer_demo(self):
        # Désactiver l'élément de menu "Lancer Démo"
        self.demo_menu.entryconfig("Lancer Démo", state=tk.DISABLED)
        self.nettoyer_tkinter()
        self.foo_demo()

    def foo_capture(self):
        # # # Chronogramme Canvas (pour suppression et mise à jour)
        # self.chronogram_canvas = None

        # # Variables de stockage
        # self.key_press_times = []
        # self.key_release_times = []
        # self.keys_pressed = []
        # self.shift_pressed = False

        # Interface utilisateur
        self.input_field = tk.Entry(self.root, width=40)
        self.input_field.pack(pady=10)

        self.init_button = tk.Button(
            self.root, text="Initialiser", command=self.reset_input
        )
        self.init_button.pack(pady=5)

        self.validate_button = tk.Button(
            self.root, text="Validation", command=self.on_validate
        )
        self.validate_button.pack(pady=5)

        self.quitter_capture_button = tk.Button(
            self.root, text="Quitter", command=self.on_quitter_menu_capture
        )
        self.quitter_capture_button.pack(pady=5)

        self.result_text = tk.Text(self.root, height=15, width=80)
        self.result_text.pack(pady=10)

        self.start_listen_keys()

    def start_listen_keys(self):
        self.reset_input()
        # Capture des touches
        self.listener = keyboard.Listener(
            on_press=self.on_press, on_release=self.on_release
        )
        self.listener.start()

    def foo_demo(self):
        self.attempts = 0
        self.data_counter = 0
        self.nettoyer_tkinter()
        # Ajouter un encadré avec la consigne dans la fenêtre principale
        consigne = (
            "Reconnsaissance de votre mot de passe par traitement biodynamique.\n"
            "Veuillez saisir le code suivant puis valider avec la touche RETURN <.tie5Roanl>.\n"
            "Vous avez 10 essais avant réinitialisation."
        )
        label = tk.Label(
            self.root, text=consigne, padx=20, pady=20, borderwidth=2, relief="groove"
        )
        label.pack(padx=20, pady=20)

        # Ajouter un champ de saisie pour l'utilisateur
        self.input_field = tk.Entry(self.root, width=40)
        self.input_field.pack(pady=20)
        # self.input_field.bind("<Return>", self.validate_password_event)
        self.input_field.bind("<KeyRelease-Return>", self.validate_password_event)

        # Ajouter un bouton de validation
        self.quitter_demo_button = tk.Button(
            self.root, text="Quitter", command=self.on_quitter_menu_demo
        )
        self.quitter_demo_button.pack(pady=10)

        # Ajouter un compteur de tentatives
        self.attempts_label = tk.Label(
            self.root,
            text=f"Tentatives restantes : {self.max_attempts - self.attempts}",
        )
        self.attempts_label.pack(pady=10)

        self.start_listen_keys()

    def validate_password_event(self, event):
        self.validate_password()

    def validate_password(self):
        entered_password = self.input_field.get() + "\r"
        print(f"Entered password: {entered_password}")
        self.input_field.delete(0, tk.END)
        if entered_password == self.password:
            hold_times, dd_times, ud_times = self.extract_durations()
            self.prepare_data(hold_times, dd_times, ud_times)
            self.attempts += 1
            self.attempts_label.config(
                text=f"Tentatives restantes : {self.max_attempts - self.attempts}"
            )
            if self.attempts >= self.max_attempts:
                # Afficher un sablier avec un message
                hourglass_frame = tk.Frame(self.root)
                hourglass_frame.pack(pady=20)

                hourglass = tk.Label(hourglass_frame, text="⏳", font=("Helvetica", 48))
                hourglass.pack(side=tk.LEFT, padx=10)

                message = tk.Label(
                    hourglass_frame,
                    text="Contrôle de l'identité en cours...",
                    font=("Helvetica", 16),
                )
                message.pack(side=tk.LEFT, padx=10)

                self.root.update()
                time.sleep(2)
                hourglass_frame.destroy()
                time.sleep(1)
                if self.check_identity() < 0.7:
                    # TODO réinitialiser les données et aller sur un menu de contrôle de l'identité par phrase secrète
                    messagebox.showinfo(
                        "Échec", "Test rejeté. Passez au contrôle d'une phrase secrète."
                    )
                else:
                    messagebox.showinfo(
                        "Succès", "Test réussi. Vous êtes bien vous-même."
                    )
        else:
            messagebox.showinfo(
                "Le mot de passe ne correspond pas, veuillez recommencer."
            )
        self.reset_capture()

    def check_identity(self):
        # Ajoutez ici le code pour comparer les données avec un modèle de prédiction
        # et retourner le score de similarité
        # en attendant, on retourne un score aléatoire
        return random.random()

    def extract_durations(self):

        self.keys_pressed, self.key_press_times, self.key_release_times = (
            process_shift_times(
                self.keys_pressed, self.key_press_times, self.key_release_times
            )
        )

        hold_times = [
            release - press
            for press, release in zip(self.key_press_times, self.key_release_times)
        ]
        dd_times = [
            press2 - press1
            for press1, press2 in zip(self.key_press_times, self.key_press_times[1:])
        ]
        ud_times = [
            press2 - release1
            for release1, press2 in zip(
                self.key_release_times, self.key_press_times[1:]
            )
        ]
        return hold_times, dd_times, ud_times

    def prepare_data(self, hold_times, dd_times, ud_times):
        # faire une liste en ajoutant successivement hold_times, dd_times, ud_times
        liste = []
        liste.append(SUBJECTS)
        liste.append(SESSIONS)
        liste.append(self.data_counter)
        self.data_counter += 1
        liste.append(hold_times[0])
        for i in range(1, len(hold_times)):
            liste.append(dd_times[i - 1])
            liste.append(ud_times[i - 1])
            liste.append(hold_times[i])

        self.data.append(liste)
        print(liste)
        # TODO prépare dataframe pour l'analyse
        # df = pd.DataFrame(data)
        # print(df)
        # Ajoutez ici le code pour utiliser le DataFrame avec un modèle de prédiction

    def reset_capture(self):
        self.input_field.delete(0, tk.END)
        self.key_press_times.clear()
        self.key_release_times.clear()
        self.keys_pressed.clear()
        self.shift_pressed = False

        # Réinitialisation des données
        self.keys_pressed = []
        self.hold_times = []
        self.dd_times = []
        self.ud_times = []

    def reset_input(self):
        """Réinitialise le champ de saisie et les données."""
        if self.result_text:
            self.result_text.delete(1.0, tk.END)

        self.reset_capture()

        # Supprimer l'ancien graphique s'il existe
        if self.chronogram_canvas:
            self.chronogram_canvas.get_tk_widget().destroy()
            self.chronogram_canvas = None

    def on_press(self, key):
        """Capture les touches pressées."""
        try:
            if hasattr(key, "char") and key.char:
                self.key_press_times.append(time.time())
                self.keys_pressed.append(
                    key.char.upper() if self.shift_pressed else key.char
                )
            elif key == keyboard.Key.shift and not self.shift_pressed:
                self.shift_pressed = True
                self.key_press_times.append(time.time())
                self.keys_pressed.append("Shift")
            elif key == keyboard.Key.enter:
                self.key_press_times.append(time.time())
                self.keys_pressed.append("Return")
        except AttributeError:
            pass

    def on_release(self, key):
        """Capture le relâchement des touches."""
        if key == keyboard.Key.shift:
            self.shift_pressed = False
        self.key_release_times.append(time.time())

    def on_quitter_menu_capture(self):
        """Quitter proprement l'application."""
        self.listener.stop()
        self.nettoyer_tkinter()
        self.capture_menu.entryconfig("Lancer Capture", state=tk.NORMAL)

    def on_quitter_menu_demo(self):
        """Quitter proprement l'application."""
        self.nettoyer_tkinter()
        self.demo_menu.entryconfig("Lancer Démo", state=tk.NORMAL)

    def on_validate(self):
        """Traite la saisie et affiche les résultats."""

        hold_times, dd_times, ud_times = self.extract_durations()

        dd_times_info = dd_times.copy()
        ud_times_info = ud_times.copy()

        # Ajouter un temps de maintien et un temps DD pour la première touche
        dd_times_info.append(0)
        ud_times_info.append(0)
        print(f"hold_times: {hold_times}")
        print(f"ud_times: {ud_times_info}")
        print(f"dd_times: {dd_times_info}")

        self.result_text.delete(1.0, tk.END)

        for i, key in enumerate(self.keys_pressed):
            self.result_text.insert(
                tk.END,
                f" Touche: {key} - Hold Time H : {hold_times[i]:.4f} s + UD : {ud_times_info[i]:.4f}, s = DD : {dd_times_info[i]:.4f} s\n",
            )

        self.show_chronogram(hold_times, dd_times, ud_times)

    def show_chronogram(self, hold_times, dd_times, ud_times):
        """Affiche les chronogrammes des temps H-UD et DD."""
        fig, axes = plt.subplots(
            2, 1, figsize=(10, 10), gridspec_kw={"height_ratios": [2, 1]}
        )

        # --- Chronogramme H-UD ---
        ax1 = axes[0]
        labels = []
        times = []
        positions = []

        bar_width = 0.4
        current_position = 0

        for i, key in enumerate(self.keys_pressed):
            # Temps H
            labels.append(f"H-{key}")
            times.append(hold_times[i])
            positions.append(current_position)
            current_position += bar_width

            # Temps UD
            if i < len(ud_times):
                labels.append(f"UD-{key}")
                times.append(ud_times[i])
                positions.append(current_position)
                current_position += bar_width
        print(positions)
        print(times)
        ax1.bar(
            positions,
            times,
            width=bar_width,
            color=["blue", "orange"] * len(self.keys_pressed),
        )

        ax1.set_ylabel("Temps (s)")
        ax1.set_title("Chronogramme des temps H et UD")
        ax1.set_xticks(positions)
        ax1.set_xticklabels(labels, rotation=45, ha="right")
        ax1.grid(axis="y", linestyle="--", alpha=0.7)

        # --- Chronogramme DD ---
        ax2 = axes[1]
        positions_dd = positions.copy()
        times_dd = []
        # # Créer les positions pour les temps DD
        for i in range(len(dd_times)):
            times_dd.append(dd_times[i])
            times_dd.append(dd_times[i])
        times_dd.append(0)
        # Ajuster les positions pour correspondre aux temps DD
        # positions_dd = positions_dd[: len(dd_times)]

        print(positions_dd)
        print(times_dd)
        ax2.bar(
            positions_dd,
            times_dd,
            width=bar_width,
            color="green",
            label="DD (Down-Down)",
        )

        ax2.set_ylabel("Temps (s)")
        ax2.set_xlabel("Temps cumulé")
        ax2.set_title("Chronogramme des temps DD (Continu)")
        ax2.grid(axis="y", linestyle="--", alpha=0.7)

        # Supprimer l'ancien graphique si existant
        if self.chronogram_canvas:
            self.chronogram_canvas.get_tk_widget().destroy()

        # Afficher les graphiques dans le cadre Tkinter
        self.chronogram_canvas = FigureCanvasTkAgg(fig, master=self.root)
        self.chronogram_canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.chronogram_canvas.draw()

    def show_code(self):
        """Affiche le code actuel dans une fenêtre popup."""
        code_window = tk.Toplevel(self.root)
        code_window.title("Exploration")
        code_window.geometry("800x600")

        code_text = tk.Text(code_window, wrap=tk.WORD)
        code_text.pack(expand=True, fill=tk.BOTH)

        with open(__file__, "r", encoding="utf-8") as file:
            code_text.insert(tk.END, file.read())
        code_text.configure(state=tk.DISABLED)

    def show_help(self):
        """Affiche un message pour guider la démo."""
        messagebox.showinfo(
            "Démo",
            "Saisissez du texte dans le champ de saisie, validez avec le bouton 'Validation', "
            "et voyez les résultats analysés apparaître ci-dessous.",
        )


def main():
    root = tk.Tk()
    app = KeyPressCaptureApp(root)
    # root.attributes("-fullscreen", True)
    root.state("zoomed")
    root.mainloop()


if __name__ == "__main__":
    main()
