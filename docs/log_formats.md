# Spécification des formats de logs

Ce document définit le **contrat de données** de Secure Log Engine : les
sources acceptées, les champs attendus et la forme de l'enregistrement
normalisé. Les constantes correspondantes sont définies dans
`log_engine/models.py`, qui fait référence en cas de divergence.

## 1. Vue d'ensemble

Le moteur accepte trois formats de sources. Chacun produit naturellement
un type Python différent, qui sera routé par `match-case` (Module 2) vers
un enregistrement normalisé unique.

| Source | Exemple de fichier | Type Python produit | Usage |
|---|---|---|---|
| Lignes texte délimitées | `auth.log` | `str` | Authentification système (SSH) |
| JSON Lines | `app_events.jsonl` | `dict` | Événements applicatifs (web) |
| CSV de connexions | `connections.csv` | `tuple` | Flux réseau (pare-feu) |

## 2. Niveaux de sévérité

| Niveau | Valeur | Signification |
|---|---|---|
| `INFO` | 20 | Fonctionnement normal (connexion réussie, requête 200) |
| `WARNING` | 30 | Anomalie isolée (mot de passe erroné, page introuvable) |
| `ERROR` | 40 | Échec ou refus significatif (accès interdit, erreur 500) |
| `CRITICAL` | 50 | Incident grave (élévation de privilèges, service tombé) |

Les valeurs sont celles du module standard `logging`. Les niveaux sont
ordonnés (`Severity.ERROR > Severity.WARNING`), ce qui permet de filtrer
par seuil minimal.

## 3. Champs de l'enregistrement normalisé (`LogRecord`)

| Champ | Type | Description |
|---|---|---|
| `timestamp` | `datetime` | Horodatage de l'événement, en UTC |
| `severity` | `Severity` | Niveau de sévérité |
| `connection` | `tuple[str, int, str]` | Métadonnées immuables `(IP, port, protocole)` |
| `user` | `str \| None` | Identifiant utilisateur, `None` si anonyme |
| `event` | `str` | Type d'événement (voir § 7) |
| `payload` | `dict \| str` | Détails : objet JSON ou chaîne brute |
| `source` | `str` | Nom du fichier d'origine (traçabilité) |

## 4. Format 1 : lignes texte délimitées

Six champs, dans un ordre fixe, séparés par ` | ` (espace, barre, espace) :

```
<timestamp> | <niveau> | <ip>:<port>/<protocole> | <utilisateur> | <événement> | <payload>
```

```
2026-11-04T08:12:01Z | WARNING | 203.0.113.45:41001/TCP | admin | AUTH_FAILURE | {"reason": "bad_password", "attempt": 1}
2026-11-04T08:00:00Z | INFO | 127.0.0.1:22/TCP | - | SERVICE_START | {"service": "sshd", "pid": 1021}
2026-11-04T08:45:21Z | WARNING | 10.0.0.15:50300/TCP | alice | AUTH_FAILURE | Password expired for user alice
```

- **Horodatage** : ISO 8601 en UTC, suffixe `Z`.
- **Utilisateur** : `-` signifie « aucun utilisateur » (événement système).
- **Payload** : un objet JSON si la ligne commence par `{`, sinon une
  chaîne brute conservée telle quelle.
- **Séparateur** : le payload est le dernier champ ; il peut lui-même
  contenir ` | `, la ligne n'est donc découpée qu'en six morceaux au maximum.

## 5. Format 2 : JSON Lines

Un objet JSON complet par ligne :

```json
{"timestamp": "2026-11-04T08:13:05Z", "level": "ERROR", "src_ip": "203.0.113.45", "src_port": 41020, "protocol": "TCP", "user": "admin", "event": "ACCESS_DENIED", "code": 403, "message": "GET /admin/users/export"}
```

- **Clés obligatoires** : `timestamp`, `level`, `src_ip`, `src_port`,
  `protocol`, `event`.
- **Clés optionnelles** : `user` (`null` si anonyme), `code`, `message`.
- Toutes les clés non obligatoires (hors `user`) forment le `payload`.

