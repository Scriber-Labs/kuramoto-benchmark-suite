from kuramoto.cli.style import supports_256_color


class _Terminal:
    def __init__(self, is_tty: bool) -> None:
        self._is_tty = is_tty

    def isatty(self) -> bool:
        return self._is_tty


def test_256_color_requires_supported_terminal(monkeypatch):
    monkeypatch.setattr("kuramoto.cli.style.sys.stdout", _Terminal(True))
    monkeypatch.setenv("TERM", "xterm-256color")
    monkeypatch.delenv("COLORTERM", raising=False)
    monkeypatch.setenv("NO_COLOR", "")

    assert supports_256_color()

    monkeypatch.setenv("NO_COLOR", "1")
    assert not supports_256_color()

    monkeypatch.delenv("NO_COLOR")
    assert supports_256_color()


def test_256_color_disabled_without_tty(monkeypatch):
    monkeypatch.setattr("kuramoto.cli.style.sys.stdout", _Terminal(False))
    monkeypatch.setenv("TERM", "xterm-256color")
    monkeypatch.delenv("NO_COLOR", raising=False)

    assert not supports_256_color()


def test_multi_gradient_rendering() -> None:
    from kuramoto.cli.style import PRESETS, hex_to_rgb, multi_gradient

    assert hex_to_rgb("#00a6ff") == (0, 166, 255)
    assert hex_to_rgb("a855f7") == (168, 85, 247)

    assert multi_gradient("") == ""
    electric = multi_gradient("Electric", PRESETS["electric"])
    assert "\033[0m" in electric
    assert "\033[1;38;2;" in electric


def test_style_coprime_helpers() -> None:
    from kuramoto.cli.style import (
        style_coprime_coeff,
        style_coprime_gcd,
        style_coprime_term,
    )

    assert "7" in style_coprime_term(7)
    assert "1" in style_coprime_gcd(1)
    assert "-3" in style_coprime_coeff(-3)
