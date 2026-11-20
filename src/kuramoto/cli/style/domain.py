"""
domain.py

Problem-specific color coders (e.g., coprime/number theory styling).

Author: Eigenscribe
Date: November 20, 2026
"""

from __future__ import annotations

__all__: list[str] = [
    "style_coprime_term",
    "style_coprime_gcd",
    "style_coprime_coeff",
]


# -----------------------------------------------------------------------------------------------------------
# 1️⃣ Public API
# -----------------------------------------------------------------------------------------------------------


def style_coprime_term(val: int | str) -> str:
    """Color (a, b) coprime terms in cyan (#00a6ff)."""
    return f"\033[38;2;0;166;255m{val}\033[0m"


def style_coprime_gcd(val: int | str) -> str:
    """Color gcd values in green (#28d728)."""
    return f"\033[38;2;40;215;40m{val}\033[0m"


def style_coprime_coeff(val: int | str) -> str:
    """Color Bezout coefficients (x, y) in magenta (#ff00c3)."""
    return f"\033[38;2;255;0;195m{val}\033[0m"


# -----------------------------------------------------------------------------------------------------------
# 💨 Smoke Tests
# -----------------------------------------------------------------------------------------------------------


def _run_smoke_test() -> None:
    """Quick sanity check for domain color coders."""
    print("💨 Running domain.py smoke tests...")
    
    term = style_coprime_term(7)
    gcd_str = style_coprime_gcd(1)
    coeff = style_coprime_coeff(-3)
    
    assert "7" in term and "1" in gcd_str and "-3" in coeff
    assert "\033[38;2;0;166;255m" in term
    assert "\033[38;2;40;215;40m" in gcd_str
    assert "\033[38;2;255;0;195m" in coeff
    
    print("✅ domain.py smoke test passed.")


# -----------------------------------------------------------------------------------------------------------
# 🔥 Entry Point
# -----------------------------------------------------------------------------------------------------------


def main() -> None:
    """Run smoke tests for the domain module."""
    _run_smoke_test()


if __name__ == "__main__":
    main()
