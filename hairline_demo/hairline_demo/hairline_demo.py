"""reflex-hairline demo: every figure, every option, theming, empty states and skill-made figures."""

from __future__ import annotations

import reflex as rx

from reflex_hairline import BY_ID, FIGURE_IDS, FIGURES, hairline

from .state import (
    PALETTE_CHOICES,
    SKILL_EXAMPLES,
    DemoState,
    EmptyState,
    GalleryState,
    PlaygroundCode,
    PlaygroundState,
    SkillState,
)

MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

NAV = [
    ("Gallery", "/"),
    ("Playground", "/playground"),
    ("Theming", "/theming"),
    ("Empty states", "/empty-states"),
    ("Skill figures", "/skill"),
    ("Reference", "/reference"),
]


# --------------------------------------------------------------------------- #
# Chrome                                                                      #
# --------------------------------------------------------------------------- #


def mono(text, **props) -> rx.Component:
    props.setdefault("size", "1")
    return rx.text(text, font_family=MONO, letter_spacing="0.02em", **props)


def nav_link(label: str, href: str) -> rx.Component:
    active = rx.State.router.page.path == href
    return rx.link(
        label,
        href=href,
        size="2",
        underline="none",
        color=rx.cond(active, rx.color("gray", 12), rx.color("gray", 10)),
        weight=rx.cond(active, "medium", "regular"),
        _hover={"color": rx.color("gray", 12)},
        white_space="nowrap",
    )


def controls() -> rx.Component:
    """The intensity slider and theme switch every page shares."""
    return rx.hstack(
        mono("intensity", color=rx.color("gray", 10)),
        rx.slider(
            value=[DemoState.intensity],
            min=0,
            max=1,
            step=0.01,
            on_change=DemoState.set_intensity.throttle(40),
            width="140px",
            size="1",
            color_scheme="gray",
        ),
        mono(DemoState.intensity.to_string(), width="4ch", white_space="nowrap", color=rx.color("gray", 12)),
        rx.segmented_control.root(
            rx.segmented_control.item("auto", value="auto"),
            rx.segmented_control.item("light", value="light"),
            rx.segmented_control.item("dark", value="dark"),
            value=DemoState.theme,
            on_change=DemoState.set_theme,
            size="1",
        ),
        rx.color_mode.button(size="1", variant="ghost"),
        align="center",
        spacing="3",
        wrap="wrap",
    )


def header() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.link(
                    rx.hstack(
                        hairline.terrain(width="34px", intensity=0.9, label="Hairline"),
                        rx.text("reflex-hairline", weight="medium", size="3", color=rx.color("gray", 12)),
                        align="center",
                        spacing="2",
                    ),
                    href="/",
                    underline="none",
                ),
                rx.hstack(*[nav_link(text, href) for text, href in NAV], spacing="4", wrap="wrap"),
                spacing="6",
                align="center",
                wrap="wrap",
            ),
            controls(),
            justify="between",
            align="center",
            wrap="wrap",
            row_gap="3",
            max_width="1180px",
            margin_x="auto",
            padding_x="16px",
            padding_y="12px",
        ),
        position="sticky",
        top="0",
        z_index="10",
        background=rx.color("gray", 1),
        border_bottom=f"1px solid {rx.color('gray', 4)}",
    )


def page(*children: rx.Component, title: str, lede: str | rx.Component) -> rx.Component:
    return rx.box(
        header(),
        rx.box(
            rx.vstack(
                rx.heading(title, size="7", weight="medium", letter_spacing="-0.02em"),
                rx.text(lede, size="3", color=rx.color("gray", 11), max_width="68ch")
                if isinstance(lede, str)
                else lede,
                spacing="2",
                margin_bottom="28px",
            ),
            *children,
            max_width="1180px",
            margin_x="auto",
            padding_x="16px",
            padding_y="32px",
        ),
        rx.box(
            rx.text(
                "Hairline by Lucas Marques (MIT) · ",
                rx.link("hairline.lucasmarkes.com", href="https://hairline.lucasmarkes.com", is_external=True),
                " · Reflex wrapper: reflex-hairline",
                size="1",
                color=rx.color("gray", 9),
            ),
            max_width="1180px",
            margin_x="auto",
            padding="24px 16px 48px",
            border_top=f"1px solid {rx.color('gray', 4)}",
        ),
        background=rx.color("gray", 1),
        min_height="100vh",
    )


