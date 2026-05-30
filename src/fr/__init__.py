"""France — *permis plaisance* content (côtière + eaux intérieures).

Self-contained, hand-authored and fully cited, derived from French law (an
official act, no copyright, published under the Licence Ouverte / Etalab). It does
not go through the Swiss Fedlex pipeline; `build_fr.py` turns the seed bank into
the canonical Question schema and bundles per-option static players under web/fr/.

Importing this package registers the French exam themes with `src.themes` so the
shared question validator accepts them.
"""

from . import themes_fr as _themes_fr  # noqa: F401  (registers FR themes on import)
