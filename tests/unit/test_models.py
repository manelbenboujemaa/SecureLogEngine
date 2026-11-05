"""Tests des modèles de données et de la conformité du jeu d'échantillons."""

import csv
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import pytest

from log_engine.models import (
    CSV_COLUMNS,
    JSONL_REQUIRED_KEYS,
    KNOWN_EVENTS,
    SUPPORTED_PROTOCOLS,
    TEXT_FIELDS,
    TEXT_SEPARATOR,
    LogRecord,
    Severity,
)

SAMPLES_DIR = Path(__file__).resolve().parents[2] / "data" / "samples"


# --- Severity -------------------------------------------------------------


def test_severity_levels_are_ordered() -> None:
    """Les niveaux sont comparables du moins au plus grave."""
    assert (
        Severity.INFO < Severity.WARNING < Severity.ERROR < Severity.CRITICAL
    )


def test_severity_values_match_logging_module() -> None:
    """Les valeurs reprennent celles du module standard logging."""
    assert Severity.WARNING == logging.WARNING
    assert Severity.CRITICAL == logging.CRITICAL


def test_severity_lookup_by_name() -> None:
    """Un niveau se retrouve à partir de son nom textuel."""
    assert Severity["ERROR"] is Severity.ERROR


def test_severity_unknown_name_raises_key_error() -> None:
    """Un nom inconnu lève KeyError (à gérer lors du parsing)."""
    with pytest.raises(KeyError):
        Severity["DEBUG"]


def test_severity_str_is_its_name() -> None:
    """str() renvoie le nom du niveau, quelle que soit la version de Python."""
    assert str(Severity.ERROR) == "ERROR"
    assert f"{Severity.CRITICAL}" == "CRITICAL"


# --- LogRecord ------------------------------------------------------------


def test_log_record_is_a_plain_dict() -> None:
    """Un LogRecord reste un dict ordinaire à l'exécution."""
    record: LogRecord = {
        "timestamp": datetime(2026, 11, 4, 8, 12, tzinfo=timezone.utc),
        "severity": Severity.WARNING,
        "connection": ("203.0.113.45", 41001, "TCP"),
        "user": "admin",
        "event": "AUTH_FAILURE",
        "payload": {"reason": "bad_password"},
        "source": "auth.log",
    }
    assert type(record) is dict
    assert isinstance(record["connection"], tuple)


def test_text_fields_cover_text_format() -> None:
    """Le format texte compte six champs ordonnés."""
    assert len(TEXT_FIELDS) == 6
    assert TEXT_FIELDS[0] == "timestamp"
    assert TEXT_FIELDS[-1] == "payload"


# --- Conformité du jeu d'échantillons ---------------------------------------


def test_sample_files_exist() -> None:
    """Les quatre fichiers de démonstration sont présents."""
    for name in (
        "auth.log",
        "app_events.jsonl",
        "connections.csv",
        "blacklist.txt",
    ):
        assert (SAMPLES_DIR / name).is_file(), name


def test_text_sample_well_formed_lines_follow_spec() -> None:
    """Chaque ligne texte à six champs respecte la spécification."""
    path = SAMPLES_DIR / "auth.log"
    checked = 0
    with path.open(encoding="utf-8") as file:
        for line in file:
            fields = line.rstrip("\n").split(TEXT_SEPARATOR, 5)
            if len(fields) != len(TEXT_FIELDS):
                continue  # Lignes non conformes volontaires
            assert fields[1] in Severity.__members__
            assert fields[4] in KNOWN_EVENTS
            assert fields[2].rsplit("/", 1)[1] in SUPPORTED_PROTOCOLS
            checked += 1
    assert checked >= 20  # Le test a réellement vérifié des lignes


def test_jsonl_sample_valid_objects_follow_spec() -> None:
    """Chaque objet JSON complet utilise un niveau et un événement connus."""
    path = SAMPLES_DIR / "app_events.jsonl"
    checked = 0
    with path.open(encoding="utf-8") as file:
        for line in file:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue  # Lignes vides ou tronquées volontaires
            if not JSONL_REQUIRED_KEYS <= event.keys():
                continue  # Objet incomplet volontaire
            assert event["level"] in Severity.__members__
            assert event["event"] in KNOWN_EVENTS
            assert event["protocol"] in SUPPORTED_PROTOCOLS
            checked += 1
    assert checked >= 10  # Le test a réellement vérifié des objets


def test_csv_sample_header_matches_spec() -> None:
    """L'en-tête du CSV correspond exactement aux colonnes attendues."""
    path = SAMPLES_DIR / "connections.csv"
    with path.open(encoding="utf-8", newline="") as file:
        header = next(csv.reader(file))
    assert tuple(header) == CSV_COLUMNS
