"""The catalogue of Hairline figures: names, copy and the intensity map.

Generated from @lucasmarkes/hairline 0.3.0 (packages/hairline/src/index.ts and
src/intensity.ts) and the site's apps/site/lib/figures.ts. Keep it in sync when
the npm package adds figures.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class FigureInfo:
    """What one figure is and what `intensity` does to it."""

    id: str
    """The lowercase id, as the vanilla function is named (``"terrain"``)."""
    name: str
    """The React component name (``"Terrain"``)."""
    summary: str
    """One or two sentences on what the figure shows and how it answers."""
    stronger: str
    """What a higher ``intensity`` does to this figure."""
    label: str
    """The default accessible name the figure gives itself."""
    rest: str
    """The caption ``on_read`` reports at rest."""
    parameter: str
    """The number ``intensity`` drives inside the figure."""
    unit: str
    """The unit of that number."""
    range: tuple[float, float, float]
    """The parameter at intensity 0, 0.5 and 1."""

    def parameter_at(self, intensity: float) -> float:
        """The figure's own number for an intensity, as the package computes it."""
        lo, mid, hi = self.range
        try:
            i = float(intensity)
        except (TypeError, ValueError):
            i = 0.5
        if math.isnan(i):
            i = 0.5
        i = min(1.0, max(0.0, i))
        v = lo + (i / 0.5) * (mid - lo) if i <= 0.5 else mid + ((i - 0.5) / 0.5) * (hi - mid)
        return round(v * 1000) / 1000


