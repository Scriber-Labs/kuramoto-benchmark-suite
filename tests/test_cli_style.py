from kuramoto.cli.style import supports_256_color


class _Terminal:
    def __init__(self, is_tty: bool) -> None:
        self._is_tty = is_tty

    def isatty(self) -> bool:
        return self._is_tty


def test_256_color_requires_supported_terminal(monkeypatch):
    monkeypatch.setattr(
        "kuramoto.cli.style.sys.stdout", _Terminal(True)
    )
    monkeypatch.setenv("TERM", "xterm-256color")
    monkeypatch.delenv("COLORTERM", raising=False)
    monkeypatch.setenv("NO_COLOR", "")

    assert supports_256_color()

    monkeypatch.setenv("NO_COLOR", "1")
    assert not supports_256_color()

    monkeypatch.delenv("NO_COLOR")
    assert supports_256_color()


def test_256_color_disabled_without_tty(monkeypatch):
    monkeypatch.setattr(
        "kuramoto.cli.style.sys.stdout", _Terminal(False)
    )
    monkeypatch.setenv("TERM", "xterm-256color")
    monkeypatch.delenv("NO_COLOR", raising=False)

    assert not supports_256_color()