def plate(*children: rx.Component, **props) -> rx.Component:
    """A bordered card the figures sit in, like the site's tiles."""
    props.setdefault("border", f"1px solid {rx.color('gray', 4)}")
    props.setdefault("border_radius", "14px")
    props.setdefault("overflow", "hidden")
    props.setdefault("position", "relative")
    props.setdefault("background", rx.color("gray", 1))
    return rx.box(*children, **props)


def code_block(code, language: str = "python") -> rx.Component:
    return rx.code_block(
        code,
        language=language,
        show_line_numbers=False,
        wrap_long_lines=True,
        custom_style={"fontSize": "12.5px", "borderRadius": "10px", "margin": "0"},
        width="100%",
    )


# --------------------------------------------------------------------------- #
# Gallery                                                                     #
# --------------------------------------------------------------------------- #


def gallery_tile(fid: str) -> rx.Component:
    meta = BY_ID[fid]
    return rx.box(
        plate(
            mono(
                meta.name.lower(), position="absolute", top="12px", left="14px", color=rx.color("gray", 10), z_index="1"
            ),
            mono(
                GalleryState.captions.get(fid, meta.rest),
                position="absolute",
                top="12px",
                right="14px",
                color=rx.color("gray", 12),
                z_index="1",
                style={"fontVariantNumeric": "tabular-nums"},
            ),
            hairline.figure(
                figure=fid,
                intensity=DemoState.intensity,
                theme=DemoState.theme,
                on_read=lambda text: GalleryState.read(fid, text),
            ),
            background=rx.cond(
                DemoState.theme == "dark",
                "#08090a",
                rx.cond(DemoState.theme == "light", "#ffffff", rx.color_mode_cond("#ffffff", "#08090a")),
            ),
        ),
        rx.text(meta.summary, size="2", color=rx.color("gray", 11), margin_top="10px", line_height="1.5"),
        rx.text(
            rx.text.strong("Higher intensity: "),
            meta.stronger,
            size="1",
            color=rx.color("gray", 10),
            margin_top="4px",
        ),
    )


def gallery() -> rx.Component:
    return page(
        rx.grid(
            *[gallery_tile(fid) for fid in FIGURE_IDS],
            columns=rx.breakpoints(initial="1", sm="2", lg="3"),
            spacing="6",
        ),
        title="Twenty-seven isometric line figures that answer the pointer",
        lede=(
            "Hairline's figures as Reflex components. Move the pointer over any of them. "
            "The slider in the bar sets intensity for all of them, the switch sets the theme, "
            "and the top-right caption of each tile comes back to Python through on_read."
        ),
    )


# --------------------------------------------------------------------------- #
# Playground                                                                  #
# --------------------------------------------------------------------------- #


def labelled(label: str, *children: rx.Component) -> rx.Component:
    return rx.vstack(mono(label, color=rx.color("gray", 10)), *children, spacing="1", width="100%")


def color_input(key: str) -> rx.Component:
    return rx.hstack(
        rx.el.input(
            type="color",
            value=getattr(PlaygroundState, key),
            on_change=lambda v: PlaygroundState.set_color(key, v),
            style={
                "width": "28px",
                "height": "22px",
                "border": "none",
                "padding": "0",
                "background": "none",
                "cursor": "pointer",
            },
        ),
        mono(f"--hairline-{key}", color=rx.color("gray", 11)),
        align="center",
        spacing="2",
    )


