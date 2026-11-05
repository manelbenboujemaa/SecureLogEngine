"""Tests de la lecture de fichiers avec read_lines."""

import inspect
from pathlib import Path

import pytest

from log_engine.exceptions import LogEngineError, SourceNotFoundError
from log_engine.ingestion import readers
from log_engine.ingestion.readers import read_lines, read_source, read_sources

SAMPLES_DIR = Path(__file__).parent.parent.parent / "data" / "samples"


def create_file(folder, content):
    """Petite fonction d'aide : crée un fichier test.log avec ce contenu."""
    path = folder / "test.log"
    path.write_text(content, encoding="utf-8")
    return path


def test_read_lines_is_a_generator(tmp_path):
    """read_lines renvoie un générateur, pas une liste."""
    path = create_file(tmp_path, "a\n")
    assert inspect.isgenerator(read_lines(path))


def test_lines_are_numbered_without_newline(tmp_path):
    """Chaque ligne est un tuple (numéro, texte sans saut de ligne)."""
    path = create_file(tmp_path, "un\ndeux\ntrois\n")
    assert list(read_lines(path)) == [(1, "un"), (2, "deux"), (3, "trois")]


def test_empty_lines_are_kept(tmp_path):
    """Les lignes vides sont gardées (elles seront filtrées plus tard)."""
    path = create_file(tmp_path, "a\n\nb\n")
    assert list(read_lines(path)) == [(1, "a"), (2, ""), (3, "b")]


def test_empty_file(tmp_path):
    """Un fichier vide ne produit aucune ligne."""
    path = create_file(tmp_path, "")
    assert list(read_lines(path)) == []


def test_bad_character_does_not_crash(tmp_path):
    """Un octet illisible est remplacé par � au lieu de planter."""
    path = tmp_path / "bad.log"
    path.write_bytes(b"ok\nmauvais \xff octet\n")
    assert list(read_lines(path)) == [(1, "ok"), (2, "mauvais � octet")]


def test_next_gives_one_line_at_a_time(tmp_path):
    """next() demande la ligne suivante au générateur."""
    path = create_file(tmp_path, "a\nb\n")
    lines = read_lines(path)
    assert next(lines) == (1, "a")
    assert next(lines) == (2, "b")


def test_stop_iteration_at_the_end(tmp_path):
    """Quand il n'y a plus de ligne, next() lève StopIteration."""
    path = create_file(tmp_path, "seule\n")
    lines = read_lines(path)
    next(lines)
    with pytest.raises(StopIteration):
        next(lines)


def test_generator_can_be_used_only_once(tmp_path):
    """Un générateur ne se relit pas : le deuxième parcours est vide."""
    path = create_file(tmp_path, "a\nb\n")
    lines = read_lines(path)
    assert len(list(lines)) == 2
    assert list(lines) == []


def test_missing_file_raises_error(tmp_path):
    """Un fichier absent lève SourceNotFoundError avec un message clair."""
    with pytest.raises(SourceNotFoundError, match="Source introuvable"):
        list(read_lines(tmp_path / "absent.log"))


def test_error_only_at_first_next(tmp_path):
    """Le générateur ne fait rien tant qu'on ne lui demande pas de ligne."""
    lines = read_lines(tmp_path / "absent.log")
    with pytest.raises(SourceNotFoundError):
        next(lines)


def test_error_can_be_caught_with_base_class(tmp_path):
    """SourceNotFoundError peut être interceptée avec LogEngineError."""
    with pytest.raises(LogEngineError):
        list(read_lines(tmp_path / "absent.log"))


@pytest.mark.parametrize(
    "file_name, expected",
    [
        ("auth.log", 24),
        ("app_events.jsonl", 14),
        ("connections.csv", 17),
        ("blacklist.txt", 6),
    ],
)
def test_each_sample_file(file_name, expected):
    """Chaque fichier d'exemple est lu en entier."""
    lines = list(read_lines(SAMPLES_DIR / file_name))
    assert len(lines) == expected
    assert lines[0][0] == 1


def test_read_source_adds_file_name(tmp_path):
    """Chaque ligne est accompagnée du nom de son fichier."""
    path = create_file(tmp_path, "a\nb\n")
    assert list(read_source(path)) == [
        ("test.log", 1, "a"),
        ("test.log", 2, "b"),
    ]


def test_read_sources_is_a_generator():
    """read_sources renvoie un générateur."""
    assert inspect.isgenerator(read_sources([]))


def test_read_sources_chains_files_in_order(tmp_path):
    """Les fichiers sont lus l'un après l'autre, dans l'ordre de la liste."""
    first = tmp_path / "un.log"
    first.write_text("a\nb\n", encoding="utf-8")
    second = tmp_path / "deux.log"
    second.write_text("c\n", encoding="utf-8")
    assert list(read_sources([first, second])) == [
        ("un.log", 1, "a"),
        ("un.log", 2, "b"),
        ("deux.log", 1, "c"),
    ]


def test_read_sources_on_sample_files():
    """Les trois fichiers d'exemple forment un seul flux de lignes."""
    paths = [
        SAMPLES_DIR / "auth.log",
        SAMPLES_DIR / "app_events.jsonl",
        SAMPLES_DIR / "connections.csv",
    ]
    lines = list(read_sources(paths))
    assert len(lines) == 24 + 14 + 17
    assert lines[0][0] == "auth.log"
    assert lines[-1][0] == "connections.csv"


def test_read_sources_with_empty_list():
    """Une liste vide ne produit aucune ligne."""
    assert list(read_sources([])) == []


def test_missing_file_is_skipped_with_warning(tmp_path, caplog):
    """Un fichier absent est signalé puis ignoré, les autres sont lus."""
    path = create_file(tmp_path, "a\n")
    lines = list(read_sources([tmp_path / "absent.log", path]))
    assert lines == [("test.log", 1, "a")]
    assert "Source ignorée" in caplog.text
    assert "absent.log" in caplog.text


def test_unreadable_file_is_skipped(tmp_path, monkeypatch, caplog):
    """Un fichier sans droit de lecture est ignoré sans tout arrêter."""
    good = create_file(tmp_path, "ok\n")

    def fake_read_lines(path):
        if str(path).endswith("secret.log"):
            raise PermissionError("Permission refusée : secret.log")
        yield from real_read_lines(path)

    real_read_lines = readers.read_lines
    monkeypatch.setattr(readers, "read_lines", fake_read_lines)
    lines = list(read_sources([tmp_path / "secret.log", good]))
    assert lines == [("test.log", 1, "ok")]
    assert "Permission refusée" in caplog.text


def test_second_file_is_opened_only_when_needed(tmp_path, caplog):
    """Le fichier suivant n'est ouvert qu'une fois le premier terminé."""
    path = create_file(tmp_path, "a\n")
    lines = read_sources([path, tmp_path / "absent.log"])
    assert next(lines) == ("test.log", 1, "a")
    assert caplog.text == ""
    assert list(lines) == []
    assert "absent.log" in caplog.text
