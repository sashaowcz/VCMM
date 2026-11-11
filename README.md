# MTBLANC-VCMM — Streamlit V6

Météo montagne pour Verbier, les 4 Vallées, Chamonix, Megève et leurs environs. Application d'information et de préparation, **pas un outil de secours certifié**.

## Déploiement
1. Créer un dépôt GitHub public `MTBLANC-VCMM`.
2. Envoyer `app.py`, `requirements.txt` et le dossier `.streamlit` à la racine du dépôt.
3. Ouvrir https://share.streamlit.io, se connecter avec GitHub et choisir **Create app**.
4. Sélectionner le dépôt, la branche `main` et le fichier `app.py`, puis **Deploy**.

## Exécution locale
```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Sources et limites
- Prévisions Open-Meteo, altitude demandée à l'API. Résolution réelle du modèle beaucoup plus grossière que 50 m.
- Fond OpenTopoMap et Leaflet/Folium.
- Radar RainViewer : dernière image passée disponible, sous réserve de disponibilité.
- Webcams : liens vers les sites des stations, pas des flux vérifiés.
- Pas de système de dispatch, de suivi de personnes ou d'alertes certifiées.
