"""Unit tests for reflex-hairline: catalogue, components, theming and the JS assets."""

from __future__ import annotations

from pathlib import Path

import pytest

import reflex_hairline as rh
from reflex_hairline import (
    BY_ID,
    FIGURE_CLASSES,
    FIGURE_IDS,
    FIGURES,
    HAIRLINE_NPM,
    hairline,
    tokens,
)

PKG = Path(rh.__file__).parent

# The table in @lucasmarkes/hairline src/intensity.ts (v0.3.0): value at intensity 0, 0.5 and 1.
UPSTREAM_TABLE = {
    "riffle": (0, 40, 90), "terrain": (1.5, 3, 5), "exploded": (12, 28, 40),
    "phosphor": (150, 520, 1500), "slow": (0.6, 0.2, 0.05), "turntable": (200, 650, 1500),
    "keyboard": (1, 2, 3.5), "elevator": (40, 100, 220), "phone": (16, 28, 40),
    "laptop": (100, 125, 150), "terminal": (1, 2, 3.5), "cabinet": (1.5, 3, 5),
    "branches": (1, 3, 6), "vault": (250, 600, 1500), "lockers": (55, 90, 120),
    "padlock": (45, 90, 100), "patch": (1, 2.5, 5), "dish": (30, 50, 70),
    "router": (0.5, 1.5, 3), "loupe": (1.3, 1.8, 2.6), "sieve": (6, 14, 24),
    "rail": (1, 2, 3.5), "plug": (0.35, 0.6, 0.9), "query": (20, 40, 55),
    "drawer": (12, 22, 34), "basket": (8, 16, 28), "plot": (3, 6, 12),
}  # fmt: skip


def test_catalogue_has_all_27_figures():
    assert len(FIGURES) == 27
    assert len(set(FIGURE_IDS)) == 27
    assert set(FIGURE_IDS) == set(UPSTREAM_TABLE)
    assert set(BY_ID) == set(FIGURE_IDS)


@pytest.mark.parametrize("fid", sorted(UPSTREAM_TABLE))
def test_catalogue_ranges_match_upstream(fid):
    assert tuple(BY_ID[fid].range) == pytest.approx(UPSTREAM_TABLE[fid])


@pytest.mark.parametrize("fid", sorted(UPSTREAM_TABLE))
def test_every_figure_has_a_component_and_a_namespace_entry(fid):
    cls = FIGURE_CLASSES[fid]
    assert cls.tag == BY_ID[fid].name
    assert cls.info() is BY_ID[fid]
    factory = getattr(hairline, fid)
    comp = factory(intensity=0.3)
    assert comp.render()["name"] == BY_ID[fid].name
    assert getattr(rh, fid) == cls.create


def test_figure_imports_from_react_entry_with_pinned_version():
    comp = hairline.terrain()
    imports = comp._get_all_imports()
    assert HAIRLINE_NPM == "@lucasmarkes/hairline@0.3.0"
    (var,) = imports[HAIRLINE_NPM]
    assert var.tag == "Terrain"
    assert var.package_path == "/react"
    assert not var.is_default


def test_props_render():
    props = hairline.vault(intensity=0.8, theme="dark", label="A vault").render()["props"]
    assert "intensity:0.8" in props
    assert 'theme:"dark"' in props
    assert 'label:"A vault"' in props


def test_on_read_is_an_event_trigger():
    assert "on_read" in hairline.terrain().get_event_triggers()


def test_tokens_helper():
    assert tokens(plate="#000", stroke=1.2) == {"--hairline-plate": "#000", "--hairline-stroke": 1.2}
    radix = tokens(palette="radix", hi="red")
    assert radix["--hairline-hi"] == "red"
    assert radix["--hairline-plate"] == "var(--color-panel-solid)"
    assert tokens(palette="dark")["--hairline-plate"] == "#08090a"
    with pytest.raises(ValueError):
        tokens(palette="nope")


def test_theme_kwargs_fold_into_style():
    rendered = str(hairline.plot(plate="#123456", palette="light").render()["props"])
    assert "--hairline-plate" in rendered
    assert "#123456" in rendered
    assert "plate:" not in rendered.replace("--hairline-plate", "")


def test_dynamic_figure_and_custom_use_the_wrapper_module():
    for comp in (hairline.figure(figure="sieve"), hairline.custom(src="/x.html")):
        imports = comp._get_all_imports()
        wrapper = [k for k in imports if k.endswith("hairline_reflex.js")]
        assert wrapper, imports
        assert HAIRLINE_NPM in imports  # installed as a dependency


def test_empty_state_builds():
    comp = hairline.empty_state("drawer", "Nothing here", "Add a file to start.")
    assert "Drawer" in str(comp)


def test_js_assets_ship_with_the_package():
    wrapper = (PKG / "hairline_reflex.js").read_text()
    kernel = (PKG / "hairline_kernel.js").read_text()
    assert "export function HairlineFigure" in wrapper
    assert "export function HairlineCustom" in wrapper
    assert kernel.rstrip().endswith("export default HL;")
    assert (PKG / "LICENSE.hairline").exists()