def playground() -> rx.Component:
    figure_box = plate(
        mono(
            PlaygroundState.figure,
            position="absolute",
            top="12px",
            left="14px",
            color=rx.color("gray", 10),
            z_index="1",
        ),
        mono(
            PlaygroundState.caption,
            position="absolute",
            top="12px",
            right="14px",
            z_index="1",
            color=rx.color("gray", 12),
        ),
        rx.center(
            hairline.figure(
                figure=PlaygroundState.figure,
                intensity=DemoState.intensity,
                theme=DemoState.theme,
                on_read=PlaygroundState.read,
                plate=PlaygroundState.tok["plate"],
                hi=PlaygroundState.tok["hi"],
                edge=PlaygroundState.tok["edge"],
                mid=PlaygroundState.tok["mid"],
                lo=PlaygroundState.tok["lo"],
                stroke=PlaygroundState.tok["stroke"],
                width=PlaygroundState.width.to_string() + "px",
                max_width="100%",
            ),
            width="100%",
            padding_y="16px",
        ),
        background=PlaygroundState.plate_background,
        width="100%",
    )
    side = rx.vstack(
        labelled(
            "figure",
            rx.hstack(
                rx.icon_button(
                    rx.icon("chevron-left", size=14), on_click=PlaygroundState.step(-1), variant="soft", size="1"
                ),
                rx.box(
                    rx.select(
                        list(FIGURE_IDS),
                        value=PlaygroundState.figure,
                        on_change=PlaygroundState.pick,
                        size="2",
                        width="100%",
                    ),
                    flex="1",
                    min_width="0",
                ),
                rx.icon_button(
                    rx.icon("chevron-right", size=14), on_click=PlaygroundState.step(1), variant="soft", size="1"
                ),
                width="100%",
                align="center",
            ),
        ),
        rx.box(
            rx.text(PlaygroundState.info["summary"], size="2", color=rx.color("gray", 11)),
            rx.text(
                rx.text.strong("Higher intensity: "),
                PlaygroundState.info["stronger"],
                size="2",
                color=rx.color("gray", 11),
                margin_top="6px",
            ),
            mono(
                PlaygroundState.info["parameter"]
                + ": "
                + PlaygroundState.info["lo"]
                + " → "
                + PlaygroundState.info["mid"]
                + " → "
                + PlaygroundState.info["hi"]
                + " "
                + PlaygroundState.info["unit"],
                margin_top="8px",
                color=rx.color("gray", 10),
            ),
        ),
        rx.separator(),
        labelled(
            "palette",
            rx.segmented_control.root(
                *[rx.segmented_control.item(p.replace("radix-accent", "accent"), value=p) for p in PALETTE_CHOICES],
                value=PlaygroundState.palette,
                on_change=PlaygroundState.set_palette,
                size="1",
                width="100%",
                max_width="100%",
            ),
        ),
        rx.cond(
            PlaygroundState.palette == "custom",
            rx.vstack(
                *[color_input(k) for k in ("plate", "hi", "edge", "mid", "lo")],
                rx.hstack(
                    rx.button("light preset", size="1", variant="soft", on_click=PlaygroundState.reset_colors(False)),
                    rx.button("dark preset", size="1", variant="soft", on_click=PlaygroundState.reset_colors(True)),
                ),
                spacing="2",
            ),
        ),
        labelled(
            "stroke",
            rx.hstack(
                rx.slider(
                    value=[PlaygroundState.stroke],
                    min=0.4,
                    max=2.5,
                    step=0.05,
                    on_change=PlaygroundState.set_stroke.throttle(40),
                    size="1",
                ),
                mono(PlaygroundState.stroke.to_string(), width="4ch"),
                width="100%",
                align="center",
            ),
        ),
        labelled(
            "width",
            rx.hstack(
                rx.slider(
                    value=[PlaygroundState.width],
                    min=160,
                    max=760,
                    step=10,
                    on_change=PlaygroundState.set_width.throttle(40),
                    size="1",
                ),
                mono(PlaygroundState.width.to_string() + "px", width="6ch"),
                width="100%",
                align="center",
            ),
        ),
        rx.separator(),
        labelled(
            "on_read",
            rx.hstack(
                rx.badge(PlaygroundState.caption, variant="surface", size="2", font_family=MONO),
                mono(PlaygroundState.reads.to_string() + " events", color=rx.color("gray", 10)),
                align="center",
            ),
        ),
        spacing="4",
        width="100%",
        min_width="0",
    )
    return page(
        rx.grid(
            rx.vstack(figure_box, code_block(PlaygroundCode.snippet), spacing="4", width="100%"),
            side,
            columns=rx.breakpoints(initial="1", md="minmax(0, 1fr) 320px"),
            spacing="6",
            width="100%",
        ),
        title="Playground",
        lede="One figure, every option. The figure is picked by a state var through hairline.figure(), so switching remounts it; intensity, theme and the palette reach the running figure without a remount.",
    )


