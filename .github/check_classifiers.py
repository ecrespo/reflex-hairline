"""Fail if pyproject.toml uses a classifier PyPI would reject."""

import sys

import tomllib
from trove_classifiers import classifiers

with open("pyproject.toml", "rb") as f:
    used = tomllib.load(f)["project"].get("classifiers", [])
bad = [c for c in used if c not in classifiers]
for c in bad:
    print(f"::error file=pyproject.toml::invalid classifier: {c!r}")
sys.exit(1 if bad else 0)
