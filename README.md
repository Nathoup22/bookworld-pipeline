# BookWorld — Pipeline de données

Projet final DataBird — Pipeline d'intégration de données multi-sources.

## Structure du projet

```
bookworld/
├── pipeline.py               # Pipeline principal
├── api.py                    # API REST Flask
├── queries.sql               # Requêtes SQL d'extraction
├── schema_final.sql          # Schéma de la base finale
├── sales_raw.csv             # Données brutes de ventes
├── bookworld_reference.sql   # Script de création de la base de référence
├── bookworld_reference.db    # Base SQLite de référence (générée)
├── bookworld_final.db        # Base SQLite finale (générée)
└── README.md
```

## Installation

```bash
pip install requests beautifulsoup4 flask
```

## Exécuter le pipeline

```bash
python pipeline.py
```

## Lancer l'API

```bash
python api.py
```

L'API démarre sur `http://127.0.0.1:5000`

## Authentification par token

```
Authorization: Bearer bookworld-secret-token-2024
```

Exemple curl :

```bash
curl http://127.0.0.1:5000/health
curl -H "Authorization: Bearer bookworld-secret-token-2024" http://127.0.0.1:5000/sales-by-country
```

## Endpoints

| Méthode | Route | Auth | Description |
|---------|-------|------|-------------|
| GET | `/health` | Non | Statut de l'API |
| GET | `/sales-by-country` | Oui | Ventes agrégées par pays |

## Note RGPD

Les colonnes `customer_first_name` et `customer_last_name` sont exclues de la base finale. Ces données personnelles ne sont pas nécessaires à l'usage analytique et ne sont pas conservées, conformément au principe de minimisation du RGPD.
