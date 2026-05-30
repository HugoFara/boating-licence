"""A small curated seed of prose/law questions, hand-authored from real KB units.

These exist so the review queue and the player have genuine multi-theme content
before anyone runs the LLM drafter (`run.py draft`), and so the
review→approve→publish loop is demonstrable end-to-end. They are *drafts like any
other*: loaded through the same grounding + validation path and stored as
`pending` (generator `seed:curated.v1`) — a human must still approve them.

Each entry is keyed by a KB unit `ref`; the loader (`prose.seed_questions`)
attaches that unit's provenance/licence and grounds the answer against its text.
Choices are (text, is_correct).
"""

SEED = [
    # --- Définitions (ONI art. 2) -------------------------------------------
    {"ref": "ONI art. 2", "polarity": "affirmative",
     "stem": "Au sens de l’ONI, que désigne le terme « bateau motorisé » ?",
     "choices": [("Un bateau à propulsion mécanique", True),
                 ("Un bateau non propulsé remorqué par un autre bateau", False),
                 ("Un engin flottant tel qu’une drague ou une grue", False)],
     "explanation": "ONI art. 2 : le « bateau motorisé » est un bateau à propulsion mécanique."},
    {"ref": "ONI art. 2", "polarity": "affirmative",
     "stem": "Qu’est-ce qu’un « convoi poussé » selon l’ONI ?",
     "choices": [("Une composition de bateaux non propulsés réunis en un ensemble rigide, poussée par au moins un bateau à moteur", True),
                 ("Une composition de bateaux non propulsés remorquée par au moins un bateau à moteur", False),
                 ("Tout groupe de bateaux de plaisance naviguant ensemble", False)],
     "explanation": "ONI art. 2 : le convoi poussé est un ensemble rigide poussé ; remorqué = convoi remorqué."},

    # --- Météorologie (MétéoSuisse : La bise) -------------------------------
    {"ref": "MétéoSuisse : La bise", "polarity": "affirmative",
     "stem": "De quelle direction souffle la bise sur le Petit-Lac et le Grand-Lac ?",
     "choices": [("Du nord-est (NE)", True),
                 ("Du sud-ouest (SO)", False),
                 ("Du nord-ouest sur l’ensemble du lac", False)],
     "explanation": "MétéoSuisse : la bise souffle du NE sur le Petit et le Grand-Lac (NNW seulement sur le Haut-Lac)."},
    {"ref": "MétéoSuisse : La bise", "polarity": "affirmative",
     "stem": "À quelle période la bise est-elle nettement dominante sur le Léman ?",
     "choices": [("Dans la première moitié de l’année, notamment au printemps", True),
                 ("En plein été, de juillet à août", False),
                 ("Uniquement lors des nuits d’automne", False)],
     "explanation": "MétéoSuisse : la bise est dominante dans la première moitié de l’année, surtout au printemps."},

    # --- Matelotage (Nœud de chaise) ----------------------------------------
    {"ref": "Matelotage — Nœud de chaise : Roi des nœuds", "polarity": "affirmative",
     "stem": "Pourquoi le nœud de chaise est-il qualifié de « roi des nœuds » ?",
     "choices": [("C’est un nœud de boucle fiable qui ne glisse pas sous tension et se dénoue facilement", True),
                 ("Il se resserre de plus en plus sous tension jusqu’à devenir indénouable", False),
                 ("Il sert uniquement à raccorder deux cordages de même diamètre", False)],
     "explanation": "Le nœud de chaise est une boucle fiable qui ne glisse pas et se dénoue aisément."},
    {"ref": "Matelotage — Nœud de chaise : Roi des nœuds", "polarity": "affirmative",
     "stem": "Combien de méthodes classiques sont retenues pour l’enseignement du nœud de chaise ?",
     "choices": [("Deux (la tricotée et la préparée)", True),
                 ("Dix-huit méthodes équivalentes", False),
                 ("Une seule méthode officielle", False)],
     "explanation": "Il subsiste deux méthodes classiques d’enseignement : tricotée ou préparée."},

    # --- Eaux frontalières (RNL art. 64 — Priorités) ------------------------
    {"ref": "RNL art. 64", "polarity": "affirmative",
     "stem": "Face à un bateau incapable de manœuvrer qui signale sa présence, que doit faire tout autre bateau ?",
     "choices": [("S’écarter de ce bateau", True),
                 ("Maintenir son cap et sa vitesse", False),
                 ("Le dépasser par tribord", False)],
     "explanation": "RNL art. 64, al. 1 : tout bateau doit s’écarter d’un bateau incapable de manœuvrer qui signale sa présence."},
    {"ref": "RNL art. 64", "polarity": "affirmative",
     "stem": "En cas de rencontre, de quels bateaux tout bateau — hormis les bateaux à passagers prioritaires et les convois remorqués — doit-il s’écarter ?",
     "choices": [("Des bateaux à marchandises", True),
                 ("Des bateaux de plaisance", False),
                 ("Des bateaux de sport naviguant à la voile", False)],
     "explanation": "RNL art. 64, al. 2 let. b : il s’écarte des bateaux à marchandises."},

    # --- Lois (ONI art. 134 — Engins de sauvetage) --------------------------
    {"ref": "ONI art. 134", "polarity": "affirmative",
     "stem": "Lesquels de ces engins sont des moyens de sauvetage INDIVIDUELS au sens de l’ONI ?",
     "choices": [("Les gilets de sauvetage avec cols", True),
                 ("Les bouées de sauvetage", True),
                 ("Les îlots de sauvetage pour l’embarquement", False)],
     "explanation": "ONI art. 134 : gilets avec cols et bouées = individuels ; les îlots d’embarquement sont collectifs."},
    {"ref": "ONI art. 134", "polarity": "affirmative",
     "stem": "Quelle poussée hydrostatique minimale un moyen de sauvetage individuel doit-il avoir (cas général) ?",
     "choices": [("Au moins 75 N", True),
                 ("Au moins 750 N", False),
                 ("Au moins 50 N", False)],
     "explanation": "ONI art. 134, al. 2 : au moins 75 N (sauf bateaux visés à l’art. 134a)."},
]
