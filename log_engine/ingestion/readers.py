"""Lecture des fichiers de logs, ligne par ligne."""

import logging
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


def read_source(path: str | Path) -> Iterator[tuple[str, int, str]]:
    """Renvoie les lignes d'un fichier avec le nom de ce fichier."""
    name = os.path.basename(path)
    for number, line in read_lines(path):
        yield name, number, line


def read_sources(paths: list[str | Path]) -> Iterator[tuple[str, int, str]]:
    """Enchaîne la lecture de plusieurs fichiers dans un seul flux."""
    for path in paths:
        try:
            yield from read_source(path)
        except (SourceNotFoundError, PermissionError) as error:
            logging.warning(f"Source ignorée : {error}")
