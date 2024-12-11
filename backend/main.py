import os
import pickle
import pandas as pd
import numpy as np
import pickle
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier

app = FastAPI()

# Charger le modèle et scaler
# model, scaler = load_model()


# Définir le chemin pour sauvegarder le modèle
MODEL_PATH = "model.pkl"

# Endpoint payloads
class CapturePayload(BaseModel):
    captures: List[List[float]]

class RecordPayload(BaseModel):
    author: str
    captures: List[List[float]]

class RecordPayload(BaseModel):
    data: List[Dict[str, Any]]

col=['subject', 'sessionIndex', 'rep', 'H.period', 'DD.period.t',
       'UD.period.t', 'H.t', 'DD.t.i', 'UD.t.i', 'H.i', 'DD.i.e', 'UD.i.e',
       'H.e', 'DD.e.five', 'UD.e.five', 'H.five', 'DD.five.Shift.r',
       'UD.five.Shift.r', 'H.Shift.r', 'DD.Shift.r.o', 'UD.Shift.r.o', 'H.o',
       'DD.o.a', 'UD.o.a', 'H.a', 'DD.a.n', 'UD.a.n', 'H.n', 'DD.n.l',
       'UD.n.l', 'H.l', 'DD.l.Return', 'UD.l.Return', 'H.Return']


def train(data):
    # Retirer les colonnes non pertinentes
    data_cleaned = data.drop(['subject', 'sessionIndex', 'rep'], axis=1)

    # Sélectionner uniquement les colonnes quantitatives (numériques)
    X = data_cleaned.select_dtypes(include=['float64', 'int64'])  # Sélectionne les colonnes numériques
    y = data['subject']  # La colonne 'subject' comme cible

    # Encoder les labels en entiers si ce n'est pas déjà fait
    y_y = pd.Categorical(y).codes  # Encoder les labels de 'subject' en entiers si ce n'est pas déjà fait
    # Encoder les labels en entiers si ce n'est pas déjà fait
    codes = pd.Categorical(y).codes  # Encoder les labels de 'subject' en entiers si ce n'est pas déjà fait
    categories=pd.Categorical(y).categories
    # Séparer les données en jeu d'entraînement et de test
    X_train, X_test, y_train, y_test = train_test_split(X, y_y, test_size=0.3, random_state=42)

    # Appliquer la normalisation (standardisation)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Création du modèle MLPClassifier
    model = MLPClassifier(hidden_layer_sizes=(128, 64), activation='relu', max_iter=50, random_state=42)

    # Entraînement du modèle
    model.fit(X_train_scaled, y_train)

    # Précision sur les données de test
    test_accuracy = model.score(X_test_scaled, y_test)
    dico_accuracy = {"test_accuracy": test_accuracy}
    return model, scaler, codes,categories, dico_accuracy



def predict_author_with_threshold(model, scaler, data, threshold, classes):
    # Prétraiter les données
    data_scaled = scaler.transform(data.reshape(1, -1))
    
    # Prédiction des probabilités
    probabilities = model.predict_proba(data_scaled)[0]
    
    # Identifier la classe avec la probabilité maximale
    max_prob = np.max(probabilities)
    predicted_class = classes[np.argmax(probabilities)]
        
    # Vérifier si la probabilité maximale dépasse le seuil
    accepted = max_prob >= threshold
    
    # Retourner un dictionnaire avec les résultats
    return {
        "predicted_class": predicted_class,
        "max_prob": max_prob,
        "accepted": accepted
    }



@app.get("/")
def read_root():
    return {"Application": "ready"}


@app.post("/train_model_full_dataset")
def train_model_full_dataset():
    data=pd.read_csv('DSL-StrongPasswordData.csv')
    model, scaler, codes, categories, dico_accuracy = train(data)
    # Sauvegarder le modèle
    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "scaler": scaler}, f)

    return dico_accuracy


@app.post("/record_password")
def record_password():
    df=pd.read_csv('keyboard_capture.csv')
    df.columns=col
    df_control=df.iloc[[0]]
    df_train=df.iloc[1:]
    # Ajouter les nouvelles observations
    data=pd.read_csv('DSL-StrongPasswordData.csv')
    updated_data = pd.concat([data, df_train], ignore_index=True)
    model, scaler, codes, categories, dico_accuracy = train(updated_data)
    input_data=df_control.drop(['subject', 'sessionIndex', 'rep'], axis=1)
    result = predict_author_with_threshold(
            model=model,
            scaler=scaler,
            data=input_data.values,
            threshold=0.8,
            classes=np.unique(codes)
        )

    # Affichage du résultat
    if result["accepted"] and categories[result["predicted_class"]]== df_control['subject'].values[0]:
        decision=f"Utilisateur {df_control['subject'].values[0]} reconnu comme le nouvel auteur."
    else:
        decision=f"Vérification échouée. Auteur {df_control['subject'].values[0]} non reconnu. Accès refusé."

    print(decision)

    return {"decision": decision}

@app.post("/record_password_with_payload")
def record_password_with_payload(payload: RecordPayload):
    # Convertir le JSON en DataFrame
    df = pd.DataFrame(payload.data)
    df.columns=col
    df_control=df.iloc[[0]]
    df_train=df.iloc[1:]
    # Ajouter les nouvelles observations
    data=pd.read_csv('DSL-StrongPasswordData.csv')
    updated_data = pd.concat([data, df_train], ignore_index=True)
    model, scaler, codes, categories, dico_accuracy = train(updated_data)
    input_data=df_control.drop(['subject', 'sessionIndex', 'rep'], axis=1)
    result = predict_author_with_threshold(
            model=model,
            scaler=scaler,
            data=input_data.values,
            threshold=0.8,
            classes=np.unique(codes)
        )

    # Affichage du résultat
    if result["accepted"] and categories[result["predicted_class"]]== df_control['subject'].values[0]:
        decision=f"Utilisateur {df_control['subject'].values[0]} reconnu comme le nouvel auteur."
    else:
        decision=f"Vérification échouée. Auteur {df_control['subject'].values[0]} non reconnu. Accès refusé."

    print(decision)

    return {"decision": decision, "max_prob": result["max_prob"]} 

