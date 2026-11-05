# Secure Log Engine

Moteur en ligne de commande d'ingestion, de filtrage, de transformation et
d'analyse de logs de sécurité, conçu pour traiter des fichiers volumineux
**en flux**, sans jamais les charger intégralement en mémoire.

> Projet final ING3 — *Engine de traitement et d'analyse de flux de données
> sécurisé en temps réel* — Python 3.10+.

## État d'avancement

| Étape | Contenu | Statut |
|---|---|---|
| 1 | Structure du projet, environnement virtuel, outillage | ✅ Terminée |
| 2 | Modèles de données et jeux d'échantillons | ✅ Terminée |
| 3 | Ingestion en flux (`yield` / `yield from`) | 🔄 En cours |
| 4 | Parsing et routage structurel (`match-case`) | ⏳ À venir |
| 5 | Pipeline fonctionnel (`map` / `filter` / `lambda`) | ⏳ À venir |
| 6 | Agrégation (`set`, `frozenset`, `defaultdict`) | ⏳ À venir |
| 7 | Détection de force brute | ⏳ À venir |
| 8 | Moteur de règles (`*args` / `**kwargs`) | ⏳ À venir |
| 9 | Audit d'introspection (`globals()` / `locals()`) | ⏳ À venir |
| 10 | CLI complète et rapports | ⏳ À venir |
| 11 | Tests d'intégration et de mémoire | ⏳ À venir |
| 12 | Documentation et rapport | ⏳ À venir |

## Prérequis

- Python **3.10 ou supérieur** (`match-case` et annotations `X | Y`)
- Git
- Testé sous Windows 10/11 (PowerShell) ; compatible Linux et macOS

## Installation (Windows, PowerShell)

```powershell
git clone <url-du-depot>
cd SecureLogEngine

# Création et activation de l'environnement virtuel
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1

# Installation des dépendances
python -m pip install --upgrade pip
pip install -r requirements.txt
```

> Si PowerShell refuse d'exécuter `Activate.ps1`, autorisez les scripts pour
> la session courante uniquement :
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

Sous Linux / macOS : `python3 -m venv .venv` puis `source .venv/bin/activate`.

## Utilisation

```powershell
python main.py --help
python main.py --version
```

Démonstration de la lecture en flux (mémoire d'un générateur vs chargement
complet) :

```powershell
python -m scripts.memory_demo                 # Fichier généré de 200 000 lignes
python -m scripts.memory_demo --lines 500000  # Taille personnalisée
```

Les commandes d'analyse seront documentées au fur et à mesure de leur
implémentation. Les formats de logs acceptés sont décrits dans
[`docs/log_formats.md`](docs/log_formats.md).

## Tests et qualité

```powershell
python -m pytest                                  # Lance la suite de tests
python -m pytest --cov --cov-report=term-missing  # Avec mesure de couverture
python -m ruff check .                            # Vérification PEP 8
python -m ruff format --check .                   # Vérification du formatage
```

> On passe par `python -m` plutôt que d'appeler directement `pytest.exe` :
> certaines configurations de Windows bloquent ces exécutables non signés.

## Arborescence

```
secure-log-engine/
├── main.py              # Point d'entrée : délègue à log_engine.cli
├── requirements.txt     # Dépendances figées (pip freeze)
├── pyproject.toml       # Configuration de pytest, coverage et ruff
├── log_engine/          # Package principal
│   ├── cli.py           # Interface en ligne de commande
│   ├── ingestion/       # Module 1 : lecture en flux
│   ├── parsing/         # Modules 1-2 : parsing et routage match-case
│   ├── pipeline/        # Module 2 : transformations fonctionnelles
│   ├── analysis/        # Module 3 : agrégation et force brute
│   ├── security/        # Module 4 : moteur de règles
│   ├── audit/           # Module 4 : introspection
│   └── reporting/       # Rapports console et JSON
├── docs/                # Spécifications (formats de logs)
├── scripts/             # Outils annexes (génération de données)
├── data/
│   ├── samples/         # Jeu de démonstration versionné
│   └── generated/       # Gros fichiers générés (ignorés par Git)
├── tests/               # Tests unitaires et d'intégration
├── notebooks/           # Rapport et démonstration graphique
└── reports/             # Sorties d'exécution (ignorées par Git)
```

## Dépendances

Le moteur n'utilise **que la bibliothèque standard**. Les dépendances listées
dans `requirements.txt` servent exclusivement au développement :

| Paquet | Rôle |
|---|---|
| `pytest` | Exécution des tests automatisés |
| `pytest-cov` | Mesure de la couverture de code |
| `ruff` | Vérification de la PEP 8 et du formatage |

Les autres lignes du fichier sont leurs dépendances transitives, figées par
`pip freeze`.

## Auteurs

Projet réalisé en trinôme (TAGNE CHIBY Ellios, BENBOUJEMAA Manel, SABITY Brahim).
