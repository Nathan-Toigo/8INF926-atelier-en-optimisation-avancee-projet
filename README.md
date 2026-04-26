# Atelier en optimisation avancée : interface utilisateur et modélisation

## Introduction

Ce projet présente une application web dédiée à l’optimisation de la répartition du débit entre cinq turbines hydroélectriques. L’objectif est de maximiser la puissance produite à partir d’un débit total disponible et d’une élévation amont donnée, en tenant compte des contraintes de débit maximal et de disponibilité de chaque turbine.

L’application combine trois éléments principaux :

- une interface web interactive pour saisir les contraintes et visualiser les résultats ;
- une API FastAPI qui expose les calculs d’optimisation ;
- un moteur de programmation dynamique qui calcule la répartition optimale des débits.

Le dossier `modelisations/` regroupe les notebooks et les résultats utilisés pour comparer et valider les approches de modélisation.

## Fonctionnalités

- Répartition optimale du débit entre cinq turbines.
- Activation ou désactivation individuelle de chaque turbine.
- Ajustement du débit maximal admissible pour chaque turbine.
- Calcul de la puissance totale et de la puissance par turbine.
- Visualisation de l’évolution des débits turbinés sur plusieurs itérations.

## Comment lancer l'application en local

### Option 1 : avec Docker Compose

Cette méthode lance l’application dans un environnement isolé avec toutes les dépendances nécessaires.

1. Construire et démarrer les conteneurs :
    ```bash
    docker-compose up --build
    ```
2. Ouvrir l’application dans le navigateur à l’adresse :
    ```
    http://localhost:8000
    ```
3. Arrêter l’application :
    ```bash
    docker-compose down
    ```

### Option 2 : avec Python

Cette option lance directement l’application depuis le dossier `app/`.

1. Se placer dans le dossier de l’application :
    ```bash
    cd app
    ```
2. Installer les dépendances :
    ```bash
    pip install -r requirements.txt
    ```
3. Démarrer le serveur :
    ```bash
    python main.py
    ```
4. Ouvrir l’application dans le navigateur à l’adresse :
    ```
    http://localhost:8000
    ```

### Remarques

- Le fichier de données `DataProjet2026.xlsx` est lu depuis le dossier `app/`, donc le lancement depuis ce répertoire est recommandé pour l’exécution locale en Python.
- L’interface principale se trouve dans `app/index.html` et est rendue par l’API au démarrage.

## Arborescence du projet

```text
.
├── app/
│   ├── algo_dp.py              # Modèle hydraulique et optimisation par programmation dynamique
│   ├── api.py                  # API FastAPI et routes /api/optimize et /api/iterations
│   ├── DataProjet2026.xlsx     # Données utilisées pour les itérations et la validation
│   ├── index.html              # Interface web principale
│   ├── main.py                 # Point d’entrée du serveur
│   ├── web_app.py              # Rendu HTML et injection du script client
│   ├── requirements.txt        # Dépendances Python
│   └── img/                    # Ressources d’images utilisées par l’interface
├── modelisations/
│   ├── comparaison_dp_nomad.ipynb
│   ├── projet1_partie2_dp_python.ipynb
│   ├── projet2_partie2_nomad_python.ipynb
│   ├── partie2_validation_100_resultats_nomad.csv
│   ├── partie2_validation_100_resultats_python.csv
│   ├── partie2_validation_100_summary_nomad.csv
│   ├── partie2_validation_100_summary_python.csv
│   └── DataProjet2026.xlsx
├── docker-compose.yaml         # Configuration Docker
├── Dockerfile                  # Configuration Docker
└── README.md
```

## Description technique

### Interface utilisateur

L’interface permet de paramétrer le débit total, l’élévation amont, l’algorithme de calcul et les contraintes propres à chaque turbine. Elle affiche ensuite la répartition optimale du débit, la chute nette et la puissance produite par turbine.

### API

Deux routes principales sont exposées :

- `POST /api/optimize` : calcule une solution optimale à partir des contraintes saisies ;
- `POST /api/iterations` : calcule plusieurs solutions sur un sous-ensemble de données afin d’alimenter les graphiques.

### Optimisation

Le cœur du calcul repose sur une programmation dynamique discrétisée avec un pas de débit de 5 m³/s. Le modèle hydraulique combine une estimation de la chute nette et une approximation polynomiale de la puissance de chaque turbine.

## Résultats et modélisation

Les notebooks présents dans `modelisations/` sont les dossiers ayant été utilisés pour la rédaction de l'article.

Si vous souhaitez reproduire ou prolonger les expériences, commencez par les notebooks `projet1_partie2_dp_python.ipynb` et `projet2_partie2_nomad_python.ipynb`, puis consultez les fichiers CSV de synthèse pour comparer les résultats.

