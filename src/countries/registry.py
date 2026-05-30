"""The country registry — the single place that lists supported countries.

Adding a country = add its module and one line here. ``CH`` is the default so the
original Swiss build runs unchanged when no country is specified.
"""

from __future__ import annotations

from . import ch, de, fr, intl
from .base import Country

COUNTRIES: dict[str, Country] = {
    ch.COUNTRY.code: ch.COUNTRY,
    de.COUNTRY.code: de.COUNTRY,
    fr.COUNTRY.code: fr.COUNTRY,
    # The supra-national layer (harmonised codes: COLREG ingested, CEVNI pending).
    # A sourcing-only member: no permits, so the player skips it and the
    # jurisdictions tree treats it as a base, not a national implementer.
    intl.COUNTRY.code: intl.COUNTRY,
}

DEFAULT = "CH"


def codes() -> list[str]:
    """Supported country codes, sorted (for argparse choices, etc.)."""
    return sorted(COUNTRIES)


def get(code: str | None) -> Country:
    """Return the Country for a code (case-insensitive); falls back to the default
    when ``code`` is empty, raises on an unknown non-empty code."""
    if not code:
        return COUNTRIES[DEFAULT]
    key = code.upper()
    if key not in COUNTRIES:
        raise ValueError(f"unknown country {code!r}; choose from {codes()}")
    return COUNTRIES[key]