# --------------------------------------------------------------------------- #
# Theming                                                                     #
# --------------------------------------------------------------------------- #

SWATCHES = [
    ("Hairline light", "#ffffff", {"palette": "light"}),
    ("Hairline dark", "#08090a", {"palette": "dark"}),
    ("Paper", "#f4efe6", {"plate": "#f4efe6", "hi": "#3b2f20", "edge": "#9b8a72", "mid": "#cbbca3", "lo": "#e4d9c6"}),
    (
        "Blueprint",
        "#0d2a4a",
        {"plate": "#0d2a4a", "hi": "#e8f1ff", "edge": "#7fa6d6", "mid": "#3f6a9c", "lo": "#1e4370", "stroke": 1.1},
    ),
    (
        "Terminal",
        "#05140b",
        {"plate": "#05140b", "hi": "#7dffb0", "edge": "#2f9e62", "mid": "#1c5e3a", "lo": "#123d27"},
    ),
    ("Heavy ink", "#ffffff", {"palette": "light", "stroke": 1.8}),
]

ACCENTS = ["iris", "crimson", "jade", "amber", "cyan", "plum"]


def theming() -> rx.Component:
    swatch_tiles = [
        rx.box(
            plate(
                hairline.figure(figure=FIGURE_IDS[(i * 4) % 27], intensity=DemoState.intensity, **props),
                background=bg,
            ),
            mono(name, margin_top="8px", color=rx.color("gray", 11)),
        )
        for i, (name, bg, props) in enumerate(SWATCHES)
    ]
    accent_tiles = [
        rx.theme(
            rx.box(
                plate(
                    hairline.figure(figure=fid, intensity=DemoState.intensity, palette="radix-accent"),
                    background="var(--color-panel-solid)",
                ),
                mono(f'accent_color="{acc}"', margin_top="8px", color=rx.color("accent", 11)),
            ),
            accent_color=acc,
            has_background=False,
        )
        for acc, fid in zip(ACCENTS, ["riffle", "keyboard", "branches", "vault", "router", "plot"], strict=True)
    ]
    return page(
        rx.heading("Your own palette", size="4", weight="medium", margin_bottom="12px"),
        rx.text(
            "Six custom properties drive every stroke. Pass them as plate=, hi=, edge=, mid=, lo=, stroke=, or as hairline.tokens(...) on any ancestor. ",
            rx.code("plate"),
            " must be the colour the figure sits on: plates are filled, so a nearer one hides what is behind it.",
            size="2",
            color=rx.color("gray", 11),
            margin_bottom="16px",
        ),
        rx.grid(*swatch_tiles, columns=rx.breakpoints(initial="1", sm="2", lg="3"), spacing="5"),
        code_block(
            'hairline.terrain(plate="#0d2a4a", hi="#e8f1ff", edge="#7fa6d6", mid="#3f6a9c", lo="#1e4370", stroke=1.1)\n\n'
            "# or once, on a container: every figure inside inherits it\n"
            'rx.grid(..., style=hairline.tokens(palette="dark", stroke=1.2))',
        ),
        rx.heading("Following Radix Themes", size="4", weight="medium", margin_top="40px", margin_bottom="12px"),
        rx.text(
            'palette="radix" maps the strokes to the gray scale of rx.theme, so figures follow the app\'s color mode. palette="radix-accent" puts the lit stroke and silhouettes in the accent colour; each tile below sits in its own rx.theme(accent_color=...).',
            size="2",
            color=rx.color("gray", 11),
            margin_bottom="16px",
        ),
        rx.grid(*accent_tiles, columns=rx.breakpoints(initial="1", sm="2", lg="3"), spacing="5"),
        rx.heading(
            'theme="auto" and the color mode', size="4", weight="medium", margin_top="40px", margin_bottom="12px"
        ),
        rx.text(
            'With the default theme="auto" a figure reads the page: Reflex puts class="dark" on <html> in dark mode, and Hairline follows it. Toggle the color mode in the header; the tiles below change with no extra code. Forcing theme="light" or "dark" pins one.',
            size="2",
            color=rx.color("gray", 11),
            margin_bottom="16px",
        ),
        rx.grid(
            *[
                rx.box(
                    plate(hairline.figure(figure="exploded", theme=t, intensity=DemoState.intensity), background=bg),
                    mono(f'theme="{t}"', margin_top="8px", color=rx.color("gray", 11)),
                )
                for t, bg in [
                    ("auto", rx.color_mode_cond("#ffffff", "#08090a")),
                    ("light", "#ffffff"),
                    ("dark", "#08090a"),
                ]
            ],
            columns=rx.breakpoints(initial="1", sm="3"),
            spacing="5",
        ),
        title="Theming",
        lede="Lines only: no fills, glows or shadows. The palette is five stroke colours and a width, and every figure reads them from CSS custom properties.",
    )


