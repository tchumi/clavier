import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime
from sklearn.preprocessing import StandardScaler
import numpy as np

# Exemple de texte à saisir
text_to_type = ".tie5Roanl"

# Initialisation du nombre de tentatives et du seuil de probabilité
max_attempts = 10
probability_threshold = 0.7

# Fonction pour simuler l'extraction de temps de pression et de changement de touche
def extract_key_press_times(text, typed_text):
    times = []
    prev_time = time.time()
    for i, char in enumerate(typed_text):
        current_time = time.time()
        duration = current_time - prev_time  # Temps entre deux frappes
        times.append(duration)
        prev_time = current_time
    return times

# Fonction pour prédire l'auteur en utilisant le modèle pré-entraîné
# Fonction pour prédire l'auteur en utilisant le modèle pré-entraîné
def predict_author(input_data):
    # Nous prenons uniquement la colonne 'Duree_pression' qui contient les données numériques
    input_data_numeric = input_data[['Duree_pression']].values
    
    # Vérification que les données sont numériques
    if input_data_numeric.ndim == 1:
        input_data_numeric = input_data_numeric.reshape(-1, 1)

    # Prétraiter les données avant la prédiction (par exemple, standardisation)
    scaler = StandardScaler()
    input_data_scaled = scaler.fit_transform(input_data_numeric)

    # Probabilité simulée de prédiction
    # prediction = model.predict(input_data_scaled)  # Utiliser le modèle réel ici
    # prob = np.max(prediction)  # La probabilité maximale de la prédiction
    prob = random.uniform(0, 1)  # Pour la simulation, générer une probabilité aléatoire
    return prob

# Fonction principale de l'UI
def main():
    # Afficher le texte à saisir
    st.title("Saisie du mot de passe")
    st.write(f"Veuillez saisir exactement ce texte : **{text_to_type}**")

    # Initialisation du nombre de tentatives et du tableau des tentatives dans session_state
    if 'attempt' not in st.session_state:
        st.session_state.attempt = 0
        st.session_state.rejected = False
        st.session_state.times = []  # Liste pour stocker les durées de saisie

    # Afficher le compteur de tentatives
    st.write(f"Tentative {st.session_state.attempt + 1}/{max_attempts}")

    # Champ de saisie pour l'utilisateur avec un 'key' unique pour chaque tentative
    typed_text = st.text_input(f"Saisir le texte (Tentative {st.session_state.attempt + 1}):", key="input_text")

    # Bouton de validation
    validate_button = st.button('Valider', key="validate_button")

    if validate_button:
        st.write("Validation en cours...")
        st.write("text_to_type : ", text_to_type)
        st.write("typed_text : ", typed_text)
        if typed_text:
            if typed_text == text_to_type:
                # Extraction des temps de frappe
                times = extract_key_press_times(text_to_type, typed_text)

                # Ajouter les durées à la liste des durées dans session_state
                st.session_state.times = times

                # Créer un dataframe avec les durées extraites
                df = pd.DataFrame({
                    'Touche': list(typed_text),
                    'Duree_pression': times
                })

                # Afficher le dataframe
                st.write("Données extraites :")
                st.write(df)

                # Prédire l'auteur avec le modèle
                prob = predict_author(df)

                # Afficher la probabilité de la prédiction
                st.write(f"Probabilité de la prédiction : {prob:.2f}")

                # Si la probabilité est suffisante, on accepte la saisie
                if prob >= probability_threshold:
                    st.success("Auteur reconnu avec succès!")
                    st.session_state.attempt = 0  # Réinitialiser le compteur de tentatives après succès
                else:
                    st.warning("La probabilité est insuffisante. Essayez à nouveau.")
                    st.session_state.attempt += 1  # Augmenter le nombre de tentatives
            else:
                st.error("Le texte saisi ne correspond pas à celui attendu. Essayez encore.")
        else:
            st.warning("Veuillez saisir un texte avant de valider.")

    # Vérification après 10 tentatives
    if st.session_state.attempt == max_attempts:
        st.session_state.rejected = True
        st.error(f"Le test est rejeté après {max_attempts} tentatives. Probabilité trop faible.")

    # Affichage des durées de saisie (bandeau inférieur pour le développement)
    if st.session_state.times:
        st.markdown(f"### Temps de saisie : {', '.join([f'{t:.2f}s' for t in st.session_state.times])}")

# Exécution de l'UI
if __name__ == "__main__":
    main()