## 6. Format 3 : CSV de connexions réseau

Fichier CSV avec une ligne d'en-tête :

```
timestamp,src_ip,src_port,protocol,dst_port,action
2026-11-04T08:08:41Z,198.51.100.77,60101,TCP,22,REJECTED
```

- `action` vaut `ACCEPTED` ou `REJECTED`.
- Ce format ne contient pas de niveau ni d'utilisateur. La conversion
  prévue est : `ACCEPTED` → `INFO` / `CONNECTION_ACCEPTED`,
  `REJECTED` → `WARNING` / `CONNECTION_REJECTED`, utilisateur `None`.
- Le protocole `ICMP` n'a pas de notion de port : le port vaut `0`.

## 7. Vocabulaires

**Protocoles** : `TCP`, `UDP`, `ICMP`.

**Types d'événements connus** :

| Catégorie | Événements |
|---|---|
| Service | `SERVICE_START`, `SERVICE_STOP`, `SERVICE_FAILURE` |
| Authentification | `AUTH_SUCCESS`, `AUTH_FAILURE` |
| Autorisation | `ACCESS_DENIED`, `PRIVILEGE_ESCALATION` |
| Administration | `CONFIG_CHANGE` |
| Web | `HTTP_REQUEST`, `HTTP_ERROR` |
| Réseau | `CONNECTION_ACCEPTED`, `CONNECTION_REJECTED` |

Un événement inconnu n'est pas une erreur de format : il est conservé
et pourra être signalé lors de l'analyse.

## 8. Liste noire d'adresses IP

`blacklist.txt` contient une adresse IP par ligne. Les lignes vides et
celles commençant par `#` sont ignorées. Elle sera chargée sous forme de
`frozenset` (Module 3).

## 9. Jeu de démonstration (`data/samples/`)

Les adresses externes appartiennent aux plages réservées à la
documentation (RFC 5737 : `192.0.2.0/24`, `198.51.100.0/24`,
`203.0.113.0/24`) ; elles ne désignent aucune machine réelle.

Scénarios volontairement présents :

| Scénario | Où | Ce qui doit être détecté plus tard |
|---|---|---|
| Force brute réussie | `auth.log` : `203.0.113.45`, 6 échecs puis succès et `sudo` | Alerte force brute + élévation de privilèges |
| Tentatives sous le seuil | `auth.log` : `198.51.100.23`, 3 échecs | Aucune alerte force brute |
| Échecs entrelacés | `auth.log` : une connexion de `dave` au milieu de l'attaque | La détection doit raisonner par IP |
| Scan de ports | `connections.csv` : `198.51.100.77` | IP active **et** blacklistée |
| Reconnaissance web | `app_events.jsonl` : `198.51.100.77`, erreurs 404 | Corrélation multi-sources |
| Attaquant non blacklisté | `203.0.113.45` absente de `blacklist.txt` | Différence d'ensembles |

Lignes **volontairement non conformes**, pour tester la robustesse :

| Fichier | Ligne non conforme |
|---|---|
| `auth.log` | une ligne vide |
| `auth.log` | une ligne noyau non structurée (`kernel: ...`) |
| `auth.log` | une ligne tronquée à trois champs |
| `app_events.jsonl` | une ligne vide |
| `app_events.jsonl` | un objet JSON tronqué (invalide) |
| `app_events.jsonl` | un objet valide auquel il manque la clé `level` |
| `connections.csv` | un port non numérique (`notaport`) |

## 10. Points d'attention pour l'implémentation

- **Python 3.10 et le suffixe `Z`** : `datetime.fromisoformat()` n'accepte
  le suffixe `Z` qu'à partir de Python 3.11. Le parseur devra le remplacer
  par `+00:00` pour rester compatible 3.10.
- **Encodage** : les fichiers sont en UTF-8 et doivent être ouverts avec
  `encoding="utf-8"` explicite (l'encodage par défaut de Windows diffère).
