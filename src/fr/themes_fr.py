"""French *permis plaisance* exam themes and per-option theme sets.

These are the France analogue of `src.themes` for Switzerland. The ids are
distinct from the Swiss ones (themes are a global namespace — see
`themes.register_themes`) and follow the official *référentiel* in the annexes of
the Arrêté du 28 septembre 2007: art. 1 for the option côtière, art. 2 for the
option eaux intérieures. The 12–13 fine-grained program headings are grouped into
the coarser exam themes the player balances draws on.

Importing this module registers the labels with `src.themes` so questions carrying
these themes validate.
"""

from __future__ import annotations

from .. import themes

# Theme id -> French label. Some themes are shared by both options (règles de
# route, sécurité, réglementation, environnement); the rest are option-specific.
FR_THEMES: dict[str, str] = {
    # --- maritime (option côtière) ----------------------------------------
    "securite": "Sécurité et matériel d'armement",
    "balisage": "Balisage et signalisation maritime",
    "regles_route": "Règles de barre et de route",
    "feux_signaux": "Feux, marques et signaux",
    "meteo_maree": "Météorologie et marées",
    "reglementation": "Réglementation, permis et radio",
    "environnement": "Protection de l'environnement",
    # --- fluvial (option eaux intérieures) --------------------------------
    "voies_navigables": "Voies navigables et stationnement",
    "ecluses": "Écluses, barrages et ouvrages",
    "signalisation_fluviale": "Signalisation des voies et des bateaux",
}

# English study-translation labels (FR is the only authoritative language for the
# permit; EN is an unofficial study aid). Same keys as FR_THEMES.
FR_THEMES_EN: dict[str, str] = {
    "securite": "Safety and required equipment",
    "balisage": "Maritime buoyage and marks",
    "regles_route": "Steering and sailing rules",
    "feux_signaux": "Lights, shapes and signals",
    "meteo_maree": "Weather and tides",
    "reglementation": "Regulations, licence and radio",
    "environnement": "Environmental protection",
    "voies_navigables": "Waterways and mooring",
    "ecluses": "Locks, dams and structures",
    "signalisation_fluviale": "Waterway and vessel signs",
}

# Which themes each option's exam draws on, in display/exam order. The shared
# themes appear in both; the option-specific ones differ. This is the single
# source of truth for the per-option theme set (the exam config reads it).
OPTION_THEMES: dict[str, tuple[str, ...]] = {
    "cotiere": (
        "securite", "balisage", "regles_route", "feux_signaux",
        "meteo_maree", "reglementation", "environnement",
    ),
    "eaux_interieures": (
        "voies_navigables", "ecluses", "signalisation_fluviale",
        "regles_route", "securite", "reglementation", "environnement",
    ),
}

# Register with the shared theme system so question validation accepts these ids.
themes.register_themes(FR_THEMES)


def is_valid(theme_id: str) -> bool:
    return theme_id in FR_THEMES


def label(theme_id: str, lang: str = "fr") -> str:
    table = FR_THEMES_EN if lang == "en" else FR_THEMES
    return table.get(theme_id, theme_id)
