"""Démonstration : consommation mémoire d'un générateur vs chargement complet.

Le script crée un fichier de logs temporaire (ou utilise un fichier fourni),
puis mesure avec ``tracemalloc`` le pic mémoire de trois façons de le lire :

1. parcourir ``read_lines`` ligne par ligne (générateur) ;
2. transformer ce générateur en liste avec ``list()`` (erreur fréquente) ;
3. charger tout le fichier avec ``read_text().splitlines()``.

Usage (depuis la racine du projet) ::

    python -m scripts.memory_demo
    python -m scripts.memory_demo --lines 500000
    python -m scripts.memory_demo --file data/samples/auth.log
"""

from __future__ import annotations

import argparse
import tempfile
import tracemalloc
from collections.abc import Callable, Sequence
from pathlib import Path

from log_engine.ingestion.readers import SOURCE_ENCODING, read_lines

DEFAULT_LINES: int = 200_000
# En dessous de ce rapport, l'écart n'est pas significatif.
MEANINGFUL_RATIO: float = 2.0
SAMPLE_LINE: str = (
    "2026-11-04T08:12:01Z | WARNING | 203.0.113.45:41001/TCP | admin "
    '| AUTH_FAILURE | {{"reason": "bad_password", "attempt": {n}}}\n'
)


def generate_log_file(path: Path, line_count: int) -> None:
    """Écrit un fichier de logs réaliste, ligne par ligne.

    L'écriture se fait elle aussi en flux : le fichier n'est jamais
    construit en mémoire avant d'être écrit.

    Args:
        path: Chemin du fichier à créer.
        line_count: Nombre de lignes à écrire.
    """
    with path.open("w", encoding=SOURCE_ENCODING) as file:
        for number in range(1, line_count + 1):
            file.write(SAMPLE_LINE.format(n=number))


def measure_peak(action: Callable[[], int]) -> tuple[int, int]:
    """Exécute ``action`` et mesure le pic de mémoire allouée par Python.

    Args:
        action: Fonction sans argument qui renvoie un nombre de lignes lues.

    Returns:
        Le couple ``(lignes_lues, pic_mémoire_en_octets)``.
    """
    tracemalloc.start()
    try:
        line_count = action()
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return line_count, peak


def format_size(size: float) -> str:
    """Convertit un nombre d'octets en texte lisible (ex. ``"9.8 Mo"``).

    Args:
        size: Taille en octets.

    Returns:
        La taille exprimée en o, Ko, Mo ou Go.
    """
    for unit in ("o", "Ko", "Mo"):
        if size < 1024:
            return (
                f"{size:.0f} {unit}" if unit == "o" else f"{size:.1f} {unit}"
            )
        size /= 1024
    return f"{size:.1f} Go"


def count_with_generator(path: Path) -> int:
    """Parcourt le fichier avec le générateur, sans rien conserver."""
    count = 0
    for _ in read_lines(path):
        count += 1
    return count


def count_with_list(path: Path) -> int:
    """Matérialise le générateur dans une liste (annule son intérêt)."""
    return len(list(read_lines(path)))


def count_with_full_load(path: Path) -> int:
    """Charge tout le fichier d'un coup en mémoire."""
    return len(path.read_text(encoding=SOURCE_ENCODING).splitlines())


# Les fonctions sont rangées dans un tuple comme n'importe quelle valeur :
# ce sont des objets de première classe.
METHODS: tuple[tuple[str, Callable[[Path], int]], ...] = (
    ("read_lines (générateur)", count_with_generator),
    ("list(read_lines(...))", count_with_list),
    ("read_text().splitlines()", count_with_full_load),
)


def run_demo(path: Path) -> list[tuple[str, int]]:
    """Mesure le pic mémoire de chaque méthode de lecture sur ``path``.

    Args:
        path: Fichier de logs à lire.

    Returns:
        Une liste de couples ``(nom_de_la_méthode, pic_en_octets)``.
    """
    results = []
    for name, method in METHODS:
        _, peak = measure_peak(lambda method=method: method(path))
        results.append((name, peak))
    return results


def print_report(path: Path, results: list[tuple[str, int]]) -> None:
    """Affiche le tableau comparatif des pics mémoire."""
    line_count = count_with_generator(path)
    size = format_size(path.stat().st_size)
    print(f"\nFichier : {size} ({line_count:,} lignes)".replace(",", " "))
    print(f"\n{'Méthode':<28}{'Pic mémoire':>14}")
    print("-" * 42)
    for name, peak in results:
        print(f"{name:<28}{format_size(peak):>14}")

    generator_peak = results[0][1]
    full_load_peak = results[-1][1]
    ratio = full_load_peak / generator_peak if generator_peak else 0.0
    if ratio >= MEANINGFUL_RATIO:
        print(f"\n-> Le générateur utilise {ratio:.0f} fois moins de mémoire.")
    else:
        # Sur un petit fichier, le tampon de lecture (~8 Ko) domine :
        # le gain du générateur n'apparaît qu'avec des fichiers volumineux.
        print(
            "\n-> Fichier trop petit pour observer une différence : "
            "le gain du générateur apparaît sur les gros fichiers."
        )


def build_parser() -> argparse.ArgumentParser:
    """Construit l'analyseur des arguments du script."""
    parser = argparse.ArgumentParser(
        description="Compare la mémoire utilisée par différentes lectures."
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument(
        "--lines",
        type=int,
        default=DEFAULT_LINES,
        help=f"lignes du fichier généré (défaut : {DEFAULT_LINES})",
    )
    source.add_argument(
        "--file",
        type=Path,
        help="mesurer un fichier existant au lieu d'en générer un",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Point d'entrée du script.

    Args:
        argv: Arguments de la ligne de commande (``None`` = ``sys.argv``).

    Returns:
        Le code de sortie (0 en cas de succès).
    """
    args = build_parser().parse_args(argv)
    if args.file is not None:
        print_report(args.file, run_demo(args.file))
        return 0

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "demo.log"
        print(f"Génération de {args.lines:,} lignes...".replace(",", " "))
        generate_log_file(path, args.lines)
        print_report(path, run_demo(path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
