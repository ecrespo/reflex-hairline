"""State for the reflex-hairline demo."""

from __future__ import annotations

from typing import Any

import reflex as rx

from reflex_hairline import BY_ID, FIGURE_IDS

PALETTE_CHOICES = ["hairline", "radix", "radix-accent", "custom"]

SKILL_EXAMPLES: list[dict[str, str]] = [
    {"file": "hairline-funnel.html", "idea": "a sales funnel"},
    {"file": "hairline-clearance.html", "idea": "a rate limiter"},
    {"file": "hairline-sidings.html", "idea": "git branches"},
    {"file": "hairline-storm.html", "idea": "weather over a city"},
]


def _first(value: Any) -> float:
    """A slider sends a list of numbers; take the first."""
    if isinstance(value, (list, tuple)):
        value = value[0] if value else 0
    return float(value)


class DemoState(rx.State):
    """Shared controls: the intensity and theme every page reads."""

    intensity: float = 0.5
    theme: str = "auto"

    @rx.event
    def set_intensity(self, value: list[float] | float):
        self.intensity = round(_first(value), 2)

    @rx.event
    def set_theme(self, value: str | list[str]):
        self.theme = value if value in ("auto", "light", "dark") else "auto"


class GalleryState(rx.State):
    """The captions each figure on the gallery reports through on_read."""

    captions: dict[str, str] = {}

    @rx.event
    def read(self, figure_id: str, text: str):
        self.captions[figure_id] = text


class PlaygroundState(rx.State):
    """One figure under every control the component has."""

    figure: str = "terrain"
    caption: str = "rest"
    reads: int = 0
    palette: str = "hairline"
    stroke: float = 0.9
    width: int = 520
    plate: str = "#ffffff"
    hi: str = "#232327"
    edge: str = "#a4a4ac"
    mid: str = "#c3c3c9"
    lo: str = "#e0e0e4"

    @rx.event
    def pick(self, value: str):
        if value in FIGURE_IDS:
            self.figure = value
            self.caption = "rest"
            self.reads = 0

    @rx.event
    def step(self, delta: int):
        i = FIGURE_IDS.index(self.figure)
        self.pick(FIGURE_IDS[(i + delta) % len(FIGURE_IDS)])

    @rx.event
    def read(self, text: str):
        self.caption = text
        self.reads += 1

    @rx.event
    def set_palette(self, value: str | list[str]):
        self.palette = value

    @rx.event
    def set_stroke(self, value: list[float] | float):
        self.stroke = round(_first(value), 2)

    @rx.event
    def set_width(self, value: list[float] | float):
        self.width = int(_first(value))

    @rx.event
    def set_color(self, key: str, value: str):
        if key in ("plate", "hi", "edge", "mid", "lo"):
            setattr(self, key, value)

    @rx.event
    def reset_colors(self, dark: bool):
        src = (
            {"plate": "#08090a", "hi": "#d0d6e0", "edge": "#5b5d64", "mid": "#3e3e44", "lo": "#29292d"}
            if dark
            else {"plate": "#ffffff", "hi": "#232327", "edge": "#a4a4ac", "mid": "#c3c3c9", "lo": "#e0e0e4"}
        )
        for k, v in src.items():
            setattr(self, k, v)

    @rx.var
    def info(self) -> dict[str, str]:
        meta = BY_ID[self.figure]
        return {
            "name": meta.name,
            "summary": meta.summary,
            "stronger": meta.stronger,
            "parameter": meta.parameter,
            "unit": meta.unit,
            "lo": f"{meta.range[0]:g}",
            "mid": f"{meta.range[1]:g}",
            "hi": f"{meta.range[2]:g}",
        }

    @rx.var
    def tok(self) -> dict[str, str]:
        """The five colours and the stroke, as the figure's theme kwargs. "initial" leaves one unset."""
        out = {k: "initial" for k in ("plate", "hi", "edge", "mid", "lo")}
        if self.palette in ("radix", "radix-accent"):
            from reflex_hairline import PALETTES

            out.update({k.removeprefix("--hairline-"): v for k, v in PALETTES[self.palette].items()})
        elif self.palette == "custom":
            out.update(plate=self.plate, hi=self.hi, edge=self.edge, mid=self.mid, lo=self.lo)
        out["stroke"] = str(self.stroke)
        return out

    @rx.var
    def plate_background(self) -> str:
        if self.palette == "custom":
            return self.plate
        if self.palette in ("radix", "radix-accent"):
            return "var(--color-panel-solid)"
        return "transparent"


class PlaygroundCode(rx.State):
    """The Python snippet for what the playground shows."""

    @rx.var
    async def snippet(self) -> str:
        pg = await self.get_state(PlaygroundState)
        demo = await self.get_state(DemoState)
        args = [f"intensity={demo.intensity:g}"]
        if demo.theme != "auto":
            args.append(f'theme="{demo.theme}"')
        if pg.palette in ("radix", "radix-accent"):
            args.append(f'palette="{pg.palette}"')
        elif pg.palette == "custom":
            args += [f'plate="{pg.plate}"', f'hi="{pg.hi}"', f'edge="{pg.edge}"', f'mid="{pg.mid}"', f'lo="{pg.lo}"']
        if pg.stroke != 0.9:
            args.append(f"stroke={pg.stroke:g}")
        args.append(f'width="{pg.width}px"')
        args.append("on_read=State.set_caption")
        body = ",\n    ".join(args)
        return f"from reflex_hairline import hairline\n\nhairline.{pg.figure}(\n    {body},\n)"


class SkillState(rx.State):
    """Figures made with the hairline-create skill, loaded through hairline.custom."""

    selected: str = SKILL_EXAMPLES[0]["file"]
    declared: dict[str, Any] = {}
    caption: str = "rest"
    error: str = ""
    pasted: str = ""
    pasted_code: str = ""

    @rx.event
    def select(self, file: str):
        self.selected = file
        self.declared = {}
        self.caption = "rest"
        self.error = ""

    @rx.event
    def loaded(self, spec: dict[str, Any]):
        self.declared = spec
        self.error = ""

    @rx.event
    def failed(self, message: str):
        self.error = message

    @rx.event
    def read(self, text: str):
        self.caption = text

    @rx.event
    def set_pasted(self, value: str):
        self.pasted = value

    @rx.event
    def mount_pasted(self):
        self.pasted_code = self.pasted

    @rx.var
    def src(self) -> str:
        return f"/skill/{self.selected}"

    @rx.var
    def idea(self) -> str:
        for e in SKILL_EXAMPLES:
            if e["file"] == self.selected:
                return e["idea"]
        return ""

    @rx.var
    def rules_text(self) -> str:
        names = ["hit", "order", "reach", "accent", "rest", "honesty", "cost", "clock", "radius", "quiet"]
        rules = self.declared.get("rules") or []
        return " · ".join(f"{int(n):02d} {names[int(n) - 1]}" for n in rules if 1 <= int(n) <= 10)

    @rx.var
    def range_text(self) -> str:
        r = self.declared.get("range") or []
        return " → ".join(f"{float(x):g}" for x in r)


class EmptyState(rx.State):
    """The empty-state examples' buttons."""

    cleared: int = 0

    @rx.event
    def act(self, what: str):
        self.cleared += 1
        return rx.toast(what)