FIGURES: tuple[FigureInfo, ...] = (
    FigureInfo(
        id="riffle",
        name="Riffle",
        summary="A tray of eight cards. The card under the pointer stands up and its neighbours lean after it. The arrow keys walk the cards.",
        stronger="The ripple spreads further from the pulled card.",
        label="A tray of eight cards. Hover or use the arrow keys to pull a card.",
        rest="rest",
        parameter="stagger",
        unit="ms",
        range=(0.0, 40.0, 90.0),
    ),
    FigureInfo(
        id="terrain",
        name="Terrain",
        summary="Eighty-one pillars on a plinth. They rise around the pointer and settle back into a dune with two rises.",
        stronger="A wider area rises.",
        label="Eighty-one pillars on a plinth that rise around the pointer and rest as a dune with two rises.",
        rest="rest",
        parameter="radius",
        unit="cells",
        range=(1.5, 3.0, 5.0),
    ),
    FigureInfo(
        id="exploded",
        name="Exploded",
        summary="An app window taken apart into four layers. Moving across opens the gap; moving down picks a layer.",
        stronger="The layers open further.",
        label="An app window taken apart into four layers. Moving across opens the gap; moving down picks a layer.",
        rest="",
        parameter="gap",
        unit="viewBox units",
        range=(12.0, 28.0, 40.0),
    ),
    FigureInfo(
        id="phosphor",
        name="Phosphor",
        summary="A seven by seven dot matrix playing a loop. Where the pointer paints, the dots fade like phosphor.",
        stronger="The trail lingers longer.",
        label="A seven by seven dot matrix on a floating tile that plays a loop, and fades like phosphor where you paint it.",
        rest="loop",
        parameter="afterglow",
        unit="ms",
        range=(150.0, 520.0, 1500.0),
    ),
    FigureInfo(
        id="slow",
        name="Slow",
        summary="Crates riding a belt through a gate. Hovering slows the clock without stopping it.",
        stronger="Time slows down more.",
        label="Crates riding a belt through a gate. Hovering slows the clock without stopping it.",
        rest="rate 1.00×",
        parameter="rate",
        unit="× normal speed",
        range=(0.6, 0.2, 0.05),
    ),
    FigureInfo(
        id="turntable",
        name="Turntable",
        summary="Blocks on a turntable. A flick across it spins it, and it settles on the nearest quarter turn.",
        stronger="The spin coasts longer.",
        label="Blocks on a turntable. Flick across it to spin it; it settles on the nearest quarter turn.",
        rest="az 045° · el 30°",
        parameter="coast",
        unit="ms",
        range=(200.0, 650.0, 1500.0),
    ),
    FigureInfo(
        id="keyboard",
        name="Keyboard",
        summary="Sixty keys in a block. The key under the pointer sinks and its neighbours follow it down, less the further away.",
        stronger="A wider patch of keys sinks.",
        label="A sixty-key board. The key under the pointer sinks, and its neighbours follow it down, less the further away.",
        rest="rest",
        parameter="radius",
        unit="keys",
        range=(1.0, 2.0, 3.5),
    ),
    FigureInfo(
        id="elevator",
        name="Elevator",
        summary="Four floors with the shaft open and the car inside. The pointer's height picks the floor; the car travels there.",
        stronger="The car travels faster between floors.",
        label="Four floors beside an open shaft. The pointer's height picks a floor, and the car travels there through the ones between.",
        rest="rest",
        parameter="stiffness",
        unit="spring units",
        range=(40.0, 100.0, 220.0),
    ),
    FigureInfo(
        id="phone",
        name="Phone",
        summary="A phone in layers: glass, board, battery, shell. Moving across opens the gap; moving down picks a layer.",
        stronger="The layers open further.",
        label="A phone in layers: glass, board, battery, shell. Moving across opens the gap; moving down picks a layer.",
        rest="rest",
        parameter="gap",
        unit="viewBox units",
        range=(16.0, 28.0, 40.0),
    ),
    FigureInfo(
        id="laptop",
        name="Laptop",
        summary="A thin laptop, open on its hinge. The pointer's height sets the lid; it follows on a spring.",
        stronger="The lid opens wider.",
        label="A thin laptop: the pointer's height sets how far the lid stands open, and the lid follows it on a spring.",
        rest="rest",
        parameter="lid",
        unit="degrees",
        range=(100.0, 125.0, 150.0),
    ),
    FigureInfo(
        id="terminal",
        name="Terminal",
        summary="A terminal window with its history in rows. The pointer's height scrolls back; the line under it lifts and its neighbours follow.",
        stronger="The lift spreads further.",
        label="A terminal window: the pointer's height scrolls back through its history, and the line under it lifts off the screen.",
        rest="rest",
        parameter="spread",
        unit="lines",
        range=(1.0, 2.0, 3.5),
    ),
    FigureInfo(
        id="cabinet",
        name="Cabinet",
        summary="A rack of twelve blades, a few half out. The pointer's height pulls the nearest ones out, the farther the less.",
        stronger="More blades come out.",
        label="A rack of twelve blades: the pointer's height pulls the nearest ones out on their rails, the farther the less.",
        rest="rest",
        parameter="reach",
        unit="blades",
        range=(1.5, 3.0, 5.0),
    ),
    FigureInfo(
        id="branches",
        name="Branches",
        summary="A commit graph with a branch forking off main and merging back. The commit under the pointer rises, and its history rises after it.",
        stronger="More of the history rises.",
        label="A commit graph on a board: the commit under the pointer rises, and its history rises after it, the farther back the less.",
        rest="rest",
        parameter="reach",
        unit="commits",
        range=(1.0, 3.0, 6.0),
    ),
    FigureInfo(
        id="vault",
        name="Vault",
        summary="A vault door with a dial and three bolts. The pointer turns the dial; detents catch every ten, and on the combination the bolts draw back.",
        stronger="The dial coasts longer.",
        label="A vault door: circling the pointer turns its dial, which coasts and catches every ten; on forty its three bolts draw back.",
        rest="rest",
        parameter="coast",
        unit="ms",
        range=(250.0, 600.0, 1500.0),
    ),
    FigureInfo(
        id="lockers",
        name="Lockers",
        summary="A bank of twelve lockers, one ajar at rest. The locker under the pointer opens; the one at rest closes.",
        stronger="The door opens wider.",
        label="A bank of twelve lockers, one ajar at rest: the locker under the pointer opens, and the one open before it swings shut.",
        rest="rest",
        parameter="opening",
        unit="degrees",
        range=(55.0, 90.0, 120.0),
    ),
    FigureInfo(
        id="padlock",
        name="Padlock",
        summary="A padlock with its shackle in. As the pointer comes near the shackle lifts out and swings open.",
        stronger="The shackle swings further.",
        label="A padlock: as the pointer nears, the shackle springs up out of the body and swings open about its long leg.",
        rest="rest",
        parameter="swing",
        unit="degrees",
        range=(45.0, 90.0, 100.0),
    ),
    FigureInfo(
        id="patch",
        name="Patch",
        summary="A patch panel of twenty-four ports with cables. The cable under the pointer lifts and its neighbours lean away.",
        stronger="The lean spreads further.",
        label="A patch panel of twenty-four ports: the cable under the pointer lifts, and its neighbours lean away, less the further away.",
        rest="rest",
        parameter="radius",
        unit="ports",
        range=(1.0, 2.5, 5.0),
    ),
    FigureInfo(
        id="dish",
        name="Dish",
        summary="A parabolic dish on a two-axis gimbal. The pointer aims the dish; it follows on a spring.",
        stronger="The dish swings further.",
        label="A parabolic dish on a two-axis gimbal: the pointer aims it, and it follows on a spring.",
        rest="rest",
        parameter="reach",
        unit="degrees",
        range=(30.0, 50.0, 70.0),
    ),
    FigureInfo(
        id="router",
        name="Router",
        summary="A router with its antennas up. Each antenna leans toward the pointer, the nearest most.",
        stronger="The lean spreads further.",
        label="A wifi router whose antennas lean toward the pointer, the nearest the most and the others less the further away.",
        rest="rest",
        parameter="spread",
        unit="antennas",
        range=(0.5, 1.5, 3.0),
    ),
    FigureInfo(
        id="loupe",
        name="Loupe",
        summary="A stand loupe on a blank ruled sheet. The pointer drags it across; the rules pass enlarged under the glass, with nothing between them.",
        stronger="The glass magnifies more.",
        label="A stand loupe over a blank ruled sheet: the pointer drags it across, and the rules pass enlarged under the glass with nothing between them.",
        rest="rest",
        parameter="magnification",
        unit="×",
        range=(1.3, 1.8, 2.6),
    ),
    FigureInfo(
        id="sieve",
        name="Sieve",
        summary="Three test sieves stacked over a pan. The pointer's height picks one; it rises clear of the stack, and every mesh is bare.",
        stronger="The gap opens further.",
        label="Three test sieves stacked over a pan: the pointer's height picks one, it rises clear of the stack, and every mesh is bare.",
        rest="rest",
        parameter="gap",
        unit="viewBox units",
        range=(6.0, 14.0, 24.0),
    ),
    FigureInfo(
        id="rail",
        name="Rail",
        summary="A garment rail with seven bare hangers. The pointer brushes them; each rocks away, the nearest most, and settles.",
        stronger="The brush reaches more hangers.",
        label="A garment rail with seven bare hangers: the pointer brushes them, and each rocks away from it, the nearest most, and settles.",
        rest="rest",
        parameter="radius",
        unit="hangers",
        range=(1.0, 2.0, 3.5),
    ),
    FigureInfo(
        id="plug",
        name="Plug",
        summary="A wall socket, and a plug lying on the floor at the end of its cord. The pointer draws the plug up toward the socket; it stops short, and falls back.",
        stronger="The plug comes closer to the socket.",
        label="A wall socket and a plug lying on the floor at the end of its cord: the pointer draws the plug up toward the socket, and it stops short of it.",
        rest="rest",
        parameter="pull",
        unit="of the way",
        range=(0.35, 0.6, 0.9),
    ),
    FigureInfo(
        id="query",
        name="Query",
        summary="A question mark built as a bent bar over a loose ball. The hook turns toward the pointer, and the ball rolls after it.",
        stronger="The hook turns further.",
        label="A question mark built as a solid on a plinth, its dot a loose ball: the hook turns about its stem toward the pointer, and the ball rolls after it.",
        rest="rest",
        parameter="turn",
        unit="degrees",
        range=(20.0, 40.0, 55.0),
    ),
    FigureInfo(
        id="drawer",
        name="Drawer",
        summary="A cabinet of three drawers. The pointer's height picks one; it slides out and shows two dividers with nothing between them.",
        stronger="The drawer opens further.",
        label="A filing cabinet of three drawers: the pointer's height picks one, it slides out, and inside are two dividers and nothing between them.",
        rest="rest",
        parameter="pull",
        unit="viewBox units",
        range=(12.0, 22.0, 34.0),
    ),
    FigureInfo(
        id="basket",
        name="Basket",
        summary="A wire basket under a bail handle. It tilts toward the pointer and shows its bare floor; the handle swings after it.",
        stronger="The basket tilts further.",
        label="An empty wire shopping basket under a bail handle: the pointer tilts it toward itself on a spring, so the bare floor shows, and the handle swings after it, late.",
        rest="rest",
        parameter="tilt",
        unit="degrees",
        range=(8.0, 16.0, 28.0),
    ),
    FigureInfo(
        id="plot",
        name="Plot",
        summary="A bar chart with seven flat tabs where the bars would stand. The pointer brushes them; each lifts a little and drops back to zero.",
        stronger="The tabs lift higher.",
        label="A bar chart with no data: seven flat tabs on its base, before a plate of grid lines. The pointer brushes them, and each lifts a little, the nearest most, and drops back to zero.",
        rest="rest",
        parameter="lift",
        unit="viewBox units",
        range=(3.0, 6.0, 12.0),
    ),
)

FIGURE_IDS: tuple[str, ...] = tuple(f.id for f in FIGURES)
"""Every figure id, in the order the docs list them."""

BY_ID: dict[str, FigureInfo] = {f.id: f for f in FIGURES}
"""Figure metadata by id."""