# --------------------------------------------------------------------------- #
# Empty states                                                                #
# --------------------------------------------------------------------------- #


def empty_states() -> rx.Component:
    examples = [
        hairline.empty_state(
            "sieve",
            "No results match these filters",
            "Try widening the date range or removing a tag.",
            rx.button("Clear filters", variant="outline", size="2", on_click=EmptyState.act("Filters cleared")),
            label="An empty sieve",
        ),
        hairline.empty_state(
            "drawer",
            "No documents yet",
            "Upload an invoice to start the digitalization flow.",
            rx.button(rx.icon("upload", size=14), "Upload", size="2", on_click=EmptyState.act("Upload dialog")),
        ),
        hairline.empty_state(
            "basket",
            "Your cart is empty",
            "Plans you add show up here.",
            rx.button("Browse plans", variant="soft", size="2", on_click=EmptyState.act("Browse plans")),
        ),
        hairline.empty_state(
            "plot",
            "No data for this period",
            "Charts appear once the first events arrive.",
            rx.button("Connect a source", variant="outline", size="2", on_click=EmptyState.act("Connect a source")),
        ),
        hairline.empty_state(
            "plug",
            "Not connected",
            "The device has not reported in the last hour.",
            rx.button("Retry", size="2", variant="soft", on_click=EmptyState.act("Retrying")),
        ),
        hairline.empty_state(
            "query",
            "Nothing found for that search",
            None,
            rx.button("Ask support", size="2", variant="outline", on_click=EmptyState.act("Support")),
        ),
    ]
    return page(
        rx.grid(
            *[plate(e, background=rx.color("gray", 1)) for e in examples],
            columns=rx.breakpoints(initial="1", sm="2", lg="3"),
            spacing="5",
        ),
        rx.box(
            code_block(
                "hairline.empty_state(\n"
                '    "sieve",\n'
                '    "No results match these filters",\n'
                '    "Try widening the date range or removing a tag.",\n'
                '    rx.button("Clear filters", on_click=State.clear),\n'
                '    width="200px",\n'
                ")"
            ),
            margin_top="24px",
        ),
        title="Empty states",
        lede="At 160 to 240px, above a heading and one action, a figure makes an empty state. Its rest pose is the picture; the pointer is a bonus. hairline.empty_state() lays it out.",
    )


# --------------------------------------------------------------------------- #
# Skill-made figures                                                          #
# --------------------------------------------------------------------------- #


