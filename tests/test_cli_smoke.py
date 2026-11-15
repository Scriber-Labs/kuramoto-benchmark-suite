from __future__ import annotations

import kuramoto.cli.commands as cli_commands
import kuramoto.cli.main as cli_main
import kuramoto.cli.style as cli_style
import kuramoto.cli.utils as cli_utils


def test_cli_style_smoke_test() -> None:
    """Verify CLI style smoke test runs without errors."""
    cli_style._run_smoke_test()


def test_cli_utils_smoke_test() -> None:
    """Verify CLI utils smoke test runs without errors."""
    cli_utils._run_smoke_test()


def test_cli_commands_smoke_test() -> None:
    """Verify CLI commands smoke test runs without errors."""
    cli_commands._run_smoke_test()


def test_cli_main_smoke_test() -> None:
    """Verify CLI main group registration smoke test runs without errors."""
    cli_main._run_smoke_test()
