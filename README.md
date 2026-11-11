# MTBLANC-VCMM V8 — Streamlit

Application météo alpine pour Verbier, 4 Vallées, Chamonix, Megève et corridor.

## Déployer sur Streamlit Community Cloud
1. Décompressez le ZIP.
2. Dans votre dépôt GitHub existant, remplacez `app.py`, `requirements.txt` et `.streamlit/config.toml` par les fichiers du projet. Conservez leur arborescence.
3. Validez avec **Commit changes**.
4. Streamlit Community Cloud redéploie l’application automatiquement. Si nécessaire, ouvrez **Manage app → Reboot**.

## Nouveauté V8
Onglet **COMPARAISON MODÈLES** : récupération indépendante des modèles ICON-CH1, ICON-CH2, AROME HD et ECMWF via Open-Meteo, graphiques et médiane/fourchette de prévision. Les modèles indisponibles sont signalés, jamais remplacés par des valeurs inventées.

## Précautions
Les valeurs tous les 50 m sont des estimations ajustées à l'altitude, pas des observations tous les 50 m. Les radars RainViewer ne garantissent pas 48 h d'historique. Les données ne remplacent pas les bulletins officiels ni l'expertise terrain. Vérifiez les licences et conditions d'utilisation des fournisseurs pour un usage commercial.
