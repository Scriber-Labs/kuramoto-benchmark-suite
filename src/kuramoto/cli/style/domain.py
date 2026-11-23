"""
domain.py

Problem-specific color coders (e.g., coprime/number theory styling).

Author: Eigenscribe
Date: November 20, 2026
"""

from __future__ import annotations

from scriber_core.frontend.colors import COLOR_PALETTE, hex_to_rgb

__all__: list[str] = [
    "style_coprime_term",
    "style_coprime_gcd",
    "style_coprime_coeff",
    "style_crt_channel",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

# CRT channel colors drawn from the Scriber Core palette
_CRT_CHANNEL_A: tuple[int, int, int] = hex_to_rgb(COLOR_PALETTE["electric_blue"])   # #00a6ff
_CRT_CHANNEL_B: tuple[int, int, int] = hex_to_rgb(COLOR_PALETTE["coral_orange"])     # #ff783d
_COPRIME_TERM: tuple[int, int, int] = hex_to_rgb(COLOR_PALETTE["electric_blue"])     # #00a6ff
_COPRIME_GCD: tuple[int, int, int] = hex_to_rgb(COLOR_PALETTE["brigh_green"])        # #28d728
_COPRIME_COEFF: tuple[int, int, int] = hex_to_rgb(COLOR_PALETTE["bright_magenta"])   # #ff00c3


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API
# -----------------------------------------------------------------------------------------------------------


def _ansi_truecolor(rgb: tuple[int, int, int], val: int | str) -> str:
    """Wrap *val* in a TrueColor ANSI escape using the given RGB tuple."""
    r, g, b = rgb
    return f"\033[38;2;{r};{g};{b}m{val}\033[0m"


def style_coprime_term(val: int | str) -> str:
    """Color (a, b) coprime terms in electric_blue from the Scriber Core palette."""
    return _ansi_truecolor(_COPRIME_TERM, val)


def style_coprime_gcd(val: int | str) -> str:
    """Color gcd values in brigh_green from the Scriber Core palette."""
    return _ansi_truecolor(_COPRIME_GCD, val)


def style_coprime_coeff(val: int | str) -> str:
    """Color Bezout coefficients (x, y) in bright_magenta from the Scriber Core palette."""
    return _ansi_truecolor(_COPRIME_COEFF, val)


def style_crt_channel(val: int | str, channel: str = "A") -> str:
    """
    Color CRT channel contributions.

    Channel A uses electric_blue (#00a6ff) and Channel B uses coral_orange (#ff783d)
    from the Scriber Core palette, so the two sampling channels are visually distinct.

    Parameters
    ----------
    val : int | str
        The value to color.
    channel : str
        Either "A" or "B" (case-insensitive).

    Returns
    -------
    str
        ANSI-escaped colored string.
    """
    rgb = _CRT_CHANNEL_A if channel.upper() == "A" else _CRT_CHANNEL_B
    return _ansi_truecolor(rgb, val)


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke Tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for domain color coders."""
    print("💨 Running domain.py smoke tests...")

    term = style_coprime_term(7)
    gcd_str = style_coprime_gcd(1)
    coeff = style_coprime_coeff(-3)
    crt_a = style_crt_channel(110, "A")
    crt_b = style_crt_channel(63, "B")

    assert "7" in term and "1" in gcd_str and "-3" in coeff
    assert "110" in crt_a and "63" in crt_b

    # Verify Channel A and B use different colors
    a_rgb = f"{_CRT_CHANNEL_A[0]};{_CRT_CHANNEL_A[1]};{_CRT_CHANNEL_A[2]}"
    b_rgb = f"{_CRT_CHANNEL_B[0]};{_CRT_CHANNEL_B[1]};{_CRT_CHANNEL_B[2]}"
    assert a_rgb in crt_a
    assert b_rgb in crt_b
    assert a_rgb != b_rgb, "Channel A and B should have different colors"

    print("✅ domain.py smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry Point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Run smoke tests for the domain module."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
