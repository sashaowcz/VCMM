# MTBLANC-VCMM V10 — Freeride Snow

Application Streamlit pour consulter les prévisions de neige, de pluie, l'altitude et le vent autour de Verbier, des 4 Vallées, de Chamonix et de Megève.

## Déploiement sur Streamlit Community Cloud

1. Décompressez le ZIP.
2. Sur GitHub, dans le dépôt existant, remplacez `app.py`, `requirements.txt` et `.streamlit/config.toml` à la racine du dépôt.
3. Validez avec **Commit changes**.
4. Dans Streamlit Cloud, l'application existante se redéploie automatiquement. Si nécessaire, redémarrez-la depuis **Manage app**.

## Fonctionnalités

- Accueil : classement des chutes de neige prévues sur 12, 24, 48 ou 72 h, par station.
- Carte topographique : points colorés neige (bleu), pluie (rouge), absence de précipitation notable (vert), heure cible réglable. Radar d'observation optionnel.
- Détail : prévisions à altitude ajustable par pas de 50 m, heures de neige et de pluie, rafales.
- Webcams : accès aux sites des stations et aux bulletins officiels.

## Limites importantes

- **Les valeurs de neige sont des prévisions de chutes de neige, pas des mesures de poudreuse au sol.**
- Les points sont des prévisions numériques, et non une carte spatiale continue de phase de précipitation.
- L'altitude à 50 m est une correction du modèle et n'implique pas une précision à 50 m.
- Le radar RainViewer est une couche d'observations de précipitations, sans distinction directe pluie/neige.
- Les données sont mises en cache 15 minutes pour limiter les appels ; elles ne sont pas des observations en direct.
- Les bulletins d'avalanches officiels restent indispensables.

Sources : https://open-meteo.com/en/docs ; https://opendatadocs.meteoswiss.ch/


## V11 : Pisteurs & secours

L’onglet **Pisteurs & secours** affiche un briefing météorologique par secteur, point, altitude (pas de 50 m) et fenêtre de 6 à 48 h : rafales, neige, pluie, température, isotherme et tableau horaire exportable. Les messages de vigilance reposent sur des seuils indicatifs non officiels et ne sont pas des alertes de sécurité. Des liens directs mènent aux bulletins officiels.

Déploiement : remplacer `app.py`, `requirements.txt` et `.streamlit/config.toml` dans le dépôt GitHub existant. Streamlit Cloud redéploie après le commit.


## V12 — correction du contraste
Les alertes, boutons de liens et sélecteurs de période sont désormais stylisés avec un fond sombre et des textes blancs. Les options actives sont vert fluo avec texte noir. Aucun changement de source météo.
