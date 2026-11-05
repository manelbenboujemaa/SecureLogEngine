"""Tests du lecteur de fichiers de logs en flux."""

import inspect
import tracemalloc
from itertools import islice
from pathlib import Path

import pytest

from log_engine.exceptions import (
    LogEngineError,
    SourceError,
    SourceNotFoundError,
)
from log_engine.ingestion.readers import read_lines

SAMPLES_DIR = Path(__file__).resolve().parents[2] / "data" / "samples"


# --- Lecture de base ------------------------------------------------------


def test_read_lines_returns_a_generator(tmp_path: Path) -> None:
    """read_lines est une fonction génératrice : l'appel ne lit rien."""
    source = tmp_path / "simple.log"
    source.write_text("ligne\n", encoding="utf-8")
    assert inspect.isgenerator(read_lines(source))


def test_read_lines_yields_numbered_lines_without_newline(
    tmp_path: Path,
) -> None:
    """Chaque ligne est un tuple (numéro, texte) sans saut de ligne."""
    source = tmp_path / "simple.log"
    source.write_text("premiere\ndeuxieme\ntroisieme\n", encoding="utf-8")
    assert list(read_lines(source)) == [
        (1, "premiere"),
        (2, "deuxieme"),
        (3, "troisieme"),
    ]


def test_read_lines_keeps_empty_lines(tmp_path: Path) -> None:
    """Les lignes vides sont conservées (filtrées plus tard)."""
    source = tmp_path / "trous.log"
    source.write_text("a\n\nb\n", encoding="utf-8")
    assert list(read_lines(source)) == [(1, "a"), (2, ""), (3, "b")]


def test_read_lines_handles_last_line_without_newline(tmp_path: Path) -> None:
    """La dernière ligne est lue même sans saut de ligne final."""
    source = tmp_path / "fin.log"
    source.write_text("a\nb", encoding="utf-8")
    assert list(read_lines(source)) == [(1, "a"), (2, "b")]


def test_read_lines_on_empty_file_yields_nothing(tmp_path: Path) -> None:
    """Un fichier vide ne produit aucune ligne et ne plante pas."""
    source = tmp_path / "vide.log"
    source.touch()
    assert list(read_lines(source)) == []


def test_read_lines_replaces_invalid_bytes(tmp_path: Path) -> None:
    """Un octet non UTF-8 est remplacé par � sans arrêter la lecture."""
    source = tmp_path / "corrompu.log"
    source.write_bytes(b"avant\nmauvais \xff octet\napres\n")
    lines = [text for _, text in read_lines(source)]
    assert lines == ["avant", "mauvais � octet", "apres"]


def test_read_lines_accepts_str_path(tmp_path: Path) -> None:
    """Le chemin peut être une simple chaîne de caractères."""
    source = tmp_path / "chaine.log"
    source.write_text("ok\n", encoding="utf-8")
    assert list(read_lines(str(source))) == [(1, "ok")]


# --- Lecture progressive --------------------------------------------------


def test_read_lines_stops_early_without_reading_everything(
    tmp_path: Path,
) -> None:
    """On peut ne consommer que le début d'un gros fichier."""
    source = tmp_path / "gros.log"
    source.write_text(
        "".join(f"ligne {i}\n" for i in range(1, 100_001)),
        encoding="utf-8",
    )
    first_three = list(islice(read_lines(source), 3))
    assert first_three == [(1, "ligne 1"), (2, "ligne 2"), (3, "ligne 3")]


def test_read_lines_memory_stays_constant(tmp_path: Path) -> None:
    """Parcourir un fichier de ~5 Mo n'occupe qu'une infime mémoire."""
    source = tmp_path / "volumineux.log"
    with source.open("w", encoding="utf-8") as file:
        for i in range(100_000):
            file.write(f"2026-11-04T08:00:00Z | INFO | ligne numero {i}\n")
    file_size = source.stat().st_size

    tracemalloc.start()
    count = 0
    for _ in read_lines(source):
        count += 1
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    assert count == 100_000
    # Le pic mémoire reste inférieur à 5 % de la taille du fichier.
    assert peak < file_size * 0.05


# --- Fichiers inexistants ou illisibles -----------------------------------


def test_missing_file_raises_source_not_found(tmp_path: Path) -> None:
    """Un fichier absent lève SourceNotFoundError avec un message clair."""
    missing = tmp_path / "absent.log"
    with pytest.raises(SourceNotFoundError, match="Source introuvable"):
        list(read_lines(missing))


def test_missing_file_error_is_raised_at_first_iteration(
    tmp_path: Path,
) -> None:
    """L'erreur n'apparaît qu'à la première itération (paresse)."""
    lines = read_lines(tmp_path / "absent.log")  # Aucune erreur ici
    with pytest.raises(SourceNotFoundError):
        next(lines)


def test_missing_file_error_keeps_path_and_cause(tmp_path: Path) -> None:
    """L'exception conserve le chemin fautif et l'erreur d'origine."""
    missing = tmp_path / "absent.log"
    with pytest.raises(SourceNotFoundError) as error_info:
        list(read_lines(missing))
    assert error_info.value.path == missing
    assert isinstance(error_info.value.__cause__, FileNotFoundError)


def test_directory_raises_source_error(tmp_path: Path) -> None:
    """Un dossier passé à la place d'un fichier lève SourceError."""
    with pytest.raises(SourceError, match="Source illisible"):
        list(read_lines(tmp_path))


def test_source_errors_share_a_common_base() -> None:
    """Toutes les erreurs métier peuvent être interceptées ensemble."""
    assert issubclass(SourceNotFoundError, SourceError)
    assert issubclass(SourceError, LogEngineError)


# --- Plusieurs fichiers ---------------------------------------------------


@pytest.mark.parametrize(
    ("file_name", "expected_lines"),
    [
        ("auth.log", 24),
        ("app_events.jsonl", 14),
        ("connections.csv", 17),
        ("blacklist.txt", 6),
    ],
)
def test_read_lines_on_each_sample_file(
    file_name: str, expected_lines: int
) -> None:
    """Chaque fichier d'exemple est lu en entier, numéroté à partir de 1."""
    lines = list(read_lines(SAMPLES_DIR / file_name))
    assert len(lines) == expected_lines
    assert lines[0][0] == 1
    assert lines[-1][0] == expected_lines


def test_read_lines_on_several_files_one_after_another() -> None:
    """Plusieurs fichiers se lisent successivement, chacun numéroté à part."""
    names = ("auth.log", "app_events.jsonl", "connections.csv")
    totals = {}
    for name in names:
        count = 0
        for number, _ in read_lines(SAMPLES_DIR / name):
            count += 1
            assert number == count  # Numérotation propre à chaque fichier
        totals[name] = count
    assert sum(totals.values()) == 24 + 14 + 17
