# MTBLANC-VCMM V9 — Streamlit

Application météo alpine, refonte mobile.

## Installation sur GitHub / Streamlit Cloud
1. Décompresser le ZIP.
2. Dans le dépôt GitHub déjà connecté à Streamlit, remplacer `app.py`, `requirements.txt` et `.streamlit/config.toml` par les fichiers du dossier.
3. Valider les changements avec **Commit changes**.
4. Attendre le redéploiement sur Streamlit Cloud. En cas d'erreur, ouvrir **Manage app > Logs**.

Pour un nouveau déploiement : https://share.streamlit.io/ ; choisir le dépôt GitHub, branche `main`, fichier principal `app.py`.

## Sources et limites
- Prévisions : Open-Meteo, API forecast. Rafraîchissement du cache et de l'interface toutes les 60 secondes pour les sections principales ; cela ne garantit pas des données produites toutes les minutes.
- Radar : RainViewer, historique limité à ce que fournit l'API gratuite. Ce n'est pas une archive garantie de 48 h et ce ne sont pas des prévisions radar futures.
- Altitude par 50 m : ajustement de modèle, pas une observation mesurée à cette précision.
- Carte : OpenStreetMap / Leaflet via Folium. La couche radar a une résolution native limitée.
- Sécurité : application non certifiée pour le dispatch, l'alerte ou les décisions de secours.

## Démarrage local
`pip install -r requirements.txt`
`streamlit run app.py`
