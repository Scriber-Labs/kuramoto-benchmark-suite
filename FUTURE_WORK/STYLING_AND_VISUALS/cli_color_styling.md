# CLI Color Styling / Attention Support

## Why this matters

Color styling in the CLI is not just visual polish. It helps with attention, orientation, and quickly distinguishing message types while working in the terminal.

This should eventually become a small intentional styling layer rather than scattered one-off color choices.

## Current trigger

Click supports a limited color vocabulary for `fg=...`. For example, `purple` is not a supported Click foreground color name, even though it is an intuitive color name.

Click accepts colors such as:

- `black`
- `red`
- `green`
- `yellow`
- `blue`
- `magenta`
- `cyan`
- `white`
- bright variants such as `bright_magenta`

For now, use `magenta` or `bright_magenta` when a purple-like CLI message is needed.

## Future goal

Create a small internal CLI style API so command code can use meaningful style names instead of raw Click colors or ANSI escape codes.

Example future usage:
```python
cli_info("Parsing configuration...") 
cli_success("Dataset saved.") 
cli_warning("Lie symmetry tracking requires a rotor or Euler solver.") 
cli_error("Missing configuration file.") 
cli_purple("Visualizing network...")
```
or
```python
cli_message("Visualizing network...", style="purple")
```


## Design principles

- Keep command code readable.
- Use semantic names where possible: `success`, `warning`, `error`, `info`, `accent`.
- Allow personal attention-support colors like `purple`.
- Avoid making the CLI noisy or inconsistent.
- Keep the first implementation small.
- Do not build a full standalone package until the need is clearly bigger than this project.

## Possible implementation phases

### Phase 1: Minimal Click wrapper

Use Click’s built-in colors, mapping project style names to Click-supported names.
```python
python STYLE_COLORS = { 
    "info": "blue", 
    "success": "bright_green", 
    "warning": "yellow", 
    "error": "red", 
    "accent": "bright_magenta", 
    "purple": "bright_magenta",
}
```


### Phase 2: ANSI truecolor support

Support RGB colors manually for terminals that support 24-bit color.

Example purple:
```python
"\033[38;2;128;0;255mmessage\033[0m"
```

Potential API:
```python
python cli_rgb("Visualizing network...", 128, 0, 255)
```


### Phase 3: Rich integration

Consider adding `rich` if the project needs better terminal UI features:

- custom named styles
- hex colors
- styled tables
- panels
- progress bars
- improved tracebacks

Example:
```python
from rich.console import Console
console = Console() console.print("Visualizing network...", style="#8000ff")
```

## Potential file locations

Possible implementation file:
```text
src/kuramoto/cli/style.py
```

or, if kept very small:
```python
text src/kuramoto/cli/utils.py
```

Preferrred long-term location
```text
text
text src/kuramoto/cli/style.py
```

## Related cleanup opportunity
If a styling helper is added, migrate existing direct calls like:
```python
click.secho(..., fg="green") click.secho(..., fg="blue") click.secho(..., fg="yellow") click.secho(..., fg="bright_green")
```
to semantic wrappers.

Example:
```python
cli_success(...) 
cli_info(...) 
cli_warning(...)
```

## Status

Parked for later. Do not pursue during unrelated debugging unless CLI output styling is the actual task.