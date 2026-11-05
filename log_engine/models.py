"""Modèles de données et contrat des formats de logs.

Ce module est la référence unique du projet pour :

- les niveaux de sévérité (``Severity``) ;
- la forme des métadonnées de connexion (``ConnectionMeta``) ;
- la forme de l'enregistrement normalisé (``LogRecord``) ;
- les constantes décrivant les trois formats de sources acceptés.

La spécification détaillée, avec exemples, se trouve dans
``docs/log_formats.md``.
"""

from __future__ import annotations

from datetime import datetime
from enum import IntEnum
from typing import Any, TypeAlias, TypedDict


class Severity(IntEnum):
    """Niveaux de sévérité d'un événement, du moins au plus grave.

    Les valeurs numériques reprennent celles du module standard ``logging``
    (``logging.INFO == 20``, etc.). Comme ``IntEnum`` hérite de ``int``,
    les niveaux sont **ordonnés** : ``Severity.ERROR > Severity.WARNING``,
    ce qui permet de filtrer les événements par seuil minimal.
    """

    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50

    def __str__(self) -> str:
        """Renvoie le nom du niveau (ex. ``"ERROR"``).

        Le comportement par défaut de ``str()`` sur un ``IntEnum`` a changé
        entre Python 3.10 (``"Severity.ERROR"``) et 3.11 (``"40"``) : on le
        fixe explicitement pour obtenir des rapports identiques partout.
        """
        return self.name


# Métadonnées fixes d'une connexion : (adresse IP, port, protocole).
# Un tuple est immuable : une fois l'événement parsé, son origine réseau
# ne peut plus être modifiée par erreur dans la suite du pipeline.
ConnectionMeta: TypeAlias = tuple[str, int, str]


class LogRecord(TypedDict):
    """Enregistrement normalisé produit à partir de n'importe quelle source.

    À l'exécution, c'est un ``dict`` Python ordinaire (exigence du cahier
    des charges) ; ``TypedDict`` sert uniquement à documenter et à faire
    vérifier par l'éditeur le nom et le type de chaque champ.
    """

    timestamp: datetime
    severity: Severity
    connection: ConnectionMeta
    user: str | None
    event: str
    payload: dict[str, Any] | str
    source: str


# --- Format 1 : lignes texte délimitées -----------------------------------

TEXT_SEPARATOR: str = " | "
TEXT_FIELDS: tuple[str, ...] = (
    "timestamp",
    "severity",
    "connection",
    "user",
    "event",
    "payload",
)
ANONYMOUS_USER: str = "-"

# --- Format 2 : JSON Lines (un objet JSON par ligne) ----------------------

JSONL_REQUIRED_KEYS: frozenset[str] = frozenset(
    {"timestamp", "level", "src_ip", "src_port", "protocol", "event"}
)

# --- Format 3 : CSV de connexions réseau ----------------------------------

CSV_COLUMNS: tuple[str, ...] = (
    "timestamp",
    "src_ip",
    "src_port",
    "protocol",
    "dst_port",
    "action",
)

# --- Vocabulaires communs aux trois formats -------------------------------

SUPPORTED_PROTOCOLS: frozenset[str] = frozenset({"TCP", "UDP", "ICMP"})

KNOWN_EVENTS: frozenset[str] = frozenset(
    {
        "SERVICE_START",
        "SERVICE_STOP",
        "SERVICE_FAILURE",
        "AUTH_SUCCESS",
        "AUTH_FAILURE",
        "ACCESS_DENIED",
        "PRIVILEGE_ESCALATION",
        "CONFIG_CHANGE",
        "HTTP_REQUEST",
        "HTTP_ERROR",
        "CONNECTION_ACCEPTED",
        "CONNECTION_REJECTED",
    }
)