def skill_page() -> rx.Component:
    picker = rx.hstack(
        *[
            rx.button(
                e["idea"],
                variant=rx.cond(SkillState.selected == e["file"], "solid", "soft"),
                color_scheme="gray",
                size="1",
                on_click=SkillState.select(e["file"]),
            )
            for e in SKILL_EXAMPLES
        ],
        wrap="wrap",
        spacing="2",
    )
    stage = plate(
        mono(
            SkillState.declared.get("name", "…"),
            position="absolute",
            top="12px",
            left="14px",
            color=rx.color("gray", 10),
            z_index="1",
        ),
        mono(SkillState.caption, position="absolute", top="12px", right="14px", z_index="1"),
        hairline.custom(
            src=SkillState.src,
            intensity=DemoState.intensity,
            theme=DemoState.theme,
            on_read=SkillState.read,
            on_load=SkillState.loaded,
            on_error=SkillState.failed,
        ),
        background=rx.cond(
            DemoState.theme == "dark",
            "#08090a",
            rx.cond(DemoState.theme == "light", "#ffffff", rx.color_mode_cond("#ffffff", "#08090a")),
        ),
        width="100%",
    )
    details = rx.vstack(
        mono("prompt", color=rx.color("gray", 10)),
        rx.code("/hairline-create " + SkillState.idea, size="2"),
        mono("means", color=rx.color("gray", 10), margin_top="8px"),
        rx.text(SkillState.declared.get("means", "loading…"), size="2"),
        mono("rules", color=rx.color("gray", 10), margin_top="8px"),
        mono(SkillState.rules_text, size="2"),
        mono("range (intensity 0 → 0.5 → 1)", color=rx.color("gray", 10), margin_top="8px"),
        mono(SkillState.range_text, size="2"),
        mono("src", color=rx.color("gray", 10), margin_top="8px"),
        rx.code(SkillState.src, size="2"),
        rx.cond(
            SkillState.error != "", rx.callout(SkillState.error, color_scheme="red", icon="triangle_alert", size="1")
        ),
        spacing="1",
        align="start",
        width="100%",
    )
    paste = rx.vstack(
        rx.heading("Mount your own", size="4", weight="medium"),
        rx.text(
            'Run /hairline-create with an idea in Claude Code (after npx skills add lucasmarkes/hairline), then drop the hairline-<name>.html it writes into assets/ and use hairline.custom(src="/hairline-<name>.html"). Or paste the page, or just its figure code, here:',
            size="2",
            color=rx.color("gray", 11),
        ),
        rx.text_area(
            value=SkillState.pasted,
            on_change=SkillState.set_pasted,
            placeholder="<!doctype html>… or the figure's JS ending in hairline({ name, means, rules, range, mount })",
            font_family=MONO,
            rows="6",
            width="100%",
        ),
        rx.button("Mount", on_click=SkillState.mount_pasted, size="2"),
        rx.cond(
            SkillState.pasted_code != "",
            plate(
                hairline.custom(
                    code=SkillState.pasted_code,
                    intensity=DemoState.intensity,
                    theme=DemoState.theme,
                    on_error=SkillState.failed,
                ),
                width="100%",
                max_width="560px",
                background=rx.color_mode_cond("#ffffff", "#08090a"),
            ),
        ),
        spacing="3",
        width="100%",
        margin_top="40px",
    )
    return page(
        picker,
        rx.grid(
            stage,
            details,
            columns=rx.breakpoints(initial="1", md="minmax(0, 1fr) 320px"),
            spacing="6",
            margin_top="16px",
        ),
        code_block(
            "hairline.custom(\n"
            '    src="/skill/hairline-funnel.html",   # a page the skill wrote, in assets/\n'
            "    intensity=State.intensity,           # mapped onto the figure's declared range\n"
            "    on_load=State.loaded,                # {name, means, rules, range}\n"
            "    on_read=State.set_caption,\n"
            ")"
        ),
        paste,
        title="Figures made with the hairline-create skill",
        lede="hairline-create is Hairline's skill for coding agents: give it an idea and it draws a new figure on the same engine, as one HTML file. hairline.custom() mounts those files natively, with the same options as the packaged figures. These four are the examples published on hairline.lucasmarkes.com/skill.",
    )


