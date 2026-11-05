"""Interface en ligne de commande de Secure Log Engine."""

import argparse
from collections.abc import Sequence

from log_engine import __app_name__, __version__


def build_parser() -> argparse.ArgumentParser:
    """Construit l'analyseur d'arguments de la CLI."""
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
    """Point d'entrée de la CLI."""
    parser = build_parser()
    parser.parse_args(argv)
    parser.print_help()
    return 0
