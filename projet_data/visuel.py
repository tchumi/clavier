import tkinter as tk
from PIL import Image, ImageTk

# Crée une fenêtre Tkinter
root = tk.Tk()
root.title("Analyse Biodynamique")

# Charge l'image WebP avec Pillow
image_path = "visuel.webp"
image = Image.open(image_path)

# Convertit l'image pour Tkinter
photo = ImageTk.PhotoImage(image)

# Ajoute l'image à un Label
label = tk.Label(root, image=photo)
label.pack()

# Démarre l'application
root.mainloop()
