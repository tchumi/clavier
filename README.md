Présentation du projet : voir Keymatch.pdf


Environnement
    - Python 3.10.11
    - installer les dépendances avec pip install -r requirements.txt


Lancement du frontend
    - il s'agit d'une UI développée sous python avec la librairie native 'Tkinter', l'UI s'exécute en mode local
    - se placer dans le répertoire 'frontend'
    - dans le terminal exécuter le script par : python main_tk.py


Lancement du backend
    - il s'agit d'une API développée sous python avec la librairie Fastapi
    - le swagger est accessible dans le navigateur sur le port 8000 à l'adresse : localhost:8000/docs
    - dans le terminal exécuter le script par :  uvicorn main:app --host 127.0.0.1 --port 8000 --reload


Notebook exploratoire
    - voir répertoire exploration_dataset
