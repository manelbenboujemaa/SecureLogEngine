# SecureLogEngine

Projet de Programmation en Python - ING3, ECE Paris.

Outil en ligne de commande qui lit et analyse des fichiers de logs de
sécurité. Les fichiers sont traités ligne par ligne, sans être chargés
entièrement en mémoire, pour pouvoir gérer des fichiers volumineux.

Équipe : TAGNE CHIBY Ellios, BENBOUJEMAA Manel, SABITY Brahim.

## Installation

Il faut Python 3.10 ou plus récent.

```powershell
git clone https://github.com/manelbenboujemaa/SecureLogEngine.git
cd SecureLogEngine
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Si PowerShell bloque `Activate.ps1`, lancer une fois :

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Utilisation

```powershell
python main.py --help
python -m scripts.memory_demo
```

`memory_demo` compare la mémoire utilisée pour lire un gros fichier avec
un générateur, avec une liste et avec `readlines()`.

## Tests

```powershell
python -m pytest
python -m ruff check .
```

On utilise `python -m pytest` plutôt que `pytest` car Windows bloque
parfois `pytest.exe`.

## Organisation du projet

```
main.py              point d'entrée
log_engine/          code du moteur
  ingestion/         lecture des fichiers
  parsing/           découpage des lignes
  pipeline/          filtrage et transformation
  analysis/          statistiques et détection de force brute
  security/          règles de sécurité
  audit/             audit avec globals() / locals()
  reporting/         rapports
data/samples/        fichiers de logs d'exemple
docs/                description des formats de logs
scripts/             scripts annexes
tests/               tests pytest
```

Les formats de logs acceptés sont décrits dans `docs/log_formats.md`.

## Avancement

- [x] Structure du projet et environnement
- [x] Formats de logs et données d'exemple
- [x] Lecture des fichiers avec un générateur
- [x] Lecture de plusieurs fichiers (`yield from`)
- [ ] Parsing et routage (`match-case`)
- [ ] Filtrage et transformation (`map`, `filter`, `lambda`)
- [ ] Statistiques (`set`, `frozenset`, `defaultdict`)
- [ ] Détection de force brute
- [ ] Moteur de règles (`*args`, `**kwargs`)
- [ ] Audit (`globals()`, `locals()`)
- [ ] Interface en ligne de commande complète
- [ ] Rapport final
