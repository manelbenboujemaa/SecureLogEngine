"""Tests de fumée : vérifient que le squelette du projet est opérationnel."""

import subprocess
import sys
from pathlib import Path

import pytest

import log_engine
from log_engine.cli import main

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_package_exposes_version() -> None:
    """Le package expose une version au format MAJEUR.MINEUR.CORRECTIF."""
    assert len(log_engine.__version__.split(".")) == 3


def test_cli_without_arguments_returns_success() -> None:
    """Sans argument, la CLI affiche l'aide et renvoie le code 0."""
    assert main([]) == 0


def test_cli_version_option(capsys: pytest.CaptureFixture[str]) -> None:
    """L'option --version affiche la version et quitte proprement."""
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert log_engine.__version__ in capsys.readouterr().out


def test_main_script_runs() -> None:
    """Le point d'entrée main.py s'exécute sans erreur."""
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "main.py"), "--version"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert log_engine.__version__ in result.stdout
