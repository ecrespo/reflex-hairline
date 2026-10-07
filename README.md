# reflex-hairline

[Hairline](https://hairline.lucasmarkes.com)'s twenty-seven isometric line figures that answer the pointer, as [Reflex](https://reflex.dev) components.

Each figure is an SVG drawing that reacts to the mouse: pillars rise around it, a vault dial turns, a drawer slides out. They are useful as hero art, as section illustrations and, at 160–240px, as **empty states**. This package wraps `@lucasmarkes/hairline` v0.3.0 (MIT, by Lucas Marques) and adds a few things the React entry does not have: figures picked by a state var, figures made with the `hairline-create` agent skill, and theming from Python.

```bash
pip install reflex-hairline
# or
uv add reflex-hairline
```

Reflex installs the npm package (`@lucasmarkes/hairline@0.3.0`) on the next `reflex run`; there is nothing else to set up.

## Quick start

```python
import reflex as rx
from reflex_hairline import hairline


class State(rx.State):
    caption: str = "rest"

    @rx.event
    def set_caption(self, text: str):
        self.caption = text


def index() -> rx.Component:
    return rx.vstack(
        hairline.terrain(
            intensity=0.7,  # 0 (subtle) … 1 (strong), default 0.5
            theme="auto",  # "auto" | "light" | "dark"
            label="A field of pillars",  # accessible name
            on_read=State.set_caption,  # the figure's caption, each time it changes
            width="480px",
        ),
        rx.text(State.caption),
    )


app = rx.App()
app.add_page(index)
```

A figure renders one `<div>` that fills its parent's width at a **5:4 aspect ratio**. Size it with `width=` (or its parent). Every other style prop, `id`, `class_name`, `on_click`, etc. passes through to the div.

## The figures

All 27 are available three ways: `hairline.<id>(...)`, a snake_case factory (`from reflex_hairline import terrain`) and a component class (`Terrain.create(...)`).

| id | What it is | Higher `intensity` |
| --- | --- | --- |
| `riffle` | A tray of eight cards. The card under the pointer stands up; arrow keys walk the cards. | The ripple spreads further. |
| `terrain` | Eighty-one pillars on a plinth that rise around the pointer. | A wider area rises. |
| `exploded` | An app window in four layers. Across opens the gap; down picks a layer. | The layers open further. |
| `phosphor` | A dot matrix that plays a loop and fades like phosphor where you paint. | The trail lingers longer. |
| `slow` | Crates riding a belt through a gate. Hovering slows the clock. | Time slows down more. |
| `turntable` | Blocks on a turntable. A flick spins it; it settles on a quarter turn. | The spin coasts longer. |
| `keyboard` | A sixty-key board. The key under the pointer sinks; neighbours follow. | A wider patch sinks. |
| `elevator` | Four floors beside a shaft. The pointer's height picks a floor. | The car travels faster. |
| `phone` | A phone in layers: glass, board, battery, shell. | The layers open further. |
| `laptop` | A thin laptop. The pointer's height sets the lid. | The lid opens wider. |
| `terminal` | A terminal. The pointer's height scrolls back; the line under it lifts. | The lift spreads further. |
| `cabinet` | A rack of twelve blades. The pointer pulls the nearest ones out. | More blades come out. |
| `branches` | A commit graph. The commit under the pointer rises with its history. | More history rises. |
| `vault` | A vault door. Circling turns the dial; on the combination the bolts draw back. | The dial coasts longer. |
| `lockers` | Twelve lockers, one ajar. The locker under the pointer opens. | The door opens wider. |
| `padlock` | A padlock. As the pointer nears, the shackle swings open. | The shackle swings further. |
| `patch` | A patch panel of 24 ports. The cable under the pointer lifts. | The lean spreads further. |
| `dish` | A parabolic dish on a gimbal. The pointer aims it. | The dish swings further. |
| `router` | A router whose antennas lean toward the pointer. | The lean spreads further. |
| `loupe` | A stand loupe over a blank ruled sheet. | The glass magnifies more. |
| `sieve` | Three test sieves over a pan. The pointer's height lifts one. | The gap opens further. |
| `rail` | A garment rail with seven bare hangers. | The brush reaches more hangers. |
| `plug` | A plug on the floor, drawn up toward the socket. It stops short. | The plug comes closer. |
| `query` | A question mark as a bent bar over a loose ball. | The hook turns further. |
| `drawer` | A cabinet of three drawers. The pointer's height opens one, empty. | The drawer opens further. |
| `basket` | A wire basket that tilts toward the pointer. | The basket tilts further. |
| `plot` | A bar chart with no data: seven flat tabs. | The tabs lift higher. |

The same data is available in Python as `FIGURES` / `BY_ID` (`FigureInfo` with `name`, `summary`, `stronger`, default `label`, `rest` caption, and the internal `parameter`, `unit` and `range` that `intensity` maps onto).

## Options

| Prop | Type | Default | |
| --- | --- | --- | --- |
| `intensity` | `float` | `0.5` | How strongly the figure answers the pointer, 0…1. Out-of-range values are clamped. Reaches the running figure without a remount. |
| `theme` | `"auto" \| "light" \| "dark"` | `"auto"` | `"auto"` follows the page: an ancestor with class `dark` (Reflex's color mode sets it) or `data-theme="dark"`, then `color-scheme`. |
| `label` | `str` | an English description | The accessible name. `aria_label=` works too. |
| `on_read` | event `(str)` | | The caption each time it changes: `"03"`, `"gap 28.0"`, `"rate 0.20×"`. Fired once at mount with the rest caption. |

All props accept state vars.

## Picking a figure at runtime

```python
hairline.figure(figure=State.figure_id, fallback="terrain", intensity=State.intensity)
# hairline(figure=...) is the same thing
```

Changing `figure` remounts the drawing; an unknown id draws `fallback`.

## Theming

Hairline reads six CSS custom properties. Set them from Python with keyword shortcuts on any figure:

```python
hairline.vault(plate="#0b1020", hi="#e2e8f0", edge="#64748b", mid="#334155", lo="#1e293b", stroke=1.1)
```

or build a style dict with `tokens()` and put it on any ancestor (they inherit):

```python
from reflex_hairline import tokens

rx.grid(*figures, style=tokens(palette="radix"))
```

| Shortcut | Property | Role |
| --- | --- | --- |
| `plate` | `--hairline-plate` | Fill of every plate. **Set it to the background the figure sits on.** |
| `hi` | `--hairline-hi` | What is lit. |
| `edge` | `--hairline-edge` | Silhouettes. |
| `mid` | `--hairline-mid` | Every other stroke. |
| `lo` | `--hairline-lo` | What recedes. |
| `stroke` | `--hairline-stroke` | Stroke width in CSS px (default 0.9). |

Palettes for `palette=`: `"light"` and `"dark"` (Hairline's own), `"radix"` (mapped to Radix Themes gray tokens, so figures follow `rx.theme` and color mode) and `"radix-accent"` (lit strokes in your accent colour). Explicit shortcuts win over the palette, and a `style=` you pass wins over both. The dicts are exported as `LIGHT`, `DARK`, `RADIX_TOKENS`, `RADIX_ACCENT_TOKENS` and `PALETTES`.

## Empty states

```python
hairline.empty_state(
    "sieve",
    "No results match these filters",
    "Try removing a filter.",
    rx.button("Clear filters", on_click=State.clear),
    width="200px",
)
```

Hairline recommends 160–240px above a heading and one action; the rest pose is the picture, the pointer is a bonus. `loupe`, `sieve`, `rail`, `plug`, `query`, `drawer`, `basket` and `plot` were drawn for this.

## Figures made with the `hairline-create` skill

[`hairline-create`](https://hairline.lucasmarkes.com/skill) is Hairline's skill for coding agents (`npx skills add lucasmarkes/hairline`, then `/hairline-create a sales funnel`). It outputs `hairline-<name>.html`, one file drawn on the same kernel as the packaged figures. `hairline.custom` mounts it natively, with the same options:

```python
# put hairline-funnel.html in your app's assets/ folder
hairline.custom(
    src="/hairline-funnel.html",  # or the figure's .js file, or code="..."
    intensity=State.intensity,
    theme="auto",
    on_read=State.set_caption,
    on_load=State.loaded,  # {name, means, rules, range}
    on_error=State.failed,  # str
)
```

`intensity` is mapped onto the figure's declared `range`, exactly as the packaged figures map theirs. The figure's script runs in the page, so only load files you trust.

## Notes

- **Accessibility.** A figure is an image (`role="img"`) with a description you can replace with `label`. Riffle is a focusable group whose arrow keys walk the cards.
- **Reduced motion.** With `prefers-reduced-motion`, Phosphor and Slow hold still; every figure still answers the pointer.
- **Performance.** All figures on a page share one `requestAnimationFrame` loop; a figure off screen or at rest does no work.
- **SSR.** On the server a figure is an empty 5:4 box, so nothing shifts when it draws.

## Demo

```bash
git clone https://github.com/ecrespo/reflex-hairline
cd reflex-hairline
uv sync
cd hairline_demo
uv run reflex run
```

Pages: Gallery (all 27 with live `on_read` captions), Playground (every option and generated code), Theming, Empty states, Skill figures, and an API Reference.

## Development

```bash
uv sync                          # editable install + dev tools
uv run pytest                    # unit tests
uv run reflex component build    # .pyi stubs + sdist/wheel in dist/
```

### CI and releases

- `CI (code quality)`: ruff lint/format, pytest on Python 3.10–3.13, demo `reflex compile`, build + `twine check`.
- `Security`: gitleaks, bandit, pip-audit, dependency review (PRs) and CodeQL; also weekly.
- `Release`: push a tag `vX.Y.Z` matching `version` in `pyproject.toml`. It re-runs both suites, builds,
  **pre-publishes to TestPyPI**, installs it back from there, then publishes to PyPI and creates the GitHub Release.
  Pre-release versions (`X.Y.ZrcN`, `aN`, `bN`, `.devN`) stop after TestPyPI. Publishing uses PyPI Trusted Publishing (no tokens).

## Credits and license

Hairline, its figures and the `hairline-create` kernel (`hairline_kernel.js`, shipped unchanged apart from an ES module export) are © Lucas Marques, MIT; see `LICENSE.hairline`. The demo includes four example figures from hairline.lucasmarkes.com/skill. This Reflex wrapper is © Ernesto Crespo, MIT.
