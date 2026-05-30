"""Country registry — the dimension that lets the project cover more than one
country's recreational-boating theory exam.

Each country is one self-contained module (``ch``, ``de``, …) exposing a single
``COUNTRY`` object built from the dataclasses in :mod:`countries.base`. The rest
of the pipeline (fetch → parse → normalize → questions → web) is parameterised by
the active country, defaulting to ``CH`` so the original Swiss build is unchanged.

Keeping every country in its own file is deliberate: adding a country touches
only that file + the registry below, so parallel work on different countries
doesn't collide.

Relationship to :mod:`src.jurisdictions`: that package is the *descriptive*
routing/display layer (what the player picker shows, the CEVNI relation) and
deliberately owns no sources or tagging. This package is its *build-time*
companion — the ingestion config (law sources, the theme tagger, the permit
catalogue, regional regimes) the fetch → parse → normalize pipeline consumes.
``jurisdictions/<code>.py`` derives its metadata from ``countries.<code>`` so
there's a single source of truth per country.
"""

from __future__ import annotations

from .registry import COUNTRIES, DEFAULT, codes, get

__all__ = ["COUNTRIES", "DEFAULT", "codes", "get"]
