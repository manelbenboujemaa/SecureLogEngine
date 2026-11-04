"""Interface en ligne de commande de Secure Log Engine.

À ce stade du projet, la CLI ne fait qu'exposer l'aide et la version :
les sous-commandes d'analyse seront ajoutées au fur et à mesure que les
modules du pipeline seront implémentés.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from log_engine import __app_name__, __version__


def build_parser() -> argparse.ArgumentParser:
    """Construit l'analyseur d'arguments de la CLI.

    Returns:
        Un ``ArgumentParser`` configuré avec les options globales.
    """
    parser = argparse.ArgumentParser(
        prog=__app_name__,
        description=(
            "Moteur de traitement et d'analyse de flux de logs de sécurité."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="Affiche la version et quitte.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Point d'entrée de la CLI.

    Args:
        argv: Arguments de la ligne de commande (sans le nom du programme).
            ``None`` signifie que ``sys.argv[1:]`` est utilisé.

    Returns:
        Le code de sortie du programme (0 en cas de succès).
    """
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0
