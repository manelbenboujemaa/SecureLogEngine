"""Lecture des fichiers de logs, ligne par ligne."""

import os
from collections.abc import Iterator
from pathlib import Path

from log_engine.exceptions import SourceNotFoundError


def read_lines(path: str | Path) -> Iterator[tuple[int, str]]:
    """Renvoie les lignes d'un fichier une par une (générateur)."""
    if not os.path.isfile(path):
        raise SourceNotFoundError(f"Source introuvable : {path}")

    with open(path, encoding="utf-8", errors="replace") as file:
        for number, line in enumerate(file, start=1):
            yield number, line.rstrip("\n")
