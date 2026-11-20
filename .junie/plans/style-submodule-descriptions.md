---
sessionId: session-261120-114330-1508
---

# Submodule Descriptions

### ✓ Submodule Descriptions for `kuramoto/cli/style/`

Here's a description for each submodule, what it should contain, and where to find the code in the current `style.py`.

---

#### ✓ `types.py`
**Purpose:** Type aliases used across the style package.

**Content:**
- `RGB: TypeAlias = tuple[int, int, int]` (line 69)
- `Color: TypeAlias = str | RGB` (line 70)

**Dependencies:** None (pure type definitions).

---

#### ✓ `color_utils.py` (done - tested)
**Purpose:** Low-level color conversion and terminal detection utilities.

**Content:**
- `supports_256_color() -> bool` (lines 159-181)
- `ansi_256(color_name, text, bold) -> str` (lines 184-207)
- `hex_to_rgb(hex_color) -> RGB` (lines 210-237)
- `_normalize_color(color) -> RGB` (lines 240-254)

**Dependencies:** `types.py` (for `RGB`, `Color`), `palettes.py` (for `ANSI_256_PALETTE` in `ansi_256`).

---

#### ✓ `palettes.py` (done - tested)
**Purpose:** Static color maps and palette definitions.

**Content:**
- `STYLE_MAP` (lines 104-116)
- `COLOR_PALETTE` (lines 119-134)
- `ANSI_256_PALETTE` (lines 137-148)
- `EIGENSCRIBE_PALETTE` (line 151)

**Dependencies:** None (pure constants).

---

#### ✓ `gradients.py` (done - tested)
**Purpose:** TrueColor gradient engine and preset definitions.

**Content:**
- `PRESETS` (lines 72-102) — note: references `COLOR_PALETTE` and `GRADIENT_PRESETS`
- `multi_gradient(text, colors, bold) -> str` (lines 257-307)
- `cli_gradient = multi_gradient` (line 311)

**Dependencies:** `types.py` (for `RGB`, `Color`), `color_utils.py` (for `_normalize_color`), `palettes.py` (for `COLOR_PALETTE` in `PRESETS`).

**Imports needed:**
- `from scriber_core.frontend.colors import COLOR_PALETTE`
- `from scriber_core.frontend.gradients import GRADIENT_PRESETS`

---

#### ✓ `domain.py` (done - tested)
**Purpose:** Problem-specific color coders (e.g., coprime/number theory styling).

**Content:**
- `style_coprime_term(val) -> str` (lines 314-316)
- `style_coprime_gcd(val) -> str` (lines 319-321)
- `style_coprime_coeff(val) -> str` (lines 324-326)

**Dependencies:** None (standalone TrueColor helpers).

---

#### ✓ `layout.py` (done - tested)
**Purpose:** Structural formatting — section headers, dividers, rules, and banners.

**Content:**
- `cli_echo(msg, **kwargs) -> None` (lines 329-341)
- `cli_rule(char, width, level) -> None` (lines 344-358)
- `cli_banner() -> None` (lines 361-394)
- `cli_section(title) -> None` (lines 534-547)
- `cli_divider() -> None` (lines 550-554)

**Dependencies:** `palettes.py` (for `STYLE_MAP` in `cli_rule`), `color_utils.py` (for `supports_256_color`, `ansi_256` in `cli_banner`).

**Imports needed:** `click`

---

#### ✓ `messages.py` (done - tested)
**Purpose:** Semantic echo functions — domain-specific CLI messages with emojis.

**Content:**
- `cli_message(msg, level, bold) -> None` (lines 397-411)
- `cli_info(msg) -> None` (lines 414-423)
- `cli_network(msg) -> None` (lines 426-435)
- `cli_quantum(msg) -> None` (lines 438-447)
- `cli_rotor(msg) -> None` (lines 450-459)
- `cli_success(msg) -> None` (lines 462-471)
- `cli_warning(msg) -> None` (lines 474-483)
- `cli_error(msg) -> None` (lines 486-495)
- `cli_highlight(msg) -> None` (lines 498-507)
- `cli_zbw(msg) -> None` (lines 510-519)
- `cli_coprime(msg) -> None` (lines 522-531)

**Dependencies:** `palettes.py` (for `STYLE_MAP` in `cli_message`).

**Imports needed:** `click`

---

#### ✓ `__init__.py` (done - tested)
**Purpose:** Package initialization — re-exports all public symbols for backward compatibility.

**Content:**
- Import and re-export everything from the submodules so that existing imports like `from kuramoto.cli.style import cli_info` continue to work.
- Follow the existing `__all__` list from `style.py` (lines 31-63).

**Order of imports matters to avoid circular dependencies:**
1. `types.py` (no deps)
2. `palettes.py` (no deps)
3. `color_utils.py` (depends on types, palettes)
4. `gradients.py` (depends on types, color_utils, palettes)
5. `domain.py` (no deps)
6. `layout.py` (depends on palettes, color_utils)
7. `messages.py` (depends on palettes)

# Delivery Steps

### ✓ Step 1: Write submodule descriptions
Provide descriptions for each submodule so you know what to move where.

### ✓ Step 2: Guide manual migration
Work through each submodule one at a time: you move the code, I verify the imports and structure are correct.