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
    # (Dropped on review: a "how many teaching methods exist for the bowline?"
    #  item — grounded in the WP text but pure trivia, no exam relevance.)

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

    # --- Voile (cat-D, étude — non examiné en théorie) ----------------------
    # Grounded in the FR Wikipedia "voile" KB units (CC BY-SA). Sailing technique
    # is NOT on the theory exam (identical for cat-A/D); these surface as study
    # content for the cat-D practical. Answers use the source's own vocabulary so
    # the grounding check passes; one human still approves them via `review`.
    {"ref": "Voile — Allure (marine) : Le vent debout", "polarity": "affirmative",
     "stem": "À l’allure du vent debout, que doit faire le voilier pour pouvoir progresser à l’aide de ses voiles ?",
     "choices": [("S’écarter d’environ 45° de l’axe du vent (30° sur les voiliers de régate les plus performants)", True),
                 ("Maintenir son cap exactement face au vent en bordant ses voiles au maximum", False),
                 ("Établir le spinnaker pour capter le vent venant de l’avant", False)],
     "explanation": "Face au vent (vent debout) le voilier ne peut pas avancer : il doit s’écarter d’environ 45° de l’axe du vent (30° en régate) et louvoyer."},
    {"ref": "Voile — Allure (marine) : Tribord amures, bâbord amures", "polarity": "affirmative",
     "stem": "Quand dit-on qu’un voilier est « tribord amures » ?",
     "choices": [("Lorsque le vent vient de la droite par rapport à l’axe du navire", True),
                 ("Lorsqu’il navigue vent arrière, les voiles en ciseaux", False),
                 ("Lorsqu’il a la priorité sur tous les autres bateaux du plan d’eau", False)],
     "explanation": "Le voilier est tribord amures quand le vent vient de la droite (tribord) ; bâbord amures dans le cas inverse. Ces distinctions fondent les règles de priorité entre voiliers."},
    {"ref": "Voile — Allure (marine) : Le vent arrière", "polarity": "affirmative",
     "stem": "Qu’observe-t-on à l’allure du vent arrière ?",
     "choices": [("Le roulis s’accentue et l’empannage menace", True),
                 ("La vitesse devient maximale, supérieure à celle du grand largue", False),
                 ("Le voilier ne peut plus avancer car il est face au vent", False)],
     "explanation": "Au vent arrière l’écoulement de l’air est perturbé : la vitesse diminue par rapport au grand largue, le roulis s’accentue et l’empannage menace."},
    {"ref": "Voile — Virement de bord : Principe", "polarity": "affirmative",
     "stem": "Que se passe-t-il lors d’un virement de bord ?",
     "choices": [("Le côté du bateau qui était sous le vent passe au vent, et vice-versa", True),
                 ("Le voilier conserve la même amure tout au long de la manœuvre", False),
                 ("La manœuvre se fait obligatoirement en passant par le vent arrière", False)],
     "explanation": "Au virement de bord, le côté qui était sous le vent passe au vent (changement d’amure par le vent debout)."},
    {"ref": "Voile — Empannage : Définition", "polarity": "affirmative",
     "stem": "Qu’est-ce qui caractérise l’empannage par rapport au virement de bord ?",
     "choices": [("Le changement d’amure se fait en passant par le vent arrière", True),
                 ("Le changement d’amure se fait en passant par le vent debout", False),
                 ("Il ne modifie pas l’orientation des voiles", False)],
     "explanation": "L’empannage change d’amure en passant par le vent arrière ; passer par le vent debout est au contraire un virement de bord."},
    {"ref": "Voile — Chavirage : Source du phénomène", "polarity": "affirmative",
     "stem": "Sur un dériveur léger de sport, comment nomme-t-on couramment le chavirage et quelle en est la nature ?",
     "choices": [("Le « dessalage » : il est courant et sans gravité", True),
                 ("Le « naufrage » : il entraîne presque toujours la perte du bateau", False),
                 ("L’« auloffée » : elle ne survient qu’au près serré", False)],
     "explanation": "Sur un dériveur léger, le chavirage — dit dessalage — est courant et sans gravité ; il vient d’une recherche excessive de vitesse ou d’un mauvais placement des équipiers."},
    {"ref": "Voile — Foc : Présentation", "polarity": "affirmative",
     "stem": "Qu’est-ce que le foc sur un voilier ?",
     "choices": [("Une voile d’avant de forme triangulaire, retenue à l’étai par son guindant", True),
                 ("La voile principale gréée en arrière du mât", False),
                 ("Un câble du gréement dormant qui maintient le mât", False)],
     "explanation": "Le foc est une voile d’avant triangulaire retenue à l’étai par son guindant ; il joue un rôle primordial dans la réussite du virement de bord."},
]
