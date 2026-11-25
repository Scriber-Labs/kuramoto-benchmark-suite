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
    "CRT_CHANNEL_M_COLOR",
    "CRT_CHANNEL_N_COLOR",
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
CRT_CHANNEL_M_COLOR: Final[str] = COLOR_PALETTE["vivid_pink"]
CRT_CHANNEL_N_COLOR: Final[str] = COLOR_PALETTE["cerulean_surge"]
_CRT_CHANNEL_M: tuple[int, int, int] = hex_to_rgb(CRT_CHANNEL_M_COLOR)
_CRT_CHANNEL_N: tuple[int, int, int] = hex_to_rgb(CRT_CHANNEL_N_COLOR)
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


def style_crt_channel(val: int | str, channel: str = "M") -> str:
    """
    Color CRT channel contributions.

    Channel M uses vivid_pink and Channel N uses cerulean_surge from the Scriber Core
    palette, so the two sampling channels are visually distinct.

    Parameters
    ----------
    val : int | str
        The value to color.
    channel : str
        Either "M" or "N" (case-insensitive).

    Returns
    -------
    str
        ANSI-escaped colored string.
    """
    channel = channel.upper()
    if channel == "M":
        rgb = _CRT_CHANNEL_M
    elif channel == "N":
        rgb = _CRT_CHANNEL_N
    else:
        raise ValueError(f"channel must be 'M' or 'N', got {channel!r}")
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
    crt_m = style_crt_channel(63, "M")
    crt_n = style_crt_channel(110, "N")

    assert "7" in term_m and "1" in gcd_str and "-3" in coeff_a
    assert "3" in remainder
    assert "63" in crt_m and "110" in crt_n

    # Verify Channel M and N use different colors
    m_rgb = f"{_CRT_CHANNEL_M[0]};{_CRT_CHANNEL_M[1]};{_CRT_CHANNEL_M[2]}"
    n_rgb = f"{_CRT_CHANNEL_N[0]};{_CRT_CHANNEL_N[1]};{_CRT_CHANNEL_N[2]}"
    assert m_rgb in crt_m
    assert n_rgb in crt_n
    assert m_rgb != n_rgb, "Channel M and N should have different colors"

    print(f"    Coprime terms: {term_m} and {term_n}")
    print(f"    Bezout terms: {coeff_a} and {coeff_b}")
    print(f"    gcd: {gcd_str}")
    print(f"    Channel M: {crt_m}")
    print(f"    Channel N: {crt_n}")

    print("✅ domain.py smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry Point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Run smoke tests for the domain module."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
