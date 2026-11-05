"""Lecture des fichiers de logs en flux, ligne par ligne.

Le cœur de ce module est ``read_lines``, une **fonction génératrice** :
au lieu de renvoyer la liste de toutes les lignes, elle les produit une
à une avec ``yield``. À tout instant, une seule ligne est en mémoire, quelle
que soit la taille du fichier (quelques Ko ou plusieurs Go).
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator
from pathlib import Path

from log_engine.exceptions import SourceError, SourceNotFoundError

logger = logging.getLogger(__name__)

# Chemin accepté : une chaîne ("data/auth.log") ou un objet Path.
StrPath = str | os.PathLike[str]

# Encodage imposé explicitement : sous Windows, l'encodage par défaut
# n'est pas UTF-8 (cp1252), ce qui fausserait la lecture des accents.
SOURCE_ENCODING: str = "utf-8"


def read_lines(path: StrPath) -> Iterator[tuple[int, str]]:
    """Produit les lignes d'un fichier une par une, sans le charger en entier.

    Chaque ligne est renvoyée sous la forme ``(numéro, texte)`` : le numéro
    commence à 1 et le texte est débarrassé de son saut de ligne final.
    Les lignes vides sont conservées ; elles seront filtrées plus tard dans
    le pipeline.

    Les caractères mal encodés sont remplacés par ``"\\ufffd"`` (�) au lieu
    d'interrompre la lecture : un octet corrompu ne doit pas empêcher
    l'analyse du reste d'un fichier volumineux.

    Attention : comme toute fonction génératrice, ``read_lines`` n'exécute
    rien au moment de l'appel. Le fichier n'est ouvert, et les erreurs ne
    sont levées, qu'à la **première itération**.

    Args:
        path: Chemin du fichier de logs à lire.

    Yields:
        Des tuples ``(numéro_de_ligne, texte_de_la_ligne)``.

    Raises:
        SourceNotFoundError: Si le fichier n'existe pas.
        SourceError: Si le chemin existe mais ne peut pas être lu
            (dossier, droits insuffisants...).
    """
    source = Path(path)
    try:
        file = source.open(encoding=SOURCE_ENCODING, errors="replace")
    except FileNotFoundError as error:
        raise SourceNotFoundError(source) from error
    except OSError as error:
        raise SourceError(source, "Source illisible") from error

    logger.debug("Ouverture de la source %s", source)
    # Le bloc ``with`` garantit la fermeture du fichier, que la lecture
    # aille jusqu'au bout, soit interrompue (break) ou échoue.
    number = 0  # Reste à 0 si le fichier est vide
    with file:
        for number, line in enumerate(file, start=1):
            yield number, line.rstrip("\n")
    logger.debug("Fin de lecture de %s (%d lignes)", source, number)
