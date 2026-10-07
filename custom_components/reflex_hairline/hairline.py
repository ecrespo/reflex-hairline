"""Reflex wrapper for Hairline: twenty-seven isometric line figures that answer the pointer.

Hairline (https://hairline.lucasmarkes.com, MIT, by Lucas Marques) ships one
React component per figure from ``@lucasmarkes/hairline/react``. This module
wraps each of them as a Reflex component, and adds three things the React
entry does not have:

* ``figure(figure=...)``: any of the twenty-seven, picked by id at runtime, so a
  state var can switch figures.
* ``custom(src=...)``: a figure made with the ``hairline-create`` agent skill
  (a ``hairline-<name>.html`` page or its ``<name>.js`` file), mounted natively
  on the same kernel with the same options.
* Python-side theming: ``plate=``, ``hi=``, ``edge=``, ``mid=``, ``lo=``,
  ``stroke=`` and ``palette="radix"`` write the six ``--hairline-*`` custom
  properties for you.

Every figure takes the same options: ``intensity`` (0..1, default 0.5),
``theme`` (``"auto" | "light" | "dark"``), ``label`` (accessible name) and the
``on_read`` event, which receives the figure's caption each time it changes.
"""

from __future__ import annotations

from typing import Any, ClassVar, Literal

import reflex as rx
from reflex.event import passthrough_event_spec
from reflex.utils.imports import ImportVar

from .catalogue import BY_ID, FIGURE_IDS, FIGURES, FigureInfo

HAIRLINE_VERSION: str = "0.3.0"
"""The version of ``@lucasmarkes/hairline`` this package is built and tested against."""

HAIRLINE_NPM: str = f"@lucasmarkes/hairline@{HAIRLINE_VERSION}"

ThemeName = Literal["auto", "light", "dark"]
FigureId = Literal[
    "riffle", "terrain", "exploded", "phosphor", "slow", "turntable", "keyboard",
    "elevator", "phone", "laptop", "terminal", "cabinet", "branches", "vault",
    "lockers", "padlock", "patch", "dish", "router", "loupe", "sieve", "rail",
    "plug", "query", "drawer", "basket", "plot",
]  # fmt: skip

# --------------------------------------------------------------------------- #
# Theme                                                                       #
# --------------------------------------------------------------------------- #

LIGHT: dict[str, str] = {
    "--hairline-plate": "#ffffff",
    "--hairline-hi": "#232327",
    "--hairline-edge": "#a4a4ac",
    "--hairline-mid": "#c3c3c9",
    "--hairline-lo": "#e0e0e4",
    "--hairline-stroke": "0.9",
}
"""Hairline's own light palette, as the six public custom properties."""

DARK: dict[str, str] = {
    "--hairline-plate": "#08090a",
    "--hairline-hi": "#d0d6e0",
    "--hairline-edge": "#5b5d64",
    "--hairline-mid": "#3e3e44",
    "--hairline-lo": "#29292d",
    "--hairline-stroke": "0.9",
}
"""Hairline's own dark palette, as the six public custom properties."""

RADIX_TOKENS: dict[str, str] = {
    "--hairline-plate": "var(--color-panel-solid)",
    "--hairline-hi": "var(--gray-12)",
    "--hairline-edge": "var(--gray-10)",
    "--hairline-mid": "var(--gray-7)",
    "--hairline-lo": "var(--gray-5)",
}
"""The palette mapped to Radix Themes tokens, so figures follow ``rx.theme`` and color mode.

``--hairline-plate`` is the panel colour; if the figure sits straight on the page
background, override it with ``plate="var(--color-background)"``.
"""

RADIX_ACCENT_TOKENS: dict[str, str] = {
    **RADIX_TOKENS,
    "--hairline-hi": "var(--accent-11)",
    "--hairline-edge": "var(--accent-8)",
}
"""Like :data:`RADIX_TOKENS`, with the lit stroke and silhouettes in the theme's accent colour."""

PALETTES: dict[str, dict[str, str]] = {
    "light": LIGHT,
    "dark": DARK,
    "radix": RADIX_TOKENS,
    "radix-accent": RADIX_ACCENT_TOKENS,
}

