from typer.testing import CliRunner

from pucoti.app import app
from pucoti.controller import cli


runner = CliRunner()


def test_pucoti_help():
    """Test that the main pucoti CLI --help works."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "PUCOTI" in result.stdout or "pucoti" in result.stdout.lower()


def test_pucoti_msg_help():
    """Test that the pucoti-msg CLI --help works."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Usage:" in result.stdout
    assert "Commands" in result.stdout or "set-purpose" in result.stdout