# --------------------------------------------------------------------------- #
# Reference                                                                   #
# --------------------------------------------------------------------------- #


def reference() -> rx.Component:
    rows = [
        rx.table.row(
            rx.table.cell(
                rx.box(hairline.figure(figure=f.id, intensity=DemoState.intensity, theme=DemoState.theme), width="96px")
            ),
            rx.table.cell(
                rx.code(f"hairline.{f.id}()"),
                rx.text(f.summary, size="1", color=rx.color("gray", 10), margin_top="4px"),
            ),
            rx.table.cell(mono(f.parameter)),
            rx.table.cell(mono(f"{f.range[0]:g}")),
            rx.table.cell(mono(f"{f.range[1]:g}")),
            rx.table.cell(mono(f"{f.range[2]:g} {f.unit}")),
            align="center",
        )
        for f in FIGURES
    ]
    options = [
        (
            "intensity",
            "float | Var[float]",
            "0.5",
            "How strongly the figure answers the pointer, 0 (subtle) to 1 (strong). Clamped.",
        ),
        (
            "theme",
            '"auto" | "light" | "dark"',
            '"auto"',
            "auto follows the page: class dark / data-theme=dark on an ancestor, then color-scheme.",
        ),
        ("label", "str", "a description", "The accessible name (aria-label)."),
        ("on_read", "EventHandler[str]", "", "The caption each time it changes; once at mount with the rest caption."),
        (
            "plate / hi / edge / mid / lo",
            "str (CSS colour)",
            "palette",
            "Shortcuts for the --hairline-* custom properties.",
        ),
        ("stroke", "float", "0.9", "Stroke width in CSS pixels, at any size."),
        (
            "palette",
            '"light" | "dark" | "radix" | "radix-accent" | dict',
            "",
            "A base palette for the shortcuts above.",
        ),
        ("figure (hairline.figure)", "str | Var[str]", '"terrain"', "Which of the 27 to draw; changing it remounts."),
        (
            "src / code (hairline.custom)",
            "str | Var[str]",
            "",
            "A skill-made figure: page URL, or its JS/HTML as text.",
        ),
        (
            "on_load / on_error (hairline.custom)",
            "EventHandler",
            "",
            "{name, means, rules, range} once mounted; a message on failure.",
        ),
    ]
    return page(
        rx.heading("Options", size="4", weight="medium", margin_bottom="12px"),
        rx.table.root(
            rx.table.header(
                rx.table.row(*[rx.table.column_header_cell(h) for h in ("Prop", "Type", "Default", "What it does")])
            ),
            rx.table.body(
                *[
                    rx.table.row(
                        rx.table.cell(rx.code(n)),
                        rx.table.cell(mono(t)),
                        rx.table.cell(mono(d)),
                        rx.table.cell(rx.text(w, size="2")),
                    )
                    for n, t, d, w in options
                ]
            ),
            variant="surface",
            size="1",
        ),
        rx.heading(
            "What intensity sets in each figure", size="4", weight="medium", margin_top="40px", margin_bottom="12px"
        ),
        rx.box(
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        *[rx.table.column_header_cell(h) for h in ("", "Figure", "Parameter", "0", "0.5", "1")]
                    )
                ),
                rx.table.body(*rows),
                variant="surface",
                size="1",
            ),
            overflow_x="auto",
        ),
        title="Reference",
        lede="Everything the components take. Every packaged figure has the same four options; the Python wrapper adds theme shortcuts, a runtime-picked figure and a loader for skill-made figures.",
    )


app = rx.App()
app.add_page(gallery, route="/", title="reflex-hairline · Gallery")
app.add_page(playground, route="/playground", title="reflex-hairline · Playground")
app.add_page(theming, route="/theming", title="reflex-hairline · Theming")
app.add_page(empty_states, route="/empty-states", title="reflex-hairline · Empty states")
app.add_page(skill_page, route="/skill", title="reflex-hairline · Skill figures")
app.add_page(reference, route="/reference", title="reflex-hairline · Reference")
