"""Point d'entrée principal de Secure Log Engine.

Ce fichier reste volontairement minimal : il vérifie la version de Python
puis délègue toute la logique à ``log_engine.cli``. Ainsi, le code métier
reste dans le package et peut être testé indépendamment.

Usage :
    python main.py --help
"""

import sys

MINIMUM_PYTHON: tuple[int, int] = (3, 10)


def check_python_version() -> None:
    """Interrompt le programme si la version de Python est insuffisante.

    Le projet utilise ``match-case`` et la syntaxe ``X | Y`` des annotations,
    disponibles uniquement à partir de Python 3.10.
    """
    if sys.version_info < MINIMUM_PYTHON:
        required = ".".join(map(str, MINIMUM_PYTHON))
        current = ".".join(map(str, sys.version_info[:3]))
        sys.exit(
            f"Erreur : Python {required} ou supérieur est requis "
            f"(version détectée : {current})."
        )


if __name__ == "__main__":
    check_python_version()

    from log_engine.cli import main

    sys.exit(main())