_TOKEN_KWARGS: tuple[str, ...] = ("plate", "hi", "edge", "mid", "lo", "stroke")


def tokens(
    *,
    plate: Any = None,
    hi: Any = None,
    edge: Any = None,
    mid: Any = None,
    lo: Any = None,
    stroke: Any = None,
    palette: str | dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a style dict of ``--hairline-*`` custom properties.

    Put the result on a figure (``style=``) or on any ancestor, such as a grid
    of figures: the properties inherit.

    Args:
        plate: Fill of every plate. Must match the background the figure sits on.
        hi: Stroke of what is lit.
        edge: Silhouettes.
        mid: Every other stroke.
        lo: What recedes.
        stroke: Stroke width in CSS pixels (default 0.9).
        palette: A base palette: ``"light"``, ``"dark"``, ``"radix"``,
            ``"radix-accent"`` or a dict of custom properties. Explicit keyword
            values win over it.

    Returns:
        A dict usable as (part of) a Reflex ``style``.
    """
    out: dict[str, Any] = {}
    if isinstance(palette, str):
        if palette not in PALETTES:
            msg = f"hairline: unknown palette {palette!r}; use one of {sorted(PALETTES)} or a dict."
            raise ValueError(msg)
        out.update(PALETTES[palette])
    elif isinstance(palette, dict):
        out.update(palette)
    for name, value in (("plate", plate), ("hi", hi), ("edge", edge), ("mid", mid), ("lo", lo), ("stroke", stroke)):
        if value is not None:
            out[f"--hairline-{name}"] = value
    return out


def _merge_theme_kwargs(props: dict[str, Any]) -> dict[str, Any]:
    """Pop the Python-only theme kwargs and fold them into ``style``."""
    palette = props.pop("palette", None)
    given = {k: props.pop(k) for k in _TOKEN_KWARGS if k in props}
    if palette is None and not given:
        return props
    style = tokens(palette=palette, **given)
    user_style = props.get("style")
    if user_style:
        style.update(user_style)
    props["style"] = style
    return props


# --------------------------------------------------------------------------- #
# The packaged figures                                                        #
# --------------------------------------------------------------------------- #


class HairlineBase(rx.Component):
    """Shared props and events of every Hairline figure.

    Renders a ``<div>`` that fills its parent's width at a 5:4 aspect ratio.
    Size it with ``width=`` (or its parent); any div attribute and style passes
    through.
    """

    library = HAIRLINE_NPM

    # How strongly the figure answers the pointer, from 0 (subtle) to 1 (strong). Default 0.5.
    intensity: rx.Var[float]

    # "auto" follows the page (Reflex color mode included), or force "light" / "dark".
    theme: rx.Var[ThemeName]

    # The accessible name. Each figure has a default English description.
    label: rx.Var[str]

    # The figure's caption each time it changes ("03", "gap 28.0", "rate 0.20×"); fired once at mount.
    on_read: rx.EventHandler[passthrough_event_spec(str)]

    _figure_id: ClassVar[str | None] = None

    @property
    def import_var(self) -> ImportVar:
        """Import the tag from the package's ``/react`` entry.

        Returns:
            The import var, pointing at ``@lucasmarkes/hairline/react``.
        """
        return ImportVar(tag=self.tag, is_default=False, alias=self.alias, package_path="/react")

    @classmethod
    def create(
        cls,
        *children: Any,
        plate: Any = None,
        hi: Any = None,
        edge: Any = None,
        mid: Any = None,
        lo: Any = None,
        stroke: Any = None,
        palette: Any = None,
        **props: Any,
    ) -> rx.Component:
        """Create the figure.

        Args:
            *children: Ignored: a figure draws its own content.
            plate: ``--hairline-plate``, the fill of every plate; match the background.
            hi: ``--hairline-hi``, the stroke of what is lit.
            edge: ``--hairline-edge``, silhouettes.
            mid: ``--hairline-mid``, every other stroke.
            lo: ``--hairline-lo``, what recedes.
            stroke: ``--hairline-stroke``, stroke width in CSS pixels (default 0.9).
            palette: ``"light"``, ``"dark"``, ``"radix"``, ``"radix-accent"`` or a dict (see :func:`tokens`).
            **props: Props, events and styles.

        Returns:
            The component.
        """
        shortcuts = {"plate": plate, "hi": hi, "edge": edge, "mid": mid, "lo": lo, "stroke": stroke, "palette": palette}
        props.update({k: v for k, v in shortcuts.items() if v is not None})
        props = _merge_theme_kwargs(props)
        return super().create(**props)

    @classmethod
    def info(cls) -> FigureInfo | None:
        """The catalogue entry of this figure, or None for the generic ones.

        Returns:
            Its :class:`FigureInfo`.
        """
        return BY_ID.get(cls._figure_id) if cls._figure_id else None


# Explicit class statements (not a loop) so editors and the generated .pyi see every name.
class Riffle(HairlineBase):
    """A tray of eight cards. The card under the pointer stands up; the arrow keys walk the cards. Higher intensity spreads the ripple further."""

    tag = "Riffle"
    _figure_id = "riffle"


class Terrain(HairlineBase):
    """Eighty-one pillars on a plinth that rise around the pointer. Higher intensity widens the area that rises."""

    tag = "Terrain"
    _figure_id = "terrain"


class Exploded(HairlineBase):
    """An app window in four layers. Moving across opens the gap; moving down picks a layer. Higher intensity opens the layers further."""

    tag = "Exploded"
    _figure_id = "exploded"


class Phosphor(HairlineBase):
    """A dot matrix that plays a loop and fades like phosphor where the pointer paints it. Higher intensity makes the trail linger."""

    tag = "Phosphor"
    _figure_id = "phosphor"


class Slow(HairlineBase):
    """Crates riding a belt through a gate. Hovering slows the clock without stopping it. Higher intensity slows it more."""

    tag = "Slow"
    _figure_id = "slow"


class Turntable(HairlineBase):
    """Blocks on a turntable. A flick spins it; it settles on the nearest quarter turn. Higher intensity makes the spin coast longer."""

    tag = "Turntable"
    _figure_id = "turntable"


class Keyboard(HairlineBase):
    """A sixty-key board. The key under the pointer sinks and its neighbours follow. Higher intensity sinks a wider patch."""

    tag = "Keyboard"
    _figure_id = "keyboard"


class Elevator(HairlineBase):
    """Four floors beside an open shaft. The pointer's height picks a floor; the car travels there. Higher intensity makes it faster."""

    tag = "Elevator"
    _figure_id = "elevator"


class Phone(HairlineBase):
    """A phone in layers: glass, board, battery, shell. Moving across opens the gap; moving down picks a layer."""

    tag = "Phone"
    _figure_id = "phone"


class Laptop(HairlineBase):
    """A thin laptop. The pointer's height sets the lid; it follows on a spring. Higher intensity opens the lid wider."""

    tag = "Laptop"
    _figure_id = "laptop"


class Terminal(HairlineBase):
    """A terminal window. The pointer's height scrolls back; the line under it lifts. Higher intensity spreads the lift."""

    tag = "Terminal"
    _figure_id = "terminal"


class Cabinet(HairlineBase):
    """A rack of twelve blades. The pointer's height pulls the nearest ones out. Higher intensity pulls out more blades."""

    tag = "Cabinet"
    _figure_id = "cabinet"


class Branches(HairlineBase):
    """A commit graph. The commit under the pointer rises, and its history rises after it. Higher intensity raises more history."""

    tag = "Branches"
    _figure_id = "branches"


class Vault(HairlineBase):
    """A vault door. Circling the pointer turns the dial; on the combination the bolts draw back. Higher intensity coasts longer."""

    tag = "Vault"
    _figure_id = "vault"


class Lockers(HairlineBase):
    """A bank of twelve lockers, one ajar at rest. The locker under the pointer opens. Higher intensity opens the door wider."""

    tag = "Lockers"
    _figure_id = "lockers"


class Padlock(HairlineBase):
    """A padlock. As the pointer nears, the shackle lifts out and swings open. Higher intensity swings it further."""

    tag = "Padlock"
    _figure_id = "padlock"


class Patch(HairlineBase):
    """A patch panel of twenty-four ports. The cable under the pointer lifts; neighbours lean away. Higher intensity spreads the lean."""

    tag = "Patch"
    _figure_id = "patch"


class Dish(HairlineBase):
    """A parabolic dish on a two-axis gimbal. The pointer aims it; it follows on a spring. Higher intensity swings it further."""

    tag = "Dish"
    _figure_id = "dish"


class Router(HairlineBase):
    """A router whose antennas lean toward the pointer, the nearest most. Higher intensity spreads the lean."""

    tag = "Router"
    _figure_id = "router"


class Loupe(HairlineBase):
    """A stand loupe on a blank ruled sheet. The pointer drags it across. Higher intensity magnifies more."""

    tag = "Loupe"
    _figure_id = "loupe"


class Sieve(HairlineBase):
    """Three test sieves over a pan. The pointer's height picks one; it rises clear. Higher intensity opens the gap further."""

    tag = "Sieve"
    _figure_id = "sieve"


class Rail(HairlineBase):
    """A garment rail with seven bare hangers. The pointer brushes them; each rocks away. Higher intensity reaches more hangers."""

    tag = "Rail"
    _figure_id = "rail"


class Plug(HairlineBase):
    """A wall socket and a plug on the floor. The pointer draws the plug up; it stops short. Higher intensity brings it closer."""

    tag = "Plug"
    _figure_id = "plug"


class Query(HairlineBase):
    """A question mark as a bent bar over a loose ball. The hook turns toward the pointer. Higher intensity turns it further."""

    tag = "Query"
    _figure_id = "query"


class Drawer(HairlineBase):
    """A cabinet of three drawers. The pointer's height picks one; it slides out, empty. Higher intensity opens it further."""

    tag = "Drawer"
    _figure_id = "drawer"


class Basket(HairlineBase):
    """A wire basket under a bail handle. It tilts toward the pointer. Higher intensity tilts it further."""

    tag = "Basket"
    _figure_id = "basket"


class Plot(HairlineBase):
    """A bar chart with seven flat tabs. The pointer brushes them; each lifts and drops back. Higher intensity lifts them higher."""

    tag = "Plot"
    _figure_id = "plot"


FIGURE_CLASSES: dict[str, type[HairlineBase]] = {
    "riffle": Riffle, "terrain": Terrain, "exploded": Exploded, "phosphor": Phosphor,
    "slow": Slow, "turntable": Turntable, "keyboard": Keyboard, "elevator": Elevator,
    "phone": Phone, "laptop": Laptop, "terminal": Terminal, "cabinet": Cabinet,
    "branches": Branches, "vault": Vault, "lockers": Lockers, "padlock": Padlock,
    "patch": Patch, "dish": Dish, "router": Router, "loupe": Loupe, "sieve": Sieve,
    "rail": Rail, "plug": Plug, "query": Query, "drawer": Drawer, "basket": Basket,
    "plot": Plot,
}  # fmt: skip
"""Every packaged figure's component class, by id."""

assert set(FIGURE_CLASSES) == set(FIGURE_IDS), "catalogue and classes disagree"


# --------------------------------------------------------------------------- #
# The wrapper module: runtime-picked figures and skill-made figures           #
# --------------------------------------------------------------------------- #


def _wrapper_module() -> str:
    """Link the JS wrapper (and the kernel it lazy-loads) into the app and return its import path."""
    rx.asset("hairline_kernel.js", shared=True)
    return rx.asset("hairline_reflex.js", shared=True).importable_path


class _WrapperComponent(HairlineBase):
    """A component whose React tag lives in this package's ``hairline_reflex.js``."""

    library = None

    lib_dependencies: list[str] = [HAIRLINE_NPM]

    def add_imports(self) -> dict[str, Any]:
        """Import the tag from the wrapper module linked into the app's assets.

        Returns:
            The import dict.
        """
        return {_wrapper_module(): ImportVar(tag=self.tag)}


class HairlineFigure(_WrapperComponent):
    """Any of the twenty-seven figures, chosen by id at runtime.

    Changing ``figure`` remounts the drawing. An unknown id falls back to
    ``fallback`` (``"terrain"`` by default).
    """

    tag = "HairlineFigure"

    # The figure id: "terrain", "riffle", ... (see FIGURE_IDS). Can be a state var.
    figure: rx.Var[str]

    # The figure drawn when `figure` is not a known id.
    fallback: rx.Var[str]


class HairlineCustom(_WrapperComponent):
    """A figure made with the ``hairline-create`` skill, mounted natively.

    Point ``src`` at the skill's output, a ``hairline-<name>.html`` page or its
    ``<name>.js`` figure file, placed in the app's ``assets/`` folder (so
    ``src="/hairline-funnel.html"``). Or pass the figure's JavaScript as
    ``code``. The figure runs on the same kernel the skill builds on, and takes
    the same ``intensity``, ``theme``, ``label`` and ``on_read`` as the
    packaged ones; ``intensity`` is mapped onto the figure's declared ``range``.

    The figure's code is executed in the page, so only load figures you trust.
    """

    tag = "HairlineCustom"

    # URL of a skill-made figure: a hairline-<name>.html page or a <name>.js file.
    src: rx.Var[str]

    # The figure's JavaScript (or the whole HTML page), instead of `src`.
    code: rx.Var[str]

    # Fired once the figure is mounted, with {name, means, rules, range} as it declared them.
    on_load: rx.EventHandler[passthrough_event_spec(dict[str, Any])]

    # Fired with a message when the figure cannot be loaded or mounted.
    on_error: rx.EventHandler[passthrough_event_spec(str)]


# --------------------------------------------------------------------------- #
# Patterns                                                                    #
# --------------------------------------------------------------------------- #


def empty_state(
    figure_id: str | rx.Var[str] = "sieve",
    title: str | rx.Component = "Nothing here yet",
    description: str | rx.Component | None = None,
    *actions: rx.Component,
    width: str = "200px",
    label: str | None = None,
    intensity: float | rx.Var[float] | None = None,
    **props: Any,
) -> rx.Component:
    """A figure used as empty-state art: small, above a heading and one action.

    Hairline's docs recommend 160 to 240px; the rest pose is the picture.

    Args:
        figure_id: The figure id (``"sieve"``, ``"drawer"``, ``"basket"``...).
        title: The heading.
        description: An optional line under the heading.
        *actions: Buttons or links under the text (one is best).
        width: The figure's width.
        label: Accessible name for the figure.
        intensity: Optional intensity.
        **props: Passed to the outer ``rx.vstack``.

    Returns:
        The empty state.
    """
    figure_props: dict[str, Any] = {"width": width, "max_width": "100%"}
    if label is not None:
        figure_props["label"] = label
    if intensity is not None:
        figure_props["intensity"] = intensity
    if isinstance(figure_id, str) and figure_id in FIGURE_CLASSES:
        art = FIGURE_CLASSES[figure_id].create(**figure_props)
    else:
        art = HairlineFigure.create(figure=figure_id, **figure_props)
    head = rx.heading(title, size="4", weight="medium") if isinstance(title, str) else title
    body = (
        [rx.text(description, size="2", color_scheme="gray", align="center")]
        if isinstance(description, str)
        else ([description] if description is not None else [])
    )
    props.setdefault("align", "center")
    props.setdefault("spacing", "3")
    props.setdefault("padding", "2em")
    return rx.vstack(art, head, *body, *actions, **props)


# --------------------------------------------------------------------------- #
# Namespace                                                                   #
# --------------------------------------------------------------------------- #


class Hairline(rx.ComponentNamespace):
    """``hairline.terrain(...)``, ``hairline.figure(figure=...)``, ``hairline.custom(src=...)``."""

    riffle = staticmethod(Riffle.create)
    terrain = staticmethod(Terrain.create)
    exploded = staticmethod(Exploded.create)
    phosphor = staticmethod(Phosphor.create)
    slow = staticmethod(Slow.create)
    turntable = staticmethod(Turntable.create)
    keyboard = staticmethod(Keyboard.create)
    elevator = staticmethod(Elevator.create)
    phone = staticmethod(Phone.create)
    laptop = staticmethod(Laptop.create)
    terminal = staticmethod(Terminal.create)
    cabinet = staticmethod(Cabinet.create)
    branches = staticmethod(Branches.create)
    vault = staticmethod(Vault.create)
    lockers = staticmethod(Lockers.create)
    padlock = staticmethod(Padlock.create)
    patch = staticmethod(Patch.create)
    dish = staticmethod(Dish.create)
    router = staticmethod(Router.create)
    loupe = staticmethod(Loupe.create)
    sieve = staticmethod(Sieve.create)
    rail = staticmethod(Rail.create)
    plug = staticmethod(Plug.create)
    query = staticmethod(Query.create)
    drawer = staticmethod(Drawer.create)
    basket = staticmethod(Basket.create)
    plot = staticmethod(Plot.create)

    figure = staticmethod(HairlineFigure.create)
    custom = staticmethod(HairlineCustom.create)
    empty_state = staticmethod(empty_state)
    tokens = staticmethod(tokens)

    FIGURES = FIGURES
    FIGURE_IDS = FIGURE_IDS
    BY_ID = BY_ID
    LIGHT = LIGHT
    DARK = DARK
    RADIX_TOKENS = RADIX_TOKENS
    RADIX_ACCENT_TOKENS = RADIX_ACCENT_TOKENS

    __call__ = staticmethod(HairlineFigure.create)


hairline = Hairline()

# snake_case factories, for `from reflex_hairline import terrain`
riffle = Riffle.create
terrain = Terrain.create
exploded = Exploded.create
phosphor = Phosphor.create
slow = Slow.create
turntable = Turntable.create
keyboard = Keyboard.create
elevator = Elevator.create
phone = Phone.create
laptop = Laptop.create
terminal = Terminal.create
cabinet = Cabinet.create
branches = Branches.create
vault = Vault.create
lockers = Lockers.create
padlock = Padlock.create
patch = Patch.create
dish = Dish.create
router = Router.create
loupe = Loupe.create
sieve = Sieve.create
rail = Rail.create
plug = Plug.create
query = Query.create
drawer = Drawer.create
basket = Basket.create
plot = Plot.create
figure = HairlineFigure.create
custom = HairlineCustom.create

__all__ = [
    "BY_ID",
    "DARK",
    "FIGURES",
    "FIGURE_CLASSES",
    "FIGURE_IDS",
    "HAIRLINE_NPM",
    "HAIRLINE_VERSION",
    "LIGHT",
    "PALETTES",
    "RADIX_ACCENT_TOKENS",
    "RADIX_TOKENS",
    "Basket",
    "Branches",
    "Cabinet",
    "Dish",
    "Drawer",
    "Elevator",
    "Exploded",
    "FigureInfo",
    "Hairline",
    "HairlineBase",
    "HairlineCustom",
    "HairlineFigure",
    "Keyboard",
    "Laptop",
    "Lockers",
    "Loupe",
    "Padlock",
    "Patch",
    "Phone",
    "Phosphor",
    "Plot",
    "Plug",
    "Query",
    "Rail",
    "Riffle",
    "Router",
    "Sieve",
    "Slow",
    "Terminal",
    "Terrain",
    "Turntable",
    "Vault",
    "basket",
    "branches",
    "cabinet",
    "custom",
    "dish",
    "drawer",
    "elevator",
    "empty_state",
    "exploded",
    "figure",
    "hairline",
    "keyboard",
    "laptop",
    "lockers",
    "loupe",
    "padlock",
    "patch",
    "phone",
    "phosphor",
    "plot",
    "plug",
    "query",
    "rail",
    "riffle",
    "router",
    "sieve",
    "slow",
    "terminal",
    "terrain",
    "tokens",
    "turntable",
    "vault",
]  # fmt: skip
