"""
domain.py

Problem-specific color coders (e.g., coprime/number theory styling).

Author: Eigenscribe
Date: November 20, 2026
"""

from __future__ import annotations

from typing import Final

from eigenscribe.frontend.colors import COLOR_PALETTE, hex_to_rgb

__all__: list[str] = [
    "CRT_CHANNEL_A_COLOR",
    "CRT_CHANNEL_B_COLOR",
    "style_coprime_term",
    "style_coprime_gcd",
    "style_coprime_coeff",
    "style_coprime_remainder",
    "style_crt_channel",
]

# -----------------------------------------------------------------------------------------------------------
# 0️⃣ / 🎭 Definitions, Constants & Types
# -----------------------------------------------------------------------------------------------------------

# Color scheme per Problem 17 task specification:
#   (M, N)       -> electric_blue
#   (k_m, k_n)   -> coral_orange
#   k_true       -> vivid_pink
#   (a, b)       -> brigh_green
CRT_CHANNEL_A_COLOR: Final[str] = COLOR_PALETTE["cerulean_surge"]
CRT_CHANNEL_B_COLOR: Final[str] = COLOR_PALETTE["vivid_pink"]
_CRT_CHANNEL_A: tuple[int, int, int] = hex_to_rgb(CRT_CHANNEL_A_COLOR)
_CRT_CHANNEL_B: tuple[int, int, int] = hex_to_rgb(CRT_CHANNEL_B_COLOR)
_COPRIME_TERM: tuple[int, int, int] = hex_to_rgb(COLOR_PALETTE["green_jade"])
_COPRIME_GCD: tuple[int, int, int] = hex_to_rgb(COLOR_PALETTE["coral_orange"])
_COPRIME_COEFF: tuple[int, int, int] = hex_to_rgb(COLOR_PALETTE["deep_purple"])
_COPRIME_REMAINDER: tuple[int, int, int] = hex_to_rgb(COLOR_PALETTE["node-1"])


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
    """Color k_true (reconstructed frequency) in vivid_pink from the Scriber Core palette."""
    return _ansi_truecolor(_COPRIME_GCD, val)


def style_coprime_coeff(val: int | str) -> str:
    """Color Bézout coefficients (a, b) in brigh_green from the Scriber Core palette."""
    return _ansi_truecolor(_COPRIME_COEFF, val)


def style_coprime_remainder(val: int | str) -> str:
    """Color observed remainders (k_m, k_n) in coral_orange from the Scriber Core palette."""
    return _ansi_truecolor(_COPRIME_REMAINDER, val)


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

    term_m = style_coprime_term(7)
    term_n = style_coprime_term(11)
    gcd_str = style_coprime_gcd(1)
    coeff_a = style_coprime_coeff(-3)
    coeff_b = style_coprime_coeff(2)
    remainder = style_coprime_remainder(3)
    crt_a = style_crt_channel(110, "A")
    crt_b = style_crt_channel(63, "B")

    assert "7" in term_m and "1" in gcd_str and "-3" in coeff_a
    assert "3" in remainder
    assert "110" in crt_a and "63" in crt_b

    # Verify Channel A and B use different colors
    a_rgb = f"{_CRT_CHANNEL_A[0]};{_CRT_CHANNEL_A[1]};{_CRT_CHANNEL_A[2]}"
    b_rgb = f"{_CRT_CHANNEL_B[0]};{_CRT_CHANNEL_B[1]};{_CRT_CHANNEL_B[2]}"
    assert a_rgb in crt_a
    assert b_rgb in crt_b
    assert a_rgb != b_rgb, "Channel A and B should have different colors"

    print(f"    Coprime terms: {term_m} and {term_n}")
    print(f"    Bezout terms: {coeff_a} and {coeff_b}")
    print(f"    gcd: {gcd_str}")
    print(f"    Channel A: {crt_a}")
    print(f"    Channel B: {crt_b}")

    print("✅ domain.py smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry Point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Run smoke tests for the domain module."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
