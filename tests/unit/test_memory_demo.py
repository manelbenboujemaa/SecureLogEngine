"""Tests du script de démonstration de la consommation mémoire."""

from pathlib import Path

import pytest

from scripts.memory_demo import (
    format_size,
    generate_log_file,
    main,
    measure_peak,
    run_demo,
)


def test_generate_log_file_writes_requested_lines(tmp_path: Path) -> None:
    """Le fichier généré contient exactement le nombre de lignes demandé."""
    path = tmp_path / "demo.log"
    generate_log_file(path, 50)
    assert len(path.read_text(encoding="utf-8").splitlines()) == 50


def test_measure_peak_returns_result_and_positive_peak() -> None:
    """measure_peak renvoie le résultat de l'action et un pic mémoire."""
    count, peak = measure_peak(lambda: len([0] * 10_000))
    assert count == 10_000
    assert peak > 0


@pytest.mark.parametrize(
    ("size", "expected"),
    [(512, "512 o"), (2048, "2.0 Ko"), (5 * 1024**2, "5.0 Mo")],
)
def test_format_size(size: int, expected: str) -> None:
    """Les tailles sont affichées dans l'unité adaptée."""
    assert format_size(size) == expected


def test_generator_uses_far_less_memory_than_full_load(tmp_path: Path) -> None:
    """Observation chiffrée : le générateur bat largement les deux autres."""
    path = tmp_path / "demo.log"
    generate_log_file(path, 50_000)
    peaks = dict(run_demo(path))
    generator = peaks["read_lines (générateur)"]
    assert generator * 10 < peaks["list(read_lines(...))"]
    assert generator * 10 < peaks["read_text().splitlines()"]


def test_main_runs_and_prints_report(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Le script s'exécute de bout en bout et affiche le tableau."""
    assert main(["--lines", "2000"]) == 0
    output = capsys.readouterr().out
    assert "Pic mémoire" in output
    assert "fois moins de mémoire" in output


def test_main_on_small_file_does_not_claim_a_gain(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Sur un petit fichier, le script n'annonce pas de gain trompeur."""
    sample = Path(__file__).resolve().parents[2] / "data/samples/auth.log"
    assert main(["--file", str(sample)]) == 0
    assert "trop petit" in capsys.readouterr().out
