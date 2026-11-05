"""Exceptions propres à Secure Log Engine.

Toutes les exceptions du projet héritent de ``LogEngineError``. L'appelant
(la CLI, par exemple) peut donc intercepter n'importe quelle erreur métier
avec un seul ``except LogEngineError``, sans risquer de masquer un vrai
bug Python (``TypeError``, ``KeyError``...).

Hiérarchie actuelle ::

    LogEngineError
    └── SourceError              # Source impossible à lire
        └── SourceNotFoundError  # Source inexistante
"""

from __future__ import annotations

from pathlib import Path


class LogEngineError(Exception):
    """Classe de base de toutes les erreurs métier du moteur."""


class SourceError(LogEngineError):
    """Une source de logs ne peut pas être lue (droits, dossier...)."""

    def __init__(self, path: Path, reason: str) -> None:
        """Construit l'erreur à partir du chemin fautif et de la cause.

        Args:
            path: Chemin de la source concernée.
            reason: Explication lisible par un humain.
        """
        self.path = path
        super().__init__(f"{reason} : {path}")


class SourceNotFoundError(SourceError):
    """La source de logs demandée n'existe pas."""

    def __init__(self, path: Path) -> None:
        """Construit l'erreur à partir du chemin introuvable.

        Args:
            path: Chemin de la source introuvable.
        """
        super().__init__(path, "Source introuvable")
