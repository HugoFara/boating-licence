"""Hand-authored, sourced "why" concept cards (roadmap group A).

A concept explains the *generative logic* behind a principle so a value or rule
becomes reconstructable instead of memorised. Like the France question seeds
(`seed_fr.py`), these are hand-authored, fully cited, and ship as ``approved`` —
the source is the authority (memory/source-questions-never-recall): every fact in
a body is reproduced from reviewed, already-shipped questions and their primary
source, never invented.

Scoping matters: IALA Region A buoyage is *maritime* (French coastal waters);
Swiss inland (ONI/RNL) and CEVNI rivers use different marks, so a maritime
buoyage concept is loaded ONLY into the banks where it is correct. Each entry
lists the bank ids it ``applies`` to; the build loader writes only those.
"""

from __future__ import annotations

from .schema import Concept

# Each seed: one principle, the bank ids it applies to, shared provenance, and a
# per-language {title, body}. Bodies use blank-line paragraphs (the player splits
# them). Keep them faithful to the cited source.
_SEED: list[dict] = [
    {
        "principle": "iala-buoyage",
        "kind": "principle",
        # French coastal (maritime, IALA Region A). NOT the inland eaux_interieures
        # bank (CEVNI) nor Swiss lakes — those use different buoyage.
        "applies": {"fr_cotiere"},
        "prov": {
            "ref": "Balisage IALA région A — marques latérales, eaux saines, "
                   "marques spéciales",
            "source": "IALA — Système de balisage maritime, région A "
                      "(Recommandation R1001)",
            "url": None, "as_of": None, "licence": None,
        },
        "lang": {
            "fr": {
                "title": "Balisage IALA région A : reconstituer une marque, pas la mémoriser",
                "body": (
                    "En région A (Europe, dont la France), le balisage code le côté "
                    "du chenal par la COULEUR et la FORME — de sorte qu'on peut "
                    "retrouver le sens de n'importe quelle marque au lieu d'en "
                    "apprendre la liste par cœur.\n\n"
                    "Le sens de référence est « en venant du large » (de la mer vers "
                    "le port) :\n"
                    "— Bâbord : marque ROUGE, forme CYLINDRIQUE (« boîte ») ; on la "
                    "laisse sur sa gauche en entrant.\n"
                    "— Tribord : marque VERTE, forme CONIQUE ; on la laisse sur sa "
                    "droite en entrant.\n"
                    "La forme répète l'information du côté : même à contre-jour ou de "
                    "nuit, un cône reste « tribord » et un cylindre « bâbord ».\n\n"
                    "Les autres marques ne bordent pas un chenal, elles qualifient un "
                    "point :\n"
                    "— Eaux saines (milieu de chenal / atterrissage) : bandes "
                    "VERTICALES rouges et blanches, voyant sphérique rouge — pas de "
                    "danger, on passe de chaque côté.\n"
                    "— Marque spéciale : entièrement JAUNE (croix de Saint-André "
                    "jaune) — signale une zone ou un dispositif (baignade, conduite "
                    "immergée, zone réglementée), pas un danger en soi.\n\n"
                    "La règle pratique tient en une phrase : la couleur et la forme "
                    "d'une marque latérale disent de quel côté passer — à condition "
                    "de savoir d'où l'on « vient du large »."
                ),
            },
            "en": {
                "title": "IALA Region A buoyage: reconstruct a mark instead of memorising it",
                "body": (
                    "In Region A (Europe, incl. France), buoyage encodes the side of "
                    "the channel through COLOUR and SHAPE — so you can work out any "
                    "mark rather than learning a list by heart.\n\n"
                    "The reference direction is \"coming from seaward\" (from the sea "
                    "towards the harbour):\n"
                    "— Port hand: RED mark, CYLINDRICAL (can) shape; leave it on your "
                    "left when entering.\n"
                    "— Starboard hand: GREEN mark, CONICAL shape; leave it on your "
                    "right when entering.\n"
                    "The shape repeats the side: even against the light or at night, "
                    "a cone is still \"starboard\" and a can \"port\".\n\n"
                    "Other marks don't edge a channel — they qualify a point:\n"
                    "— Safe water (mid-channel / landfall): VERTICAL red and white "
                    "stripes, red spherical topmark — no danger, pass either side.\n"
                    "— Special mark: all YELLOW (yellow St Andrew's cross) — marks a "
                    "zone or installation (bathing, submerged pipe, restricted area), "
                    "not a danger in itself.\n\n"
                    "The practical rule fits in one sentence: a lateral mark's colour "
                    "and shape tell you which side to pass — once you know which way "
                    "is \"from seaward\"."
                ),
            },
        },
    },
    {
        "principle": "nav-lights",
        "kind": "principle",
        # Swiss inland (ONI federal + RNL Léman). NOT maritime: the arcs happen to
        # match COLREG, but the carriage rules below are the inland ones.
        "applies": {"ch"},
        "prov": {
            "ref": "ONI art. 18a, 19, 24, 25, 26 — genres de feux et signalisation "
                   "de nuit (RNL art. 21, texte identique)",
            "source": "Ordonnance sur la navigation intérieure (ONI), RS 747.201.1",
            "url": "https://www.fedlex.admin.ch/eli/cc/1979/337_337_337/fr",
            "as_of": "2022-01-01",
            "licence": "Public domain — Swiss federal law (freely reusable).",
        },
        "lang": {
            "fr": {
                "title": "Feux de nuit : un code d'angles, pas une liste à retenir",
                "body": (
                    "Les feux ne décrivent pas le bateau : ils découpent l'horizon. "
                    "Chaque genre de feu couvre un arc précis (ONI art. 18a, repris "
                    "mot pour mot par le RNL art. 21), et ces arcs se complètent "
                    "exactement — c'est ce qui permet de déduire ce qu'on voit au "
                    "lieu de l'apprendre par cœur.\n\n"
                    "— Feu de mât : blanc, visible de l'avant sur 225°, soit 112° 30' "
                    "de chaque bord.\n"
                    "— Feux de côté : vert à tribord, rouge à bâbord, chacun visible "
                    "de l'avant sur 112° 30' de son bord.\n"
                    "— Feu de poupe : blanc, visible de l'arrière sur 135°, soit "
                    "67° 30' de chaque bord.\n"
                    "— Feu visible de tous les côtés : 360°.\n\n"
                    "Deux additions valent tout le tableau : 112° 30' + 112° 30' = "
                    "225°, l'arc du feu de mât ; et 225° + 135° = 360°, l'horizon "
                    "entier. Un feu bicolore réunit les deux feux de côté dans un "
                    "seul fanal ; un feu de mât tricolore y ajoute le feu de poupe "
                    "(art. 18a, al. 3 et 5).\n\n"
                    "D'où la lecture inverse, celle qui sert la nuit : les deux feux "
                    "de côté à la fois, on est dans son secteur avant ; un seul rouge "
                    "ou un seul vert, on voit son flanc ; du blanc de poupe seul, on "
                    "est derrière elle.\n\n"
                    "Ce que chaque bateau porte suit ensuite une échelle de "
                    "simplification :\n"
                    "— Bateau motorisé en cours de route, de nuit et par temps "
                    "bouché : feu de mât, feux de côté distincts, feu de poupe "
                    "(art. 24, al. 1).\n"
                    "— Bateau de sport ou de plaisance motorisé, et voilier "
                    "naviguant au moteur : quatre combinaisons au choix, du jeu "
                    "complet au feu bicolore avec un feu blanc visible de tous les "
                    "côtés (art. 24, al. 3).\n"
                    "— Voilier ne naviguant qu'à la voile : feux de côté et feu de "
                    "poupe, ou feu bicolore et feu de poupe, ou feu tricolore, ou un "
                    "feu blanc visible de tous les côtés (art. 25, al. 2) ; deux feux "
                    "superposés, rouge au-dessus de vert, peuvent s'y ajouter, mais "
                    "pas avec un tricolore (art. 25, al. 3).\n"
                    "— Bateau non motorisé : un feu ordinaire blanc visible de tous "
                    "les côtés ; sur un bateau à rames, il peut être à éclats "
                    "(art. 25, al. 1).\n"
                    "— Propulsion ne dépassant pas 6 kW, ou coque de 7 m au plus et "
                    "vitesse de 7 nœuds au plus inscrite au permis de navigation : un "
                    "seul feu blanc visible de tous les côtés suffit (art. 24, "
                    "al. 5).\n"
                    "— En stationnement de nuit : feu ordinaire blanc visible de tous "
                    "les côtés, sauf amarré à la rive ou sur un lieu de stationnement "
                    "officiellement autorisé (art. 26, al. 1).\n\n"
                    "Sur un bateau de sport ou de plaisance de moins de 12 m, les "
                    "portées minimales sont de 1 mille pour les feux de côté et le "
                    "feu bicolore, et de 2 milles pour le feu de mât, le feu de poupe "
                    "et le feu blanc visible de tous les côtés (art. 19, al. 4).\n\n"
                    "Enfin, les feux ne sont pas qu'une signature : ils définissent "
                    "une règle de route. Rattrape celui qui s'approche par l'arrière "
                    "au point de ne voir, de nuit, que le feu de poupe (art. 46, "
                    "al. 2) ; le RNL art. 63, al. 2 en donne l'angle — plus de "
                    "22° 30' sur l'arrière du travers, aucun feu de côté visible. La "
                    "géométrie des feux et celle des priorités sont la même."
                ),
            },
            "de": {
                "title": "Lichter bei Nacht: ein Winkelcode, keine Liste zum Auswendiglernen",
                "body": (
                    "Lichter beschreiben nicht das Schiff — sie teilen den Horizont "
                    "auf. Jede Lichtart deckt einen festen Horizontbogen ab (BSV "
                    "Art. 18a, wortgleich übernommen in RNL Art. 21), und diese Bögen "
                    "ergänzen sich genau. Deshalb lässt sich ableiten, was man sieht, "
                    "statt es auswendig zu lernen.\n\n"
                    "— Topplicht: weiss, von vorne über 225° sichtbar, nach jeder "
                    "Seite 112° 30'.\n"
                    "— Seitenlichter: grün an Steuerbord, rot an Backbord, je von "
                    "vorne über 112° 30' der betreffenden Seite.\n"
                    "— Hecklicht: weiss, von hinten über 135° sichtbar, nach jeder "
                    "Seite 67° 30'.\n"
                    "— Rundumlicht: 360°.\n\n"
                    "Zwei Additionen ersetzen die ganze Tabelle: 112° 30' + "
                    "112° 30' = 225°, der Bogen des Topplichts; und 225° + 135° = "
                    "360°, der volle Horizont. Ein Kombinations-Seitenlicht fasst "
                    "beide Seitenlichter in einer Laterne zusammen, ein "
                    "Dreifarben-Topplicht zusätzlich das Hecklicht (Art. 18a Abs. 3 "
                    "und 5).\n\n"
                    "Daraus folgt die umgekehrte Lesart, die nachts zählt: beide "
                    "Seitenlichter zugleich — man steht in ihrem vorderen Sektor; nur "
                    "rot oder nur grün — man sieht ihre Seite; nur weisses Hecklicht "
                    "— man ist hinter ihr.\n\n"
                    "Was ein Schiff führen muss, folgt einer Stufenleiter der "
                    "Vereinfachung:\n"
                    "— Schiff mit Maschinenantrieb in Fahrt, bei Nacht und bei "
                    "unsichtigem Wetter: Topplicht, getrennte Seitenlichter, "
                    "Hecklicht (Art. 24 Abs. 1).\n"
                    "— Sportboote und Vergnügungsschiffe mit Maschinenantrieb sowie "
                    "Segelschiffe unter Motor: vier zulässige Kombinationen, vom "
                    "vollen Satz bis zum Kombinations-Seitenlicht mit weissem "
                    "Rundumlicht (Art. 24 Abs. 3).\n"
                    "— Segelschiffe, die nur unter Segel fahren: getrennte "
                    "Seitenlichter und Hecklicht, oder Kombinations-Seitenlicht und "
                    "Hecklicht, oder Dreifarben-Topplicht, oder ein weisses "
                    "Rundumlicht (Art. 25 Abs. 2); zusätzlich sind zwei senkrecht "
                    "übereinander angebrachte Rundumlichter, rot über grün, erlaubt "
                    "— aber nicht zusammen mit einem Dreifarben-Topplicht (Art. 25 "
                    "Abs. 3).\n"
                    "— Schiff ohne Maschinenantrieb: ein weisses gewöhnliches "
                    "Rundumlicht; auf Ruderbooten darf es ein Blitzlicht sein "
                    "(Art. 25 Abs. 1).\n"
                    "— Antriebsleistung höchstens 6 kW, oder Rumpflänge höchstens 7 m "
                    "und Höchstgeschwindigkeit 7 Knoten im Schiffsausweis "
                    "eingetragen: ein einziges weisses Rundumlicht genügt (Art. 24 "
                    "Abs. 5).\n"
                    "— Stillliegend bei Nacht: weisses gewöhnliches Rundumlicht, "
                    "ausser am Ufer oder an einem amtlich bewilligten Liegeplatz "
                    "festgemacht (Art. 26 Abs. 1).\n\n"
                    "Und die Lichter sind nicht nur Kennzeichen, sie definieren eine "
                    "Fahrregel: Als überholend gilt, wer sich von hinten so nähert, "
                    "dass bei Nacht nur das Hecklicht erkennbar wäre (Art. 46 "
                    "Abs. 2); RNL Art. 63 Abs. 2 nennt den Winkel — mehr als 22° 30' "
                    "achterlicher als querab, kein Seitenlicht sichtbar. Die "
                    "Geometrie der Lichter ist die Geometrie der Ausweichpflicht."
                ),
            },
            "it": {
                "title": "Fanali di notte: un codice di angoli, non un elenco da memorizzare",
                "body": (
                    "I fanali non descrivono il battello: suddividono l'orizzonte. "
                    "Ogni genere di fanale copre un arco preciso (ONI art. 18a, "
                    "ripreso alla lettera dal RNL art. 21), e questi archi si "
                    "completano esattamente — per questo si può dedurre ciò che si "
                    "vede invece di impararlo a memoria.\n\n"
                    "— Fanale d'albero: bianco, visibile dal davanti su 225°, cioè "
                    "112° 30' per lato.\n"
                    "— Fanali laterali: verde a tribordo, rosso a babordo, ciascuno "
                    "visibile dal davanti su 112° 30' del proprio lato.\n"
                    "— Fanale di poppa: bianco, visibile da dietro su 135°, cioè "
                    "67° 30' per lato.\n"
                    "— Fanale visibile per tutto l'orizzonte: 360°.\n\n"
                    "Due addizioni valgono l'intera tabella: 112° 30' + 112° 30' = "
                    "225°, l'arco del fanale d'albero; e 225° + 135° = 360°, "
                    "l'orizzonte intero. Un fanale laterale combinato riunisce i due "
                    "fanali laterali in un'unica lanterna; un fanale d'albero "
                    "tricolore vi aggiunge il fanale di poppa (art. 18a cpv. 3 e "
                    "5).\n\n"
                    "Da qui la lettura inversa, quella che serve di notte: entrambi i "
                    "fanali laterali insieme — si è nel suo settore prodiero; un solo "
                    "rosso o un solo verde — se ne vede il fianco; solo il bianco di "
                    "poppa — le si è dietro.\n\n"
                    "Ciò che ogni battello porta segue una scala di semplificazione:\n"
                    "— Battello motorizzato in navigazione, di notte e in caso di "
                    "scarsa visibilità: fanale d'albero, fanali laterali separati, "
                    "fanale di poppa (art. 24 cpv. 1).\n"
                    "— Imbarcazioni sportive e da diporto motorizzate, e battelli a "
                    "vela che navigano a motore: quattro combinazioni a scelta, dal "
                    "corredo completo al fanale laterale combinato con un fanale "
                    "bianco visibile per tutto l'orizzonte (art. 24 cpv. 3).\n"
                    "— Battelli a vela che navigano soltanto a vela: fanali laterali "
                    "e fanale di poppa, oppure fanale laterale combinato e fanale di "
                    "poppa, oppure fanale d'albero tricolore, oppure un fanale bianco "
                    "visibile per tutto l'orizzonte (art. 25 cpv. 2); in aggiunta due "
                    "fanali sovrapposti, rosso sopra verde, ma non insieme a un "
                    "tricolore (art. 25 cpv. 3).\n"
                    "— Natante non motorizzato: un fanale ordinario bianco visibile "
                    "per tutto l'orizzonte; sui battelli a remi può essere a luce "
                    "lampeggiante (art. 25 cpv. 1).\n"
                    "— Potenza propulsiva non superiore a 6 kW, oppure scafo di al "
                    "massimo 7 m e velocità di al massimo 7 nodi iscritta nella "
                    "licenza di navigazione: basta un solo fanale bianco visibile per "
                    "tutto l'orizzonte (art. 24 cpv. 5).\n"
                    "— In stazionamento di notte: fanale ordinario bianco visibile "
                    "per tutto l'orizzonte, salvo se ormeggiato alla riva o in un "
                    "posto di stazionamento ufficialmente autorizzato (art. 26 "
                    "cpv. 1).\n\n"
                    "Infine i fanali non sono solo una firma: definiscono una regola "
                    "di rotta. È sorpassante chi si avvicina da dietro al punto che, "
                    "di notte, vedrebbe soltanto il fanale di poppa (art. 46 cpv. 2); "
                    "il RNL art. 63 cpv. 2 ne dà l'angolo — più di 22° 30' a poppavia "
                    "del traverso, nessun fanale laterale visibile. La geometria dei "
                    "fanali è la geometria delle precedenze."
                ),
            },
            "en": {
                "title": "Lights at night: an angle code, not a list to memorise",
                "body": (
                    "Lights don't describe the boat — they slice up the horizon. Each "
                    "type of light covers a fixed arc (ONI art. 18a, reproduced word "
                    "for word in RNL art. 21), and those arcs complement each other "
                    "exactly. That is what lets you work out what you are seeing "
                    "instead of learning it by heart.\n\n"
                    "— Masthead light: white, visible from ahead over 225°, i.e. "
                    "112° 30' on each side.\n"
                    "— Sidelights: green to starboard, red to port, each visible from "
                    "ahead over 112° 30' on its own side.\n"
                    "— Sternlight: white, visible from astern over 135°, i.e. "
                    "67° 30' on each side.\n"
                    "— All-round light: 360°.\n\n"
                    "Two sums replace the whole table: 112° 30' + 112° 30' = 225°, "
                    "the masthead arc; and 225° + 135° = 360°, the full horizon. A "
                    "bicolour light combines both sidelights in one lantern; a "
                    "tricolour masthead light adds the sternlight to them (art. 18a, "
                    "para. 3 and 5).\n\n"
                    "Hence the reverse reading, the one that matters at night: both "
                    "sidelights at once — you are in her forward sector; a single red "
                    "or a single green — you are looking at her side; white "
                    "sternlight alone — you are behind her.\n\n"
                    "What each boat must carry then follows a ladder of "
                    "simplification:\n"
                    "— Powered boat under way, at night and in restricted "
                    "visibility: masthead light, separate sidelights, sternlight "
                    "(art. 24, para. 1).\n"
                    "— Powered sport and pleasure craft, and sailing boats under "
                    "engine: four permitted combinations, from the full set to a "
                    "bicolour light with an all-round white light (art. 24, "
                    "para. 3).\n"
                    "— Sailing boat under sail alone: sidelights and sternlight, or "
                    "bicolour and sternlight, or a tricolour light, or an all-round "
                    "white light (art. 25, para. 2); two vertical all-round lights, "
                    "red above green, may be added — but not together with a "
                    "tricolour (art. 25, para. 3).\n"
                    "— Unpowered boat: an ordinary all-round white light; on a "
                    "rowing boat it may be a flashing light (art. 25, para. 1).\n"
                    "— Propulsion of 6 kW or less, or a hull of 7 m or less with a "
                    "speed of 7 knots or less entered in the navigation permit: a "
                    "single all-round white light is enough (art. 24, para. 5).\n"
                    "— Berthed at night: an ordinary all-round white light, except "
                    "when moored to the bank or at an officially authorised berth "
                    "(art. 26, para. 1).\n\n"
                    "Finally, the lights are not just a signature — they define a "
                    "steering rule. You are overtaking if you approach from astern "
                    "so that at night only her sternlight would be visible (art. 46, "
                    "para. 2); RNL art. 63, para. 2 gives the angle — more than "
                    "22° 30' abaft the beam, with neither sidelight in view. The "
                    "geometry of the lights is the geometry of who gives way."
                ),
            },
        },
    },
    {
        "principle": "give-way",
        "kind": "principle",
        # Swiss inland (ONI federal + RNL Léman). The maritime COLREG hierarchy is
        # different (Rule 18), so this must never load into a sea bank.
        "applies": {"ch"},
        "prov": {
            "ref": "ONI art. 41, 43, 44, 45, 46, 47 — règles de route "
                   "(RNL art. 62, 63, 64 pour le Léman)",
            "source": "Ordonnance sur la navigation intérieure (ONI), RS 747.201.1",
            "url": "https://www.fedlex.admin.ch/eli/cc/1979/337_337_337/fr",
            "as_of": "2022-01-01",
            "licence": "Public domain — Swiss federal law (freely reusable).",
        },
        "lang": {
            "fr": {
                "title": "Priorités : d'abord le rang, ensuite seulement la géométrie",
                "body": (
                    "Presque toutes les erreurs de priorité viennent d'un ordre "
                    "inversé. On regarde d'abord qui vient de tribord, alors que le "
                    "droit suisse pose une hiérarchie AVANT toute considération "
                    "d'angle. Trois questions, toujours dans cet ordre.\n\n"
                    "1. Une règle spéciale prime-t-elle ? Tout bateau s'écarte de la "
                    "route des bateaux qui montrent le feu bleu scintillant ou "
                    "émettent les signaux sonores des services d'intervention ; au "
                    "besoin, on réduit sa vitesse ou l'on s'arrête (ONI art. 43).\n\n"
                    "2. Les deux bateaux sont-ils du même rang ? En cas de rencontre "
                    "et de dépassement, l'échelle de l'art. 44 s'applique d'abord — "
                    "chacun s'écarte de tout ce qui est au-dessus de lui :\n"
                    "— les bateaux prioritaires (les bateaux en service régulier "
                    "l'emportant toujours sur les autres prioritaires) ;\n"
                    "— les bateaux à marchandises ;\n"
                    "— les bateaux de pêche professionnelle portant les signaux de "
                    "l'art. 31 ;\n"
                    "— les bateaux à voile ;\n"
                    "— les bateaux à rames, dont s'écartent les bateaux motorisés ;\n"
                    "— et tout en bas, les planches à voile et les kitesurfs, qui "
                    "s'écartent de tous les autres.\n"
                    "Les convois remorqués comptent comme prioritaires, les convois "
                    "poussés comme bateaux à marchandises (art. 44, al. 2).\n\n"
                    "3. Seulement si aucun des deux n'est tenu de s'écarter selon "
                    "l'art. 44, la géométrie tranche :\n"
                    "— Routes qui se croisent : le bateau à moteur qui voit l'autre "
                    "par tribord s'écarte (art. 45, al. 1).\n"
                    "— Routes opposées ou à peu près : chacun vient sur tribord pour "
                    "passer bâbord sur bâbord ; en cas de doute, il faut admettre "
                    "qu'on est dans cette situation (art. 45, al. 2). Pour un "
                    "accostage, on peut demander le passage tribord sur tribord par "
                    "«deux sons brefs», auxquels l'autre répond de même (al. 3).\n"
                    "— Dépassement : celui qui rattrape s'écarte (art. 46, al. 1). "
                    "Rattrape celui qui s'approche par l'arrière au point de ne voir, "
                    "de nuit, que le feu de poupe — en cas de doute, on se considère "
                    "comme rattrapant (al. 2). Et aucun changement ultérieur de "
                    "position ne transforme le dépassement en croisement ni ne "
                    "libère de l'obligation (al. 3) : c'est la situation de départ "
                    "qui commande jusqu'à ce qu'on soit franchement passé.\n"
                    "— Voile contre voile : vent d'un bord différent, celui qui "
                    "reçoit le vent de bâbord s'écarte ; vent du même bord, celui qui "
                    "est au vent s'écarte. Le côté du vent est celui opposé au bord "
                    "où est portée la grand-voile (art. 47).\n\n"
                    "Reste la manière de s'écarter, qui vaut dans tous les cas : "
                    "régler sa vitesse pour pouvoir satisfaire en tout temps à ses "
                    "obligations, exécuter la manœuvre franchement et suffisamment "
                    "tôt, et ne jamais créer par un changement de route ou de vitesse "
                    "le danger d'abordage qu'on prétend éviter (art. 41).\n\n"
                    "Sur le Léman, le RNL reprend la même architecture : priorités à "
                    "l'art. 64, rencontre à l'art. 62, dépassement à l'art. 63 — "
                    "lequel chiffre l'angle du rattrapant à plus de 22° 30' sur "
                    "l'arrière du travers."
                ),
            },
            "de": {
                "title": "Ausweichpflicht: zuerst der Rang, erst dann die Geometrie",
                "body": (
                    "Fast alle Vorfahrtsfehler entstehen aus einer vertauschten "
                    "Reihenfolge. Man schaut zuerst, wer von Steuerbord kommt — dabei "
                    "stellt das Schweizer Recht eine Rangordnung VOR jede "
                    "Winkelbetrachtung. Drei Fragen, immer in dieser Reihenfolge.\n\n"
                    "1. Geht eine Sonderregel vor? Jedes Schiff weicht Schiffen aus, "
                    "die das blaue Funkellicht führen oder die Schallsignale der "
                    "Interventionsdienste geben; nötigenfalls verlangsamen "
                    "nichtamtliche Boote oder halten an (BSV Art. 43).\n\n"
                    "2. Stehen beide Schiffe im selben Rang? Beim Begegnen und "
                    "Überholen gilt zuerst die Stufenleiter von Art. 44 — jedes "
                    "Schiff weicht allem aus, was über ihm steht:\n"
                    "— Vorrangschiffe (Kursschiffe haben dabei immer den Vortritt vor "
                    "anderen Vorrangschiffen);\n"
                    "— Güterschiffe;\n"
                    "— Schiffe der Berufsfischer, die die Zeichen nach Art. 31 "
                    "führen;\n"
                    "— Segelschiffe;\n"
                    "— Ruderboote, denen Schiffe mit Maschinenantrieb ausweichen;\n"
                    "— und zuunterst Segelbretter und Drachensegelbretter, die allen "
                    "anderen Schiffen ausweichen.\n"
                    "Schleppverbände gelten als Vorrangschiffe, Schubverbände als "
                    "Güterschiffe (Art. 44 Abs. 2).\n\n"
                    "3. Nur wenn keines der beiden nach Art. 44 ausweichpflichtig "
                    "ist, entscheidet die Geometrie:\n"
                    "— Kreuzende Kurse: Es weicht das Motorschiff aus, welches das "
                    "andere an Steuerbord hat (Art. 45 Abs. 1).\n"
                    "— Entgegengesetzte oder nahezu entgegengesetzte Kurse: Jedes "
                    "hält nach Steuerbord, um Backbord an Backbord vorbeizufahren; im "
                    "Zweifel ist anzunehmen, dass diese Lage besteht (Art. 45 "
                    "Abs. 2). Bei Landemanövern kann die Vorbeifahrt Steuerbord an "
                    "Steuerbord mit «zwei kurzen Tönen» verlangt werden, die das "
                    "andere Schiff gleich beantwortet (Abs. 3).\n"
                    "— Überholen: Das überholende Schiff weicht aus (Art. 46 "
                    "Abs. 1). Als überholend gilt, wer sich von hinten so nähert, "
                    "dass bei Nacht nur das Hecklicht erkennbar wäre — im Zweifel "
                    "gilt man als überholend (Abs. 2). Und keine spätere Änderung der "
                    "gegenseitigen Lage macht daraus ein Kreuzen oder entbindet von "
                    "der Pflicht (Abs. 3): Die Ausgangslage bindet, bis man klar "
                    "vorbei ist.\n"
                    "— Segel gegen Segel: Wind von verschiedenen Seiten — das Schiff "
                    "mit Wind von Backbord weicht aus; Wind von derselben Seite — das "
                    "luvwärtige Schiff weicht aus. Die Luvseite ist die dem gesetzten "
                    "Grosssegel gegenüberliegende Seite (Art. 47).\n\n"
                    "Bleibt das Wie, das immer gilt: die Geschwindigkeit so regeln, "
                    "dass man jederzeit seinen Pflichten im Verkehr nachkommen kann, "
                    "jedes Manöver eindeutig und rechtzeitig ausführen, und durch "
                    "Kurs- oder Geschwindigkeitsänderungen nie die "
                    "Zusammenstossgefahr schaffen, die man vermeiden will (Art. "
                    "41).\n\n"
                    "Auf dem Genfersee führt das RNL dieselbe Architektur: Vorrang in "
                    "Art. 64, Begegnen in Art. 62, Überholen in Art. 63 — dort mit "
                    "dem Winkel von mehr als 22° 30' achterlicher als querab."
                ),
            },
            "it": {
                "title": "Precedenze: prima il rango, solo dopo la geometria",
                "body": (
                    "Quasi tutti gli errori di precedenza nascono da un ordine "
                    "invertito. Si guarda subito chi viene da dritta, mentre il "
                    "diritto svizzero pone una gerarchia PRIMA di ogni "
                    "considerazione d'angolo. Tre domande, sempre in quest'ordine.\n\n"
                    "1. Prevale una regola speciale? Ogni natante si allontana dalla "
                    "rotta dei battelli che portano la luce blu scintillante o che "
                    "emettono i segnali sonori dei servizi d'intervento; se "
                    "necessario si riduce la velocità o ci si ferma (ONI art. 43).\n\n"
                    "2. I due battelli sono dello stesso rango? In caso d'incrocio o "
                    "di sorpasso vale anzitutto la scala dell'art. 44 — ciascuno si "
                    "allontana da tutto ciò che gli sta sopra:\n"
                    "— i battelli con precedenza (i battelli in servizio regolare "
                    "prevalgono sempre sugli altri battelli con precedenza);\n"
                    "— i battelli per il trasporto di merci;\n"
                    "— le imbarcazioni dei pescatori professionisti che portano i "
                    "segnali dell'art. 31;\n"
                    "— i battelli a vela;\n"
                    "— i battelli a remi, dai quali si allontanano i battelli a "
                    "motore;\n"
                    "— e in fondo le tavole a vela e i kite surf, che si allontanano "
                    "da tutti gli altri natanti.\n"
                    "I convogli rimorchiati contano come battelli con precedenza, "
                    "quelli spinti come battelli per il trasporto di merci (art. 44 "
                    "cpv. 2).\n\n"
                    "3. Solo se nessuno dei due è tenuto ad allontanarsi ai sensi "
                    "dell'art. 44, decide la geometria:\n"
                    "— Rotte che si incrociano: si allontana il battello a motore che "
                    "vede l'altro da dritta (art. 45 cpv. 1).\n"
                    "— Rotte direttamente o quasi opposte: ognuno viene a dritta per "
                    "passare sinistra su sinistra; in caso di dubbio si presume che "
                    "la situazione esista (art. 45 cpv. 2). Nelle manovre d'attracco "
                    "si può chiedere il passaggio dritta su dritta con «due suoni "
                    "brevi», ai quali l'altro risponde allo stesso modo (cpv. 3).\n"
                    "— Sorpasso: si allontana chi sorpassa (art. 46 cpv. 1). È "
                    "sorpassante chi si avvicina da dietro al punto che di notte "
                    "vedrebbe soltanto il fanale di poppa — in caso di dubbio ci si "
                    "considera sorpassanti (cpv. 2). E nessun cambiamento successivo "
                    "della posizione trasforma il sorpasso in un incrocio né libera "
                    "dall'obbligo (cpv. 3): vale la situazione iniziale finché non si "
                    "è passati del tutto.\n"
                    "— Vela contro vela: vento da lati diversi, si allontana chi "
                    "riceve il vento da sinistra; vento dallo stesso lato, si "
                    "allontana quello sopravvento. Il lato del vento è quello opposto "
                    "al lato dove è portata la randa (art. 47).\n\n"
                    "Resta il come, valido in ogni caso: regolare la velocità per "
                    "poter soddisfare in ogni momento i propri obblighi, eseguire "
                    "ogni manovra in modo netto e sufficientemente per tempo, e non "
                    "creare mai con un cambiamento di rotta o di velocità il pericolo "
                    "di collisione che si vuole evitare (art. 41).\n\n"
                    "Sul Lemano il RNL riprende la stessa architettura: precedenze "
                    "all'art. 64, incontro all'art. 62, sorpasso all'art. 63 — che "
                    "fissa l'angolo del sorpassante a più di 22° 30' a poppavia del "
                    "traverso."
                ),
            },
            "en": {
                "title": "Right of way: rank first, geometry only afterwards",
                "body": (
                    "Almost every right-of-way mistake comes from reversing the "
                    "order. People look first at who is coming from starboard, "
                    "whereas Swiss law sets a hierarchy BEFORE any question of angle. "
                    "Three questions, always in this order.\n\n"
                    "1. Does a special rule pre-empt? Every boat keeps clear of boats "
                    "showing the blue flashing light or sounding the emergency-service "
                    "signals; non-official craft slow down or stop if necessary (ONI "
                    "art. 43).\n\n"
                    "2. Are the two boats of the same rank? When meeting and "
                    "overtaking, the ladder of art. 44 applies first — each boat "
                    "keeps clear of everything above it:\n"
                    "— priority boats (scheduled-service boats always take precedence "
                    "over other priority boats);\n"
                    "— cargo boats;\n"
                    "— professional fishing boats showing the art. 31 signals;\n"
                    "— sailing boats;\n"
                    "— rowing boats, which powered boats keep clear of;\n"
                    "— and at the bottom sailboards and kitesurfs, which keep clear "
                    "of every other boat.\n"
                    "Towed convoys count as priority boats, pushed convoys as cargo "
                    "boats (art. 44, para. 2).\n\n"
                    "3. Only if neither boat is bound to keep clear under art. 44 "
                    "does geometry decide:\n"
                    "— Crossing courses: the powered boat that has the other on its "
                    "starboard side keeps clear (art. 45, para. 1).\n"
                    "— Opposite or nearly opposite courses: each turns to starboard "
                    "so as to pass port to port; in case of doubt you must assume you "
                    "are in that situation (art. 45, para. 2). For a berthing "
                    "manoeuvre a starboard-to-starboard passage may be requested with "
                    "\"two short blasts\", which the other answers alike (para. 3).\n"
                    "— Overtaking: the overtaking boat keeps clear (art. 46, "
                    "para. 1). You are overtaking if you approach from astern so that "
                    "at night only the sternlight would be visible — in case of doubt "
                    "you count as overtaking (para. 2). And no later change of "
                    "relative position turns it into a crossing or releases you from "
                    "the duty (para. 3): the opening situation binds until you are "
                    "finally past and clear.\n"
                    "— Sail against sail: wind on different sides, the boat with the "
                    "wind on its port side keeps clear; wind on the same side, the "
                    "windward boat keeps clear. The windward side is the side "
                    "opposite the one on which the mainsail is carried (art. 47).\n\n"
                    "Then the manner of keeping clear, which always applies: regulate "
                    "your speed so that you can meet your obligations at all times, "
                    "carry out every manoeuvre decisively and early enough, and never "
                    "create through a change of course or speed the collision danger "
                    "you are trying to avoid (art. 41).\n\n"
                    "On Lake Geneva the RNL follows the same architecture: priorities "
                    "in art. 64, meeting in art. 62, overtaking in art. 63 — which "
                    "puts a figure on the overtaking angle, more than 22° 30' abaft "
                    "the beam."
                ),
            },
        },
    },
    {
        "principle": "nav-lights",
        "kind": "principle",
        # Maritime: COLREG 1972, published in French law as the RIPAM. Applies to
        # the international bank and to the French *coastal* option — never to the
        # inland banks (RGP / ONI light carriage differs).
        "applies": {"int", "fr_cotiere"},
        "prov": {
            "ref": "COLREG 1972 / RIPAM — Rules 13(b), 14(b), 20, 21, 22, 23, 25(d), "
                   "26(b), 29(a), 30",
            "source": "COLREG — International Regulations for Preventing Collisions "
                      "at Sea, 1972 (publié en droit français comme RIPAM)",
            "url": "https://www.navcen.uscg.gov/sites/default/files/pdf/navRules/"
                   "navrules.pdf",
            "as_of": None,
            "licence": "Public domain — US Government work (17 USC §105); French "
                       "publication: Licence Ouverte / Etalab 2.0.",
        },
        "lang": {
            "en": {
                "title": "Lights at sea: the arcs tile the horizon, so what you see is where you are",
                "body": (
                    "Rule 21 does not describe lamps, it partitions the horizon — and "
                    "the partition is what makes the whole system reconstructable.\n\n"
                    "— Sidelights: green to starboard, red to port, each showing over "
                    "112.5°, from right ahead to 22.5° abaft the beam on its side "
                    "(Rule 21(b)).\n"
                    "— Sternlight: white, showing over 135°, that is 67.5° from right "
                    "aft on each side (Rule 21(c)).\n"
                    "— Masthead light: white, over 225° (Rule 21(a)) — exactly the "
                    "two sidelight arcs added together.\n"
                    "225° + 135° = 360°: the arcs tile the horizon with no gap and no "
                    "overlap. So the lights you see fix your position relative to the "
                    "other vessel, and that position is what selects the steering "
                    "rule.\n\n"
                    "Read it in that direction:\n"
                    "— Masthead lights in a line or nearly in a line, and/or both "
                    "sidelights: head-on (Rule 14(b)).\n"
                    "— One sidelight only: you are looking at her side — a crossing "
                    "situation.\n"
                    "— The sternlight alone, no sidelight: you are more than 22.5° "
                    "abaft her beam, which is the definition of overtaking "
                    "(Rule 13(b)).\n\n"
                    "When the rules apply: from sunset to sunrise (Rule 20(b)), in "
                    "all weathers (Rule 20(a)); shapes are shown by day (Rule "
                    "20(d)).\n\n"
                    "Carriage, from the general case downwards:\n"
                    "— Power-driven vessel under way: masthead light forward, "
                    "sidelights, sternlight (Rule 23(a)).\n"
                    "— Power-driven vessel under 7 m whose speed does not exceed 7 "
                    "knots: an all-round white light and, if practicable, sidelights "
                    "(Rule 23(d)(ii)).\n"
                    "— Sailing vessel under 7 m that cannot show the prescribed "
                    "lights: an electric torch or lighted lantern showing a white "
                    "light, ready at hand to be shown in time to prevent collision "
                    "(Rule 25(d)(i)).\n"
                    "— Vessel trawling and making way: green over white all-round "
                    "lights, plus sidelights and sternlight (Rule 26(b)).\n"
                    "— Vessel on pilotage duty: white over red all-round at the "
                    "masthead, plus sidelights and sternlight when under way "
                    "(Rule 29(a)).\n"
                    "— Vessel aground: the anchor lights plus two all-round red "
                    "lights in a vertical line, and by day three balls in a vertical "
                    "line (Rule 30(d)). A vessel under 7 m at anchor need not show "
                    "them when clear of a narrow channel, fairway, anchorage or where "
                    "other vessels normally navigate (Rule 30(e)).\n\n"
                    "Minimum ranges scale with length (Rule 22): on a vessel of 50 m "
                    "or more the masthead light must be visible at 6 miles; between "
                    "12 and 50 m, sidelights, sternlight, towing light and all-round "
                    "lights at 2 miles; and a masthead light on a vessel under 20 m "
                    "need only reach 3 miles."
                ),
            },
            "fr": {
                "title": "Feux en mer : les arcs pavent l'horizon, donc ce qu'on voit dit où l'on est",
                "body": (
                    "La règle 21 ne décrit pas des lanternes, elle partage "
                    "l'horizon — et c'est ce partage qui rend tout le système "
                    "reconstituable.\n\n"
                    "— Feux de côté : vert à tribord, rouge à bâbord, chacun sur "
                    "112,5°, de l'avant jusqu'à 22,5° sur l'arrière du travers de son "
                    "bord (règle 21(b)).\n"
                    "— Feu de poupe : blanc, sur 135°, soit 67,5° de chaque bord "
                    "depuis l'arrière (règle 21(c)).\n"
                    "— Feu de tête de mât : blanc, sur 225° (règle 21(a)) — "
                    "exactement la somme des deux arcs des feux de côté.\n"
                    "225° + 135° = 360° : les arcs pavent l'horizon sans trou ni "
                    "recouvrement. Les feux qu'on aperçoit fixent donc notre position "
                    "par rapport à l'autre navire, et c'est cette position qui "
                    "désigne la règle de barre applicable.\n\n"
                    "À lire dans ce sens :\n"
                    "— Feux de tête de mât alignés ou presque, et/ou les deux feux de "
                    "côté : routes directement opposées (règle 14(b)).\n"
                    "— Un seul feu de côté : on voit son flanc — routes qui se "
                    "croisent.\n"
                    "— Le feu de poupe seul, aucun feu de côté : on est à plus de "
                    "22,5° sur l'arrière de son travers, ce qui est la définition "
                    "même du navire qui en rattrape un autre (règle 13(b)).\n\n"
                    "Quand les règles s'appliquent : du coucher au lever du soleil "
                    "(règle 20(b)), par tous les temps (règle 20(a)) ; les marques de "
                    "jour se montrent de jour (règle 20(d)).\n\n"
                    "Le port des feux, du cas général vers les cas allégés :\n"
                    "— Navire à propulsion mécanique faisant route : feu de tête de "
                    "mât à l'avant, feux de côté, feu de poupe (règle 23(a)).\n"
                    "— Navire à moteur de moins de 7 m dont la vitesse n'excède pas 7 "
                    "nœuds : un feu blanc visible sur tout l'horizon et, si possible, "
                    "les feux de côté (règle 23(d)(ii)).\n"
                    "— Voilier de moins de 7 m ne pouvant montrer les feux prescrits "
                    ": une lampe électrique ou un fanal à feu blanc, prêt à être "
                    "montré à temps pour prévenir l'abordage (règle 25(d)(i)).\n"
                    "— Navire au chalut en route : feux visibles sur tout l'horizon "
                    "vert au-dessus de blanc, plus feux de côté et feu de poupe "
                    "(règle 26(b)).\n"
                    "— Navire en service de pilotage : blanc au-dessus de rouge en "
                    "tête de mât, plus feux de côté et feu de poupe lorsqu'il fait "
                    "route (règle 29(a)).\n"
                    "— Navire échoué : les feux de mouillage plus deux feux rouges "
                    "superposés, et de jour trois boules en ligne verticale (règle "
                    "30(d)). Un navire de moins de 7 m au mouillage en est dispensé "
                    "s'il n'est ni dans un chenal étroit, ni dans un chenal d'accès, "
                    "ni dans un mouillage, ni là où les navires naviguent "
                    "habituellement (règle 30(e)).\n\n"
                    "Les portées minimales croissent avec la longueur (règle 22) : "
                    "sur un navire de 50 m ou plus, le feu de tête de mât porte à 6 "
                    "milles ; entre 12 et 50 m, les feux de côté, le feu de poupe, le "
                    "feu de remorquage et les feux visibles sur tout l'horizon portent "
                    "à 2 milles ; et sur un navire de moins de 20 m, le feu de tête "
                    "de mât ne doit porter qu'à 3 milles."
                ),
            },
        },
    },
    {
        "principle": "give-way",
        "kind": "principle",
        # Maritime COLREG/RIPAM hierarchy (Rule 18) — deliberately NOT the inland
        # ladder of ONI art. 44 / RGP, so this never loads into an inland bank.
        "applies": {"int", "fr_cotiere"},
        "prov": {
            "ref": "COLREG 1972 / RIPAM — Rules 5, 6, 7, 8, 9, 12, 13, 14, 15, 17, "
                   "18, 19",
            "source": "COLREG — International Regulations for Preventing Collisions "
                      "at Sea, 1972 (publié en droit français comme RIPAM)",
            "url": "https://www.navcen.uscg.gov/sites/default/files/pdf/navRules/"
                   "navrules.pdf",
            "as_of": None,
            "licence": "Public domain — US Government work (17 USC §105); French "
                       "publication: Licence Ouverte / Etalab 2.0.",
        },
        "lang": {
            "en": {
                "title": "Who gives way at sea: a fixed sequence, not a table of cases",
                "body": (
                    "The COLREGs are not a list of situations to memorise — they are "
                    "a sequence you run in order. Each step only makes sense once the "
                    "previous one is answered.\n\n"
                    "1. Look out. By sight and hearing and by all available means "
                    "appropriate in the prevailing circumstances, so as to make a "
                    "full appraisal of the situation and of the risk of collision "
                    "(Rule 5).\n\n"
                    "2. Safe speed, so that you can take proper and effective action "
                    "and be stopped within a distance appropriate to the "
                    "circumstances — judged from visibility, traffic density, and "
                    "your own manoeuvrability and stopping distance (Rule 6). In or "
                    "near restricted visibility, that requirement applies to every "
                    "vessel (Rule 19(b)).\n\n"
                    "3. Is there risk of collision? Yes if the compass bearing of the "
                    "approaching vessel does not appreciably change; and yes whenever "
                    "there is any doubt. Assumptions must not be made on scanty "
                    "information, especially scanty radar information (Rule 7).\n\n"
                    "4. Which situation is it? Overtaking is decided first, because "
                    "it overrides the rest: a vessel coming up from more than 22.5° "
                    "abaft the beam is overtaking, must keep out of the way until "
                    "finally past and clear, must assume she is overtaking if in any "
                    "doubt, and is not released by any later change of bearing "
                    "(Rule 13). Otherwise: head-on, each alters course to starboard "
                    "to pass port to port (Rule 14); crossing, the vessel which has "
                    "the other on her own starboard side keeps out of the way "
                    "(Rule 15).\n\n"
                    "5. Between vessels of different kinds, Rule 18 ranks them: a "
                    "power-driven vessel under way keeps out of the way of a vessel "
                    "not under command, a vessel restricted in her ability to "
                    "manoeuvre, a vessel engaged in fishing, and a sailing vessel. A "
                    "seaplane on the water keeps well clear of all vessels and avoids "
                    "impeding their navigation (Rule 18(e)).\n\n"
                    "Between two sailing vessels, Rule 12: with the wind on different "
                    "sides, the one with the wind on the port side keeps out of the "
                    "way; with the wind on the same side, the windward vessel keeps "
                    "out of the way. The windward side is the side opposite to that "
                    "on which the mainsail is carried — for a square-rigged vessel, "
                    "opposite the largest fore-and-aft sail (Rule 12(b)).\n\n"
                    "6. In a narrow channel, keep to the starboard side of the "
                    "fairway; a vessel of less than 20 m and a sailing vessel must "
                    "not impede a vessel which can safely navigate only within that "
                    "channel (Rule 9).\n\n"
                    "7. Act. Any action shall be positive, made in ample time and "
                    "with due regard to good seamanship; an alteration large enough "
                    "to be readily apparent to another vessel visually or by radar, "
                    "avoiding a succession of small alterations (Rule 8). And the "
                    "duty is not one-sided: the stand-on vessel keeps her course and "
                    "speed, but may act by her own manoeuvre alone as soon as it "
                    "becomes apparent that the give-way vessel is not taking "
                    "appropriate action (Rule 17)."
                ),
            },
            "fr": {
                "title": "Qui s'écarte en mer : une séquence fixe, pas un tableau de cas",
                "body": (
                    "Le RIPAM n'est pas une liste de situations à mémoriser : c'est "
                    "une séquence qu'on déroule dans l'ordre. Chaque étape ne prend "
                    "son sens qu'une fois la précédente tranchée.\n\n"
                    "1. Veiller. Par la vue et l'ouïe et par tous les moyens "
                    "disponibles adaptés aux circonstances, afin d'apprécier "
                    "pleinement la situation et le risque d'abordage (règle 5).\n\n"
                    "2. Vitesse de sécurité, permettant de prendre des mesures "
                    "efficaces et de s'arrêter sur une distance adaptée aux "
                    "circonstances — appréciée d'après la visibilité, la densité du "
                    "trafic, et sa propre manœuvrabilité et distance d'arrêt "
                    "(règle 6). Par visibilité réduite ou à ses abords, l'exigence "
                    "vaut pour tout navire (règle 19(b)).\n\n"
                    "3. Y a-t-il risque d'abordage ? Oui si le relèvement au compas "
                    "du navire qui s'approche ne change pas de manière appréciable ; "
                    "oui également en cas de doute. On ne fait pas d'hypothèses sur "
                    "la base de renseignements insuffisants, en particulier "
                    "radar (règle 7).\n\n"
                    "4. Quelle situation ? Le rattrapage se tranche en premier, car "
                    "il prime le reste : un navire qui s'approche de plus de 22,5° "
                    "sur l'arrière du travers rattrape, doit s'écarter jusqu'à ce "
                    "qu'il soit franchement paré, doit se considérer comme rattrapant "
                    "en cas de doute, et n'est libéré par aucun changement ultérieur "
                    "de relèvement (règle 13) — même un voilier qui rattrape un "
                    "navire à moteur s'écarte. Sinon : routes directement opposées, "
                    "chacun vient sur tribord pour passer bâbord sur bâbord "
                    "(règle 14) ; routes qui se croisent, le navire qui voit l'autre "
                    "sur son tribord s'écarte (règle 15).\n\n"
                    "5. Entre navires de natures différentes, la règle 18 les "
                    "classe : un navire à propulsion mécanique faisant route s'écarte "
                    "d'un navire qui n'est pas maître de sa manœuvre, d'un navire à "
                    "capacité de manœuvre restreinte, d'un navire en train de pêcher "
                    "et d'un navire à voile. Un hydravion amerri se tient à l'écart "
                    "de tous les navires et évite de gêner leur navigation "
                    "(règle 18(e)).\n\n"
                    "Entre deux voiliers, la règle 12 : vent de bords différents, "
                    "celui qui reçoit le vent de bâbord s'écarte ; vent du même bord, "
                    "celui qui est au vent s'écarte. Le côté du vent est celui opposé "
                    "au bord où est portée la grand-voile — pour un navire à "
                    "gréement carré, le bord opposé à la plus grande voile "
                    "aurique (règle 12(b)).\n\n"
                    "6. Dans un chenal étroit, on serre le bord du chenal situé sur "
                    "sa droite (tribord) ; un navire de moins de 20 m et un voilier "
                    "ne doivent pas gêner le navire qui ne peut naviguer en sécurité "
                    "qu'à l'intérieur de ce chenal (règle 9).\n\n"
                    "7. Agir. Toute manœuvre doit être franche, exécutée largement à "
                    "temps et conformément aux bons usages maritimes ; un changement "
                    "assez ample pour être immédiatement perçu par l'autre navire, à "
                    "l'œil ou au radar, en évitant une succession de petits "
                    "changements (règle 8). Et l'obligation n'est pas unilatérale : "
                    "le navire privilégié maintient cap et vitesse, mais peut "
                    "manœuvrer seul dès qu'il devient évident que le navire qui doit "
                    "s'écarter ne prend pas les mesures appropriées (règle 17)."
                ),
            },
        },
    },
    {
        "principle": "waterway-signs",
        "kind": "principle",
        # Swiss inland signboards (ONI annexe 4). The French RGP and the German
        # inland codes carry their own boards, so this is ch-only.
        "applies": {"ch"},
        "prov": {
            "ref": "ONI art. 20, 36, 37, 39 et annexe 4 — signalisation de la voie "
                   "navigable",
            "source": "Ordonnance sur la navigation intérieure (ONI), RS 747.201.1",
            "url": "https://www.fedlex.admin.ch/eli/cc/1979/337_337_337/fr",
            "as_of": "2022-01-01",
            "licence": "Public domain — Swiss federal law (freely reusable).",
        },
        "lang": {
            "fr": {
                "title": "Signaux de la voie navigable : lire la famille avant le pictogramme",
                "body": (
                    "Un panneau se lit en deux temps. La FAMILLE dit quel genre "
                    "d'obligation il crée ; le pictogramme dit seulement de quelle "
                    "activité il s'agit. Les conducteurs doivent obéir aux "
                    "prescriptions et tenir compte des recommandations ou "
                    "indications portées par les signaux de l'annexe 4 (ONI "
                    "art. 36).\n\n"
                    "Les familles de l'annexe 4, telles que leurs légendes les "
                    "nomment :\n"
                    "— Interdiction : «interdiction de passer» (le signal général "
                    "d'interdiction), d'ancrer, de s'amarrer, de stationner, de "
                    "virer, de dépasser, de causer des remous…\n"
                    "— Obligation : prendre la direction de la flèche, s'arrêter "
                    "dans certaines conditions, ne pas dépasser la vitesse indiquée, "
                    "siffler, observer une vigilance particulière.\n"
                    "— Limitation : la hauteur, la largeur de la passe ou le tirant "
                    "d'eau sont limités ; la distance à tenir par rapport à la rive "
                    "est indiquée en mètres.\n"
                    "— Recommandation : une passe recommandée pour franchir un pont "
                    "(dans les deux sens ou dans le seul sens indiqué), se tenir "
                    "dans l'espace indiqué.\n"
                    "— Autorisation ou indication : autorisation de passer, de "
                    "stationner, arrêt pour la douane, bac.\n"
                    "Une fois la famille reconnue, la question «que dois-je faire ?» "
                    "est déjà tranchée : m'abstenir, exécuter, respecter une limite, "
                    "suivre un conseil, ou simplement noter une possibilité.\n\n"
                    "Les plans d'eau, eux, sont délimités par des flotteurs, pas par "
                    "des panneaux (art. 37) :\n"
                    "— Bouées jaunes sphériques : plan d'eau interdit à toute "
                    "navigation, au besoin complété par un panneau A.1.\n"
                    "— Mêmes bouées avec un panneau A.2, A.3 ou A.4 : interdit à "
                    "certaines catégories de bateaux seulement.\n"
                    "— Mêmes bouées avec des panneaux E.5 à terre : plan d'eau ou "
                    "couloir de départ ouvert au ski nautique et au wakesurfing ; "
                    "les bouées du couloir côté large sont deux fois plus grosses, "
                    "sommet rouge à gauche et vert à droite vu du large.\n\n"
                    "Deux détails qui tombent souvent : les panneaux et pavillons "
                    "mesurent au moins 60 cm de côté et les ballons au moins 30 cm "
                    "de diamètre (art. 20) ; et de nuit ou par temps bouché, des "
                    "installations fixes peuvent émettre les signaux sonores de "
                    "l'annexe 4 ou des feux à éclats jaunes, tandis que ponts et "
                    "obstacles portent des réflecteurs radar (art. 39)."
                ),
            },
            "de": {
                "title": "Schifffahrtszeichen: erst die Familie lesen, dann das Piktogramm",
                "body": (
                    "Ein Tafelzeichen liest man in zwei Schritten. Die FAMILIE sagt, "
                    "welche Art von Pflicht es begründet; das Piktogramm sagt nur, "
                    "worum es geht. Die Schiffsführer haben die Anweisungen zu "
                    "befolgen und die Empfehlungen oder Hinweise zu beachten, die "
                    "die Schifffahrtszeichen nach Anhang 4 anzeigen (BSV Art. 36).\n\n"
                    "Die Familien des Anhangs 4, wie ihre Legenden sie benennen:\n"
                    "— Verbot: Durchfahrt verboten (das allgemeine Verbotszeichen), "
                    "Ankern, Festmachen, Stillliegen, Wenden, Überholen, "
                    "schädlichen Wellenschlag verursachen…\n"
                    "— Gebot: die durch den Pfeil angezeigte Richtung nehmen, unter "
                    "bestimmten Bedingungen anhalten, die angegebene "
                    "Geschwindigkeit nicht überschreiten, ein Schallzeichen geben, "
                    "besondere Vorsicht walten lassen.\n"
                    "— Beschränkung: die Durchfahrtshöhe, die Durchfahrtsbreite oder "
                    "der Tiefgang sind begrenzt; der einzuhaltende Uferabstand ist "
                    "in Metern angegeben.\n"
                    "— Empfehlung: eine empfohlene Durchfahrt unter einer Brücke (in "
                    "beiden Richtungen oder nur in der angezeigten), sich im "
                    "bezeichneten Raum halten.\n"
                    "— Erlaubnis oder Hinweis: Durchfahrt erlaubt, Stillliegen "
                    "erlaubt, Halt für den Zoll, Fähre.\n"
                    "Ist die Familie erkannt, ist die Frage «was muss ich tun?» "
                    "schon beantwortet: unterlassen, ausführen, eine Grenze "
                    "einhalten, einem Rat folgen oder bloss eine Möglichkeit zur "
                    "Kenntnis nehmen.\n\n"
                    "Wasserflächen dagegen werden mit Schwimmkörpern abgegrenzt, "
                    "nicht mit Tafeln (Art. 37):\n"
                    "— Gelbe kugelförmige Schwimmkörper: für die Schifffahrt "
                    "gesperrte Wasserfläche, nötigenfalls mit einer Tafel A.1 "
                    "ergänzt.\n"
                    "— Dieselben Schwimmkörper mit Tafel A.2, A.3 oder A.4: nur für "
                    "bestimmte Schiffsarten gesperrt.\n"
                    "— Dieselben Schwimmkörper mit Tafeln E.5 am Ufer: für "
                    "Wasserskifahren und Wakesurfen zugelassene Wasserfläche oder "
                    "Startgasse; die seeseitigen Schwimmkörper der Startgasse haben "
                    "den doppelten Durchmesser, vom See her gesehen die linke mit "
                    "roter, die rechte mit grüner Spitze.\n\n"
                    "Zwei Details, die gern geprüft werden: Tafeln und Flaggen sind "
                    "mindestens 60 cm hoch und breit, Bälle haben mindestens 30 cm "
                    "Durchmesser (Art. 20); und bei Nacht oder unsichtigem Wetter "
                    "dürfen feste Anlagen die Schallzeichen des Anhangs 4 oder gelbe "
                    "Blitzlichter geben, während Brücken und Hindernisse "
                    "Radarreflektoren tragen (Art. 39)."
                ),
            },
            "it": {
                "title": "Segnali della via navigabile: prima la famiglia, poi il pittogramma",
                "body": (
                    "Una tavola si legge in due tempi. La FAMIGLIA dice che tipo di "
                    "obbligo crea; il pittogramma dice soltanto di quale attività si "
                    "tratta. I conduttori devono attenersi alle prescrizioni e tener "
                    "conto delle raccomandazioni o indicazioni portate dai segnali "
                    "dell'allegato 4 (ONI art. 36).\n\n"
                    "Le famiglie dell'allegato 4, come le nominano le loro "
                    "didascalie:\n"
                    "— Divieto: divieto di passaggio (il segnale generale di "
                    "divieto), di ancorare, di ormeggiare, di stazionare, di virare, "
                    "di sorpassare, di provocare onde dannose…\n"
                    "— Obbligo: prendere la direzione indicata dalla freccia, "
                    "fermarsi a certe condizioni, non superare la velocità indicata, "
                    "emettere un segnale acustico, osservare particolare "
                    "vigilanza.\n"
                    "— Limitazione: l'altezza o la larghezza del passaggio, oppure "
                    "il pescaggio, sono limitati; la distanza da tenere dalla riva è "
                    "indicata in metri.\n"
                    "— Raccomandazione: un passaggio raccomandato sotto un ponte "
                    "(nei due sensi o nel solo senso indicato), tenersi nello spazio "
                    "indicato.\n"
                    "— Autorizzazione o indicazione: passaggio autorizzato, "
                    "stazionamento autorizzato, fermata per la dogana, traghetto.\n"
                    "Riconosciuta la famiglia, la domanda «che cosa devo fare?» è "
                    "già risolta: astenermi, eseguire, rispettare un limite, seguire "
                    "un consiglio, o solo prendere atto di una possibilità.\n\n"
                    "Gli specchi d'acqua invece si delimitano con boe, non con "
                    "tavole (art. 37):\n"
                    "— Boe gialle di forma sferica: specchio d'acqua vietato a ogni "
                    "navigazione, se del caso completato da una tavola A.1.\n"
                    "— Le stesse boe con una tavola A.2, A.3 o A.4: vietato soltanto "
                    "a certe categorie di natanti.\n"
                    "— Le stesse boe con tavole E.5 sulla riva: specchio d'acqua o "
                    "corridoio di lancio aperto allo sci nautico e al wake surf.\n\n"
                    "Due dettagli che ricorrono spesso: le tavole e le bandiere "
                    "misurano almeno 60 cm di lato e i palloni almeno 30 cm di "
                    "diametro (art. 20); e di notte o in caso di scarsa visibilità "
                    "impianti fissi possono emettere i segnali acustici "
                    "dell'allegato 4 o luci gialle lampeggianti, mentre ponti e "
                    "ostacoli portano riflettori radar (art. 39)."
                ),
            },
            "en": {
                "title": "Waterway signs: read the family before the pictogram",
                "body": (
                    "A signboard is read in two steps. The FAMILY tells you what kind "
                    "of duty it creates; the pictogram only tells you which activity "
                    "is meant. Boatmasters must obey the instructions and heed the "
                    "recommendations or indications given by the signs of annex 4 "
                    "(ONI art. 36).\n\n"
                    "The families of annex 4, as its own captions name them:\n"
                    "— Prohibition: no passage (the general prohibition sign), no "
                    "anchoring, no mooring, no berthing, no turning, no overtaking, "
                    "no harmful wash…\n"
                    "— Obligation: take the direction of the arrow, stop under "
                    "certain conditions, do not exceed the speed shown, sound a "
                    "signal, keep a particular lookout.\n"
                    "— Limitation: the headroom, the width of the passage or the "
                    "draught is limited; the distance to keep off the bank is given "
                    "in metres.\n"
                    "— Recommendation: a recommended passage under a bridge (both "
                    "ways or only in the direction shown), keep within the marked "
                    "space.\n"
                    "— Authorisation or indication: passage permitted, berthing "
                    "permitted, stop for customs, ferry.\n"
                    "Once the family is recognised, \"what must I do?\" is already "
                    "settled: refrain, comply, respect a limit, follow advice, or "
                    "merely note a possibility.\n\n"
                    "Areas of water, by contrast, are delimited by floats rather "
                    "than boards (art. 37):\n"
                    "— Yellow spherical buoys: water closed to all navigation, if "
                    "needed completed by an A.1 board.\n"
                    "— The same buoys with an A.2, A.3 or A.4 board: closed only to "
                    "certain categories of boat.\n"
                    "— The same buoys with E.5 boards ashore: water or a start lane "
                    "open to water-skiing and wakesurfing; the seaward buoys of a "
                    "start lane are twice the diameter, red top to the left and "
                    "green top to the right seen from the open water.\n\n"
                    "Two details that come up often: boards and flags are at least "
                    "60 cm high and wide, balls at least 30 cm across (art. 20); and "
                    "by night or in restricted visibility fixed installations may "
                    "give the sound signals of annex 4 or yellow flashing lights, "
                    "while bridges and obstacles carry radar reflectors (art. 39)."
                ),
            },
        },
    },
    {
        "principle": "day-shapes",
        "kind": "principle",
        "applies": {"ch"},
        "prov": {
            "ref": "ONI art. 20, 27, 28, 29, 31, 32 — signalisation de jour "
                   "(ballons, pavillons)",
            "source": "Ordonnance sur la navigation intérieure (ONI), RS 747.201.1",
            "url": "https://www.fedlex.admin.ch/eli/cc/1979/337_337_337/fr",
            "as_of": "2022-01-01",
            "licence": "Public domain — Swiss federal law (freely reusable).",
        },
        "lang": {
            "fr": {
                "title": "Signaux de jour : chaque feu de nuit a son jumeau de jour",
                "body": (
                    "L'ordonnance dit deux fois la même chose, une fois pour la nuit "
                    "et une fois pour le jour. La couleur porte le message ; seul le "
                    "support change — un feu quand il fait sombre, un ballon ou un "
                    "pavillon quand il fait clair. Retenir les paires, c'est retenir "
                    "les deux tableaux d'un coup.\n\n"
                    "— Bateau prioritaire : de nuit un feu vert clair visible de tous "
                    "les côtés, si possible 1 m plus haut que le feu de mât ; de jour "
                    "un ballon VERT visible de tous les côtés (art. 27).\n"
                    "— Pêcheur professionnel pendant la pose et le relevage des "
                    "filets : de nuit un feu ordinaire jaune visible de tous les "
                    "côtés ; de jour un ballon JAUNE. Et de jour, la pêche à la "
                    "traîne se signale par un ballon BLANC (art. 31).\n"
                    "— Bateau à protéger des remous (mesures, recherches "
                    "hydrologiques, sauvetage) : de nuit un feu rouge au-dessus d'un "
                    "feu blanc ; de jour un pavillon moitié rouge en haut, moitié "
                    "blanc en bas — ou deux pavillons superposés, rouge sur blanc "
                    "(art. 28).\n"
                    "— Ancrages dangereux pour la navigation : de nuit deux feux "
                    "blancs superposés à au moins 1 m d'intervalle ; de jour deux "
                    "pavillons BLANCS superposés. Chaque ancrage isolé se signale de "
                    "nuit par des feux blancs, de jour par des flotteurs jaunes "
                    "(art. 29).\n"
                    "— Plongée subaquatique : le pavillon «A» du Code international "
                    "de signaux — un guidon à deux pointes, blanc côté hampe, bleu "
                    "de l'autre — hissé à terre, ou placé sur le bateau visible de "
                    "tous les côtés, et éclairé de nuit (art. 32).\n\n"
                    "Les dimensions sont prescrites, elles aussi : panneaux et "
                    "pavillons d'au moins 60 cm de côté, ballons d'au moins 30 cm de "
                    "diamètre ; un ballon peut être remplacé par un dispositif de "
                    "même apparence, à condition d'exclure toute confusion (art. 20)."
                ),
            },
            "de": {
                "title": "Tagzeichen: zu jedem Nachtlicht gehört ein Tagzwilling",
                "body": (
                    "Die Verordnung sagt dasselbe zweimal, einmal für die Nacht und "
                    "einmal für den Tag. Die Farbe trägt die Botschaft; nur der "
                    "Träger wechselt — ein Licht im Dunkeln, ein Ball oder eine "
                    "Flagge bei Helligkeit. Wer die Paare behält, behält beide "
                    "Tabellen auf einmal.\n\n"
                    "— Vorrangschiff: bei Nacht ein grünes helles Rundumlicht, "
                    "möglichst 1 m höher als das Topplicht; bei Tag ein von allen "
                    "Seiten sichtbarer GRÜNER Ball (Art. 27).\n"
                    "— Berufsfischer während des Setzens und Einholens der Netze: "
                    "bei Nacht ein gelbes gewöhnliches Rundumlicht; bei Tag ein "
                    "GELBER Ball. Wer bei Tag mit der Schleppangel fischt, führt "
                    "einen WEISSEN Ball (Art. 31).\n"
                    "— Vor Wellenschlag zu schützende Schiffe (Messungen, "
                    "hydrologische Untersuchungen, Rettungsaktionen): bei Nacht ein "
                    "rotes über einem weissen Rundumlicht; bei Tag eine Flagge, obere "
                    "Hälfte rot, untere weiss — oder zwei Flaggen übereinander, rot "
                    "über weiss (Art. 28).\n"
                    "— Für die Schifffahrt gefährliche Ankerungen: bei Nacht zwei "
                    "weisse Rundumlichter übereinander mit mindestens 1 m Abstand; "
                    "bei Tag zwei WEISSE Flaggen übereinander. Jede einzelne "
                    "Ankerung wird bei Nacht mit weissen Lichtern, bei Tag mit gelben "
                    "Schwimmkörpern bezeichnet (Art. 29).\n"
                    "— Tauchen: die Flagge «A» des Internationalen Signalbuchs — ein "
                    "Doppelstander, am Stock weiss, aussen blau — an Land gehisst "
                    "oder auf dem Schiff von allen Seiten sichtbar angebracht und bei "
                    "Nacht wirksam beleuchtet (Art. 32).\n\n"
                    "Auch die Masse sind vorgeschrieben: Tafeln und Flaggen "
                    "mindestens 60 cm hoch und breit, Bälle mindestens 30 cm "
                    "Durchmesser; ein Ball darf durch eine Einrichtung ersetzt "
                    "werden, die unmissverständlich gleich wirkt (Art. 20)."
                ),
            },
            "it": {
                "title": "Segnali diurni: ogni fanale notturno ha il suo gemello di giorno",
                "body": (
                    "L'ordinanza dice due volte la stessa cosa, una per la notte e "
                    "una per il giorno. Il colore porta il messaggio; cambia solo il "
                    "supporto — un fanale al buio, un pallone o una bandiera con la "
                    "luce. Ricordare le coppie significa ricordare entrambe le "
                    "tabelle in una volta.\n\n"
                    "— Battello con precedenza: di notte un fanale chiaro a luce "
                    "verde visibile per tutto l'orizzonte, se possibile un metro più "
                    "in alto del fanale d'albero; di giorno un pallone VERDE visibile "
                    "da tutti i lati (art. 27).\n"
                    "— Pescatore professionista durante la posa e il ritiro delle "
                    "reti: di notte un fanale ordinario a luce gialla visibile per "
                    "tutto l'orizzonte; di giorno un pallone GIALLO. Chi di giorno "
                    "pesca con la sciabica porta un pallone BIANCO (art. 31).\n"
                    "— Natanti da proteggere dalle onde (misurazioni, ricerche "
                    "idrologiche, salvataggio): di notte un fanale rosso sopra uno "
                    "bianco; di giorno una bandiera metà rossa in alto e metà bianca "
                    "in basso — oppure due bandiere sovrapposte, rossa sopra bianca "
                    "(art. 28).\n"
                    "— Ancoraggi pericolosi per la navigazione: di notte due fanali "
                    "bianchi sovrapposti ad almeno un metro di distanza; di giorno "
                    "due bandiere BIANCHE sovrapposte. Ogni singolo ancoraggio è "
                    "segnalato di notte con fanali bianchi, di giorno con "
                    "galleggianti gialli (art. 29).\n"
                    "— Immersione subacquea: la bandiera «A» del Codice "
                    "internazionale dei segnali — una fiamma a due punte, bianca "
                    "verso l'asta e blu dall'altra parte — issata a terra oppure "
                    "collocata sul battello visibile da tutti i lati e illuminata di "
                    "notte (art. 32).\n\n"
                    "Anche le dimensioni sono prescritte: tavole e bandiere di almeno "
                    "60 cm di lato, palloni di almeno 30 cm di diametro; un pallone "
                    "può essere sostituito da un dispositivo equivalente, purché "
                    "impedisca qualsiasi confusione (art. 20)."
                ),
            },
            "en": {
                "title": "Day signals: every night light has a daytime twin",
                "body": (
                    "The ordinance says the same thing twice, once for night and once "
                    "for day. The colour carries the message; only the carrier "
                    "changes — a light in the dark, a ball or a flag in daylight. "
                    "Learn the pairs and you learn both tables at once.\n\n"
                    "— Priority boat: by night a bright green all-round light, if "
                    "possible 1 m above the masthead light; by day a GREEN ball "
                    "visible all round (art. 27).\n"
                    "— Professional fisherman setting or hauling nets: by night an "
                    "ordinary yellow all-round light; by day a YELLOW ball. Trolling "
                    "by day is shown by a WHITE ball (art. 31).\n"
                    "— Boat to be protected from wash (survey, hydrological research, "
                    "rescue): by night a red light above a white one; by day a flag "
                    "red over white — or two flags one above the other, red above "
                    "white (art. 28).\n"
                    "— Anchors dangerous to navigation: by night two white all-round "
                    "lights at least 1 m apart; by day two WHITE flags one above the "
                    "other. Each individual anchor is marked by white lights at "
                    "night and yellow floats by day (art. 29).\n"
                    "— Underwater diving: flag \"A\" of the International Code of "
                    "Signals — a swallow-tailed pennant, white at the hoist and blue "
                    "beyond — hoisted ashore, or carried on the boat visible all "
                    "round, and effectively lit at night (art. 32).\n\n"
                    "The dimensions are prescribed too: boards and flags at least "
                    "60 cm high and wide, balls at least 30 cm across; a ball may be "
                    "replaced by a device of the same appearance provided it excludes "
                    "any confusion (art. 20)."
                ),
            },
        },
    },
    {
        "principle": "iala-buoyage",
        "kind": "principle",
        # Swiss lake/river marking (ONI annexe 4 ch. I). It shares the cone/cylinder
        # logic with IALA but is its OWN system with its own reference direction —
        # hence a ch-specific card rather than reusing the maritime Region A one.
        "applies": {"ch"},
        "prov": {
            "ref": "ONI art. 37 et annexe 4, ch. I (fig. 49 à 55) — balisage des "
                   "chenaux et des obstacles",
            "source": "Ordonnance sur la navigation intérieure (ONI), RS 747.201.1",
            "url": "https://www.fedlex.admin.ch/eli/cc/1979/337_337_337/fr",
            "as_of": "2022-01-01",
            "licence": "Public domain — Swiss federal law (freely reusable).",
        },
        "lang": {
            "fr": {
                "title": "Balisage suisse : la forme donne le côté, les cônes donnent le quadrant",
                "body": (
                    "Sur les eaux suisses, deux formes suffisent à tenir le système : "
                    "le CYLINDRE et le CÔNE. Tout se lit dans un sens de référence "
                    "unique, «vu du large» — c'est-à-dire depuis l'eau libre vers la "
                    "rive.\n\n"
                    "Chenal (art. 37, al. 4 ; annexe 4, fig. 50, 51 et 53) :\n"
                    "— À gauche, vu du large : des CYLINDRES, peints en rouge ou non "
                    "peints.\n"
                    "— À droite : des CÔNES pointe en haut, peints en vert ou non "
                    "peints.\n"
                    "— De nuit, la même chose en lumière : feux à éclats ROUGES à "
                    "gauche, VERTS à droite.\n"
                    "Le même couple sert à border un haut-fond près de la rive : "
                    "cylindres du côté du large, cônes du côté de la terre "
                    "(fig. 52).\n\n"
                    "Obstacle isolé (fig. 49) : un CÔNE POINTE EN BAS, peint en rouge "
                    "ou non peint. La pointe renversée est le signal «ceci n'est pas "
                    "un bord de chenal, c'est un objet à éviter».\n\n"
                    "Obstacles étendus — les marques de quadrant (fig. 54). Deux "
                    "cônes superposés disent dans quel quadrant se trouve l'eau "
                    "profonde :\n"
                    "— Nord : les deux pointes EN HAUT.\n"
                    "— Sud : les deux pointes EN BAS.\n"
                    "— Est : cône inférieur pointe en bas, supérieur pointe en haut "
                    "(les deux bases se touchent).\n"
                    "— Ouest : cône inférieur pointe en haut, supérieur pointe en bas "
                    "(les deux pointes se touchent).\n"
                    "Nord et Sud se retiennent seuls : les pointes montrent le côté "
                    "où passer. Un exemple de l'annexe donne la lecture complète — "
                    "les marques indiquent que les eaux profondes se trouvent dans "
                    "les quadrants Nord et Ouest (fig. 55).\n\n"
                    "Attention à ne pas mélanger deux systèmes : ce balisage-ci est "
                    "celui des eaux intérieures suisses. Le balisage maritime IALA "
                    "région A, avec ses marques latérales rouges et vertes «en venant "
                    "du large», est un autre référentiel."
                ),
            },
            "de": {
                "title": "Schweizer Bezeichnung: die Form gibt die Seite, die Kegel den Quadranten",
                "body": (
                    "Auf Schweizer Gewässern tragen zwei Formen das ganze System: der "
                    "ZYLINDER und der KEGEL. Alles wird in einer einzigen "
                    "Bezugsrichtung gelesen, «vom See her» — also vom freien Wasser "
                    "gegen das Ufer.\n\n"
                    "Fahrrinne (Art. 37 Abs. 4; Anhang 4, Fig. 50, 51 und 53):\n"
                    "— Links, vom See her gesehen: ZYLINDER, rot gestrichen oder "
                    "ungestrichen.\n"
                    "— Rechts: KEGEL mit der Spitze nach oben, grün gestrichen oder "
                    "ungestrichen.\n"
                    "— Bei Nacht dasselbe als Licht: ROTE Blitzlichter links, GRÜNE "
                    "rechts.\n"
                    "Dasselbe Paar begrenzt eine Untiefe nahe dem Ufer: Zylinder auf "
                    "der Seeseite, Kegel auf der Landseite (Fig. 52).\n\n"
                    "Einzelnes Hindernis (Fig. 49): ein KEGEL MIT DER SPITZE NACH "
                    "UNTEN, rot gestrichen oder ungestrichen. Die umgekehrte Spitze "
                    "heisst «das ist kein Fahrrinnenrand, das ist ein Objekt, das zu "
                    "meiden ist».\n\n"
                    "Ausgedehnte Hindernisse — die Quadrantenzeichen (Fig. 54). Zwei "
                    "übereinander angebrachte Kegel sagen, in welchem Quadranten das "
                    "tiefe Wasser liegt:\n"
                    "— Nord: beide Spitzen NACH OBEN.\n"
                    "— Süd: beide Spitzen NACH UNTEN.\n"
                    "— Ost: der untere mit der Spitze nach unten, der obere nach oben "
                    "(die Grundflächen berühren sich).\n"
                    "— West: der untere mit der Spitze nach oben, der obere nach "
                    "unten (die Spitzen berühren sich).\n"
                    "Nord und Süd merkt man sich von selbst: die Spitzen zeigen zur "
                    "Seite, auf der man vorbeifährt.\n\n"
                    "Nicht zu verwechseln: dies ist die Bezeichnung der Schweizer "
                    "Binnengewässer. Das maritime IALA-System der Region A mit seinen "
                    "roten und grünen Lateralzeichen «von See kommend» ist ein anderer "
                    "Bezugsrahmen."
                ),
            },
            "it": {
                "title": "Segnalamento svizzero: la forma dà il lato, i coni il quadrante",
                "body": (
                    "Sulle acque svizzere due forme reggono l'intero sistema: il "
                    "CILINDRO e il CONO. Tutto si legge in un'unica direzione di "
                    "riferimento, «visto dal largo» — cioè dall'acqua libera verso la "
                    "riva.\n\n"
                    "Canale navigabile (art. 37 cpv. 4; allegato 4, fig. 50, 51 e "
                    "53):\n"
                    "— A sinistra, visto dal largo: CILINDRI, dipinti di rosso o non "
                    "dipinti.\n"
                    "— A destra: CONI con la punta in alto, dipinti di verde o non "
                    "dipinti.\n"
                    "— Di notte lo stesso in luce: luci lampeggianti ROSSE a "
                    "sinistra, VERDI a destra.\n"
                    "La stessa coppia delimita un basso fondale vicino alla riva: "
                    "cilindri dal lato del largo, coni dal lato di terra "
                    "(fig. 52).\n\n"
                    "Ostacolo isolato (fig. 49): un CONO CON LA PUNTA IN BASSO, "
                    "dipinto di rosso o non dipinto. La punta rovesciata dice «questo "
                    "non è un bordo di canale, è un oggetto da evitare».\n\n"
                    "Ostacoli estesi — i segnali di quadrante (fig. 54). Due coni "
                    "sovrapposti dicono in quale quadrante si trova l'acqua "
                    "profonda:\n"
                    "— Nord: entrambe le punte IN ALTO.\n"
                    "— Sud: entrambe le punte IN BASSO.\n"
                    "— Est: il cono inferiore con la punta in basso, quello superiore "
                    "in alto (le basi si toccano).\n"
                    "— Ovest: il cono inferiore con la punta in alto, quello "
                    "superiore in basso (le punte si toccano).\n"
                    "Nord e Sud si ricordano da soli: le punte indicano il lato da "
                    "cui passare. Un esempio dell'allegato dà la lettura completa — i "
                    "segnali indicano che le acque profonde si trovano nei quadranti "
                    "nord e ovest (fig. 55).\n\n"
                    "Da non confondere: questo è il segnalamento delle acque interne "
                    "svizzere. Il sistema marittimo IALA regione A, con i suoi "
                    "segnali laterali rossi e verdi «venendo dal largo», è un altro "
                    "riferimento."
                ),
            },
            "en": {
                "title": "Swiss marking: the shape gives the side, the cones give the quadrant",
                "body": (
                    "On Swiss waters two shapes carry the whole system: the CYLINDER "
                    "and the CONE. Everything is read in a single reference "
                    "direction, \"seen from the open water\" — that is, from open "
                    "water towards the shore.\n\n"
                    "Channel (art. 37, para. 4; annex 4, fig. 50, 51 and 53):\n"
                    "— On the left, seen from the open water: CYLINDERS, painted red "
                    "or unpainted.\n"
                    "— On the right: CONES point upwards, painted green or "
                    "unpainted.\n"
                    "— At night the same thing in light: RED flashing lights to the "
                    "left, GREEN to the right.\n"
                    "The same pair edges a shoal near the bank: cylinders on the open-"
                    "water side, cones on the shore side (fig. 52).\n\n"
                    "Isolated obstacle (fig. 49): a CONE POINT DOWNWARDS, painted red "
                    "or unpainted. The inverted point says \"this is not a channel "
                    "edge, this is an object to avoid\".\n\n"
                    "Extended obstacles — the quadrant marks (fig. 54). Two cones one "
                    "above the other say which quadrant holds the deep water:\n"
                    "— North: both points UP.\n"
                    "— South: both points DOWN.\n"
                    "— East: lower cone point down, upper point up (the bases meet).\n"
                    "— West: lower cone point up, upper point down (the points "
                    "meet).\n"
                    "North and South remember themselves: the points show the side to "
                    "pass. An example in the annex gives the full reading — the marks "
                    "indicate that deep water lies in the North and West quadrants "
                    "(fig. 55).\n\n"
                    "Don't mix two systems: this is the marking of Swiss inland "
                    "waters. Maritime IALA Region A, with its red and green lateral "
                    "marks \"coming from seaward\", is a different frame of reference."
                ),
            },
        },
    },
    {
        "principle": "sound-signals",
        "kind": "principle",
        "applies": {"ch"},
        "prov": {
            "ref": "ONI art. 33 et 34 — signaux sonores (émission, durées, "
                   "vocabulaire)",
            "source": "Ordonnance sur la navigation intérieure (ONI), RS 747.201.1",
            "url": "https://www.fedlex.admin.ch/eli/cc/1979/337_337_337/fr",
            "as_of": "2022-01-01",
            "licence": "Public domain — Swiss federal law (freely reusable).",
        },
        "lang": {
            "fr": {
                "title": "Signaux sonores : une grammaire de durées et de nombres",
                "body": (
                    "Les signaux sonores forment une langue minuscule : deux durées, "
                    "un nombre de sons, et c'est tout. Il n'y a rien à retenir par "
                    "cœur une fois la règle de formation comprise.\n\n"
                    "Les briques (art. 33, al. 2) : les sons sont de hauteur "
                    "constante ; un SON BREF dure environ une seconde, un SON "
                    "PROLONGÉ environ quatre, et l'intervalle entre deux sons "
                    "successifs environ une seconde. La volée de cloche dure elle "
                    "aussi environ quatre secondes et peut être remplacée par des "
                    "coups frappés sur un objet métallique (al. 3).\n\n"
                    "Le vocabulaire (art. 34) — à n'émettre que lorsque la sécurité "
                    "de la navigation et des autres usagers l'exige :\n"
                    "— un son prolongé : «Attention» ou «j'avance en ligne droite» ;\n"
                    "— un son bref : «Je viens sur tribord» ;\n"
                    "— deux sons brefs : «Je viens sur bâbord» ;\n"
                    "— trois sons brefs : «Je bats en arrière» ;\n"
                    "— quatre sons brefs : «Je suis incapable de manœuvrer» ;\n"
                    "— une série de sons très brefs : «Danger d'abordage».\n"
                    "La logique se voit d'un coup d'œil : un son long annonce une "
                    "intention calme, et plus les sons brefs s'accumulent, plus la "
                    "situation se dégrade — de la simple manœuvre jusqu'à la perte de "
                    "contrôle, puis à l'alarme.\n\n"
                    "Avec quoi les émettre (art. 33, al. 1) : les bateaux à moteur, "
                    "sauf plaisance et sport, utilisent des avertisseurs actionnés "
                    "mécaniquement ou électriquement ; les autres bateaux un klaxon "
                    "ou une corne appropriés ; pour les bateaux à rames et les "
                    "voiliers jusqu'à 15 m² de surface vélique, un sifflet suffit. "
                    "Les bateaux de la police en service urgent peuvent employer un "
                    "avertisseur à deux sons alternés ou une sirène, et avec l'accord "
                    "de l'autorité les bateaux de l'OFDF, des pompiers, de la lutte "
                    "contre la pollution et des services de sauvetage également "
                    "(al. 4)."
                ),
            },
            "de": {
                "title": "Schallzeichen: eine Grammatik aus Dauer und Anzahl",
                "body": (
                    "Die Schallzeichen sind eine winzige Sprache: zwei Dauern, eine "
                    "Anzahl Töne, mehr nicht. Wer die Bildungsregel verstanden hat, "
                    "muss nichts auswendig lernen.\n\n"
                    "Die Bausteine (Art. 33 Abs. 2): Die Töne sind von "
                    "gleichbleibender Höhe; ein KURZER TON dauert etwa eine Sekunde, "
                    "ein LANGER TON etwa vier, die Pause zwischen aufeinanderfolgenden "
                    "Tönen etwa eine Sekunde. Eine Gruppe von Glockenschlägen dauert "
                    "ebenfalls etwa vier Sekunden und darf durch Schläge auf einen "
                    "metallenen Gegenstand ersetzt werden (Abs. 3).\n\n"
                    "Das Vokabular (Art. 34) — nur zu geben, wenn es die Sicherheit "
                    "der Schifffahrt und der übrigen Benützer des Gewässers "
                    "gebietet:\n"
                    "— ein langer Ton: «Achtung» oder «Ich halte meinen Kurs bei»;\n"
                    "— ein kurzer Ton: «Ich richte meinen Kurs nach Steuerbord»;\n"
                    "— zwei kurze Töne: «Ich richte meinen Kurs nach Backbord»;\n"
                    "— drei kurze Töne: «Meine Maschine geht rückwärts»;\n"
                    "— vier kurze Töne: «Ich bin manövrierunfähig»;\n"
                    "— eine Folge sehr kurzer Töne: «Gefahr eines "
                    "Zusammenstosses».\n"
                    "Die Logik sieht man auf einen Blick: ein langer Ton kündigt eine "
                    "ruhige Absicht an, und je mehr kurze Töne sich häufen, desto "
                    "schlimmer die Lage — vom blossen Manöver über den Verlust der "
                    "Manövrierfähigkeit bis zum Alarm.\n\n"
                    "Womit (Art. 33 Abs. 1): Motorschiffe, ausgenommen "
                    "Vergnügungsschiffe und Sportboote, geben sie mit mechanisch oder "
                    "elektrisch betriebenen Schallgeräten; andere Schiffe mit einer "
                    "geeigneten Hupe oder einem Horn; für Ruderboote und Segelschiffe "
                    "bis 15 m² Segelfläche genügt eine Mundpfeife. Polizeischiffe im "
                    "dringlichen Einsatz dürfen ein Zweiklanghorn oder eine Sirene "
                    "verwenden, mit Zustimmung der Behörde auch Schiffe des BAZG, der "
                    "Feuerwehr, der Ölwehr und der Rettungsdienste (Abs. 4)."
                ),
            },
            "it": {
                "title": "Segnali acustici: una grammatica di durate e di numeri",
                "body": (
                    "I segnali acustici sono una lingua minuscola: due durate, un "
                    "numero di suoni, e basta. Capita la regola di formazione, non "
                    "resta nulla da imparare a memoria.\n\n"
                    "I mattoni (art. 33 cpv. 2): i suoni sono di intensità costante; "
                    "un SUONO BREVE dura circa un secondo, un SUONO PROLUNGATO circa "
                    "quattro, e l'intervallo fra due suoni successivi circa un "
                    "secondo. Anche la scampanellata dura circa quattro secondi e può "
                    "essere sostituita da colpi battuti su un oggetto metallico "
                    "(cpv. 3).\n\n"
                    "Il vocabolario (art. 34) — da emettere solo se la sicurezza "
                    "della navigazione e degli altri utenti lo esige:\n"
                    "— un suono prolungato: «attenzione» oppure «mantengo la "
                    "rotta»;\n"
                    "— un suono breve: «accosto a destra»;\n"
                    "— due suoni brevi: «accosto a sinistra»;\n"
                    "— tre suoni brevi: «faccio marcia indietro»;\n"
                    "— quattro suoni brevi: «sono impossibilitato a manovrare»;\n"
                    "— una serie di suoni molto brevi: «pericolo di collisione».\n"
                    "La logica si coglie a colpo d'occhio: un suono lungo annuncia "
                    "un'intenzione tranquilla, e più i suoni brevi si accumulano, più "
                    "la situazione peggiora — dalla semplice manovra alla perdita di "
                    "controllo, fino all'allarme.\n\n"
                    "Con che cosa (art. 33 cpv. 1): i battelli a motore, eccettuate "
                    "le imbarcazioni da diporto e sportive, usano sorgenti sonore "
                    "azionate meccanicamente o elettricamente; gli altri natanti un "
                    "clacson o un corno idoneo; per i battelli a remi e a vela fino a "
                    "15 m² di superficie velica basta un semplice fischietto."
                ),
            },
            "en": {
                "title": "Sound signals: a grammar of durations and counts",
                "body": (
                    "Sound signals are a tiny language: two durations, a number of "
                    "blasts, and that is all. Once the rule of formation is clear "
                    "there is nothing left to memorise.\n\n"
                    "The building blocks (art. 33, para. 2): blasts are of constant "
                    "pitch; a SHORT blast lasts about one second, a PROLONGED blast "
                    "about four, and the interval between successive blasts about one "
                    "second. A peal of the bell also lasts about four seconds and may "
                    "be replaced by strokes on a metal object (para. 3).\n\n"
                    "The vocabulary (art. 34) — to be given only when the safety of "
                    "navigation and of other users requires it:\n"
                    "— one prolonged blast: \"Attention\" or \"I am holding my "
                    "course\";\n"
                    "— one short blast: \"I am turning to starboard\";\n"
                    "— two short blasts: \"I am turning to port\";\n"
                    "— three short blasts: \"I am going astern\";\n"
                    "— four short blasts: \"I am unable to manoeuvre\";\n"
                    "— a series of very short blasts: \"Risk of collision\".\n"
                    "The logic is visible at a glance: a long blast announces a calm "
                    "intention, and the more short blasts pile up the worse the "
                    "situation — from a simple manoeuvre, to loss of control, to "
                    "alarm.\n\n"
                    "What to sound them with (art. 33, para. 1): powered boats other "
                    "than pleasure and sport craft use mechanically or electrically "
                    "operated horns; other boats a suitable klaxon or horn; for "
                    "rowing boats and sailing boats up to 15 m² of sail area a "
                    "whistle is enough. Police boats on urgent service may use a "
                    "two-tone alternating horn or a siren, and with the authority's "
                    "agreement so may customs, fire, pollution-control and rescue "
                    "boats (para. 4)."
                ),
            },
        },
    },
    {
        "principle": "sound-signals",
        "kind": "principle",
        "applies": {"int", "fr_cotiere"},
        "prov": {
            "ref": "COLREG 1972 / RIPAM — Rules 32, 33, 34, 35, 36",
            "source": "COLREG — International Regulations for Preventing Collisions "
                      "at Sea, 1972 (publié en droit français comme RIPAM)",
            "url": "https://www.navcen.uscg.gov/sites/default/files/pdf/navRules/"
                   "navrules.pdf",
            "as_of": None,
            "licence": "Public domain — US Government work (17 USC §105); French "
                       "publication: Licence Ouverte / Etalab 2.0.",
        },
        "lang": {
            "en": {
                "title": "Sound at sea: short blasts say what I am doing, prolonged blasts say I am here",
                "body": (
                    "The whole system splits on one question: can the other vessel "
                    "SEE you? In sight of one another, sound reports a manoeuvre. Out "
                    "of sight, it reports a presence. Same blasts, two different "
                    "jobs.\n\n"
                    "The units (Rule 32): a whistle is any sound signalling appliance "
                    "capable of producing the prescribed blasts; a short blast lasts "
                    "about one second; a prolonged blast from four to six seconds.\n\n"
                    "In sight of another vessel — manoeuvring signals (Rule 34):\n"
                    "— one short blast: \"I am altering my course to starboard\";\n"
                    "— two short blasts: \"I am altering my course to port\";\n"
                    "— three short blasts: \"I am operating astern propulsion\";\n"
                    "— at least five short and rapid blasts: doubt about the other "
                    "vessel's intentions or manoeuvre — the warning signal.\n"
                    "Note the count matches the action, and only the doubt signal is "
                    "open-ended: five *or more*, because it is an alarm rather than a "
                    "statement.\n\n"
                    "In or near restricted visibility — signals of presence "
                    "(Rule 35): a power-driven vessel making way through the water "
                    "sounds one prolonged blast at intervals of not more than two "
                    "minutes. Here the blast is on a clock, not a reaction: nobody "
                    "can see you, so you announce yourself on a schedule.\n\n"
                    "What you must carry (Rule 33): a vessel of 100 metres or more "
                    "shall be provided with a whistle, a bell and a gong. A vessel of "
                    "less than 12 metres is not obliged to carry the prescribed "
                    "appliances, but if she does not, she must have some other means "
                    "of making an efficient sound signal.\n\n"
                    "And if you signal with light instead (Rule 36): any light used "
                    "to attract attention must be such that it cannot be mistaken for "
                    "an aid to navigation, and high-intensity intermittent or "
                    "revolving lights, such as strobe lights, shall be avoided."
                ),
            },
            "fr": {
                "title": "Le son en mer : les sons brefs disent ce que je fais, les sons prolongés disent que je suis là",
                "body": (
                    "Tout le système se partage sur une seule question : l'autre "
                    "navire peut-il vous VOIR ? En vue l'un de l'autre, le son "
                    "annonce une manœuvre. Hors de vue, il annonce une présence. Mêmes "
                    "sons, deux fonctions différentes.\n\n"
                    "Les unités (règle 32) : le sifflet est tout appareil capable "
                    "d'émettre les sons prescrits ; un son bref dure environ une "
                    "seconde, un son prolongé de quatre à six secondes.\n\n"
                    "En vue d'un autre navire — signaux de manœuvre (règle 34) :\n"
                    "— un son bref : «Je viens sur tribord» ;\n"
                    "— deux sons brefs : «Je viens sur bâbord» ;\n"
                    "— trois sons brefs : «Mes machines battent en arrière» ;\n"
                    "— au moins cinq sons brefs et rapprochés : le doute sur les "
                    "intentions ou la manœuvre de l'autre — le signal "
                    "d'avertissement.\n"
                    "Le nombre suit l'action, et seul le signal de doute reste "
                    "ouvert : cinq sons *ou plus*, parce que c'est une alarme et non "
                    "une déclaration.\n\n"
                    "Par visibilité réduite ou à ses abords — signaux de présence "
                    "(règle 35) : un navire à propulsion mécanique faisant route émet "
                    "un son prolongé à intervalles ne dépassant pas deux minutes. Ici "
                    "le son suit une horloge et non une réaction : personne ne vous "
                    "voit, vous vous annoncez donc à intervalle régulier.\n\n"
                    "Ce qu'il faut avoir à bord (règle 33) : un navire de 100 m ou "
                    "plus doit être pourvu d'un sifflet, d'une cloche et d'un gong. Un "
                    "navire de moins de 12 m n'est pas tenu d'avoir les appareils "
                    "prescrits, mais s'il ne les a pas, il doit disposer d'un autre "
                    "moyen d'émettre un signal sonore efficace.\n\n"
                    "Et si l'on signale par la lumière (règle 36) : tout feu destiné "
                    "à attirer l'attention doit être tel qu'il ne puisse être "
                    "confondu avec une aide à la navigation, et il faut éviter les "
                    "feux intermittents ou tournants de forte intensité, comme les "
                    "feux à éclats stroboscopiques."
                ),
            },
        },
    },
    {
        "principle": "day-shapes",
        "kind": "principle",
        "applies": {"int", "fr_cotiere"},
        "prov": {
            "ref": "COLREG 1972 / RIPAM — Rules 20(d), 25(e), 26(c), 28, 30",
            "source": "COLREG — International Regulations for Preventing Collisions "
                      "at Sea, 1972 (publié en droit français comme RIPAM)",
            "url": "https://www.navcen.uscg.gov/sites/default/files/pdf/navRules/"
                   "navrules.pdf",
            "as_of": None,
            "licence": "Public domain — US Government work (17 USC §105); French "
                       "publication: Licence Ouverte / Etalab 2.0.",
        },
        "lang": {
            "en": {
                "title": "Day shapes: the daylight half of the light rules",
                "body": (
                    "Shapes are not a separate subject. The rules on lights and "
                    "shapes are complied with in all weathers; lights run from sunset "
                    "to sunrise, and the shapes are shown by day (Rule 20). So every "
                    "shape answers the same question a light answers after dark: what "
                    "kind of vessel is that, and what is she doing?\n\n"
                    "Three shapes carry almost everything, and each has a settled "
                    "meaning:\n"
                    "— The BALL says \"not proceeding normally\". A vessel at anchor "
                    "shows a black ball forward — the daytime twin of her all-round "
                    "white anchor light. Aground, she shows three balls in a vertical "
                    "line, the same escalation her two all-round red lights make at "
                    "night (Rule 30).\n"
                    "— The CONE qualifies how a vessel is proceeding. A sailing vessel "
                    "also being propelled by machinery shows a conical shape, apex "
                    "DOWNWARDS, forward where it can best be seen (Rule 25(e)) — she "
                    "looks like a sailing boat but must be treated as a power-driven "
                    "one, and the cone is the only thing that says so. A vessel "
                    "fishing other than trawling, with outlying gear extending more "
                    "than 150 metres, shows a cone apex UPWARDS in the direction of "
                    "the gear (Rule 26(c)) — here the cone points at the hazard.\n"
                    "— The CYLINDER is reserved for a vessel constrained by her "
                    "draught, which may show it in addition to her ordinary lights, "
                    "or three all-round red lights in a vertical line (Rule 28).\n\n"
                    "Read that way the day picture is small: count the balls for how "
                    "stuck she is, look at which way a cone points to know whether it "
                    "is about her engine or about her gear, and treat a cylinder as a "
                    "warning about depth."
                ),
            },
            "fr": {
                "title": "Marques de jour : la moitié diurne des règles sur les feux",
                "body": (
                    "Les marques ne sont pas un sujet à part. Les règles sur les feux "
                    "et les marques s'appliquent par tous les temps ; les feux vont du "
                    "coucher au lever du soleil, et les marques se montrent de jour "
                    "(règle 20). Chaque marque répond donc à la question que le feu "
                    "traite la nuit : quel genre de navire est-ce, et que fait-il ?\n\n"
                    "Trois formes portent presque tout, chacune avec un sens fixe :\n"
                    "— La BOULE dit «je ne fais pas route normalement». Au mouillage, "
                    "un navire montre une boule noire à l'avant — le jumeau diurne de "
                    "son feu blanc de mouillage visible sur tout l'horizon. Échoué, il "
                    "montre trois boules en ligne verticale, la même gradation que ses "
                    "deux feux rouges la nuit (règle 30).\n"
                    "— Le CÔNE qualifie la façon de faire route. Un voilier qui marche "
                    "aussi au moteur montre un cône, POINTE EN BAS, à l'avant là où il "
                    "est le mieux visible (règle 25(e)) — il a l'air d'un voilier mais "
                    "doit être traité comme un navire à moteur, et seul le cône le "
                    "dit. Un navire qui pêche autrement qu'au chalut, avec un engin "
                    "déployé sur plus de 150 m, montre un cône POINTE EN HAUT dans la "
                    "direction de l'engin (règle 26(c)) — ici le cône désigne le "
                    "danger.\n"
                    "— Le CYLINDRE est réservé au navire handicapé par son tirant "
                    "d'eau, qui peut le montrer en plus de ses feux ordinaires, ou "
                    "bien trois feux rouges superposés visibles sur tout l'horizon "
                    "(règle 28).\n\n"
                    "Lu ainsi, le tableau de jour est court : comptez les boules pour "
                    "savoir à quel point il est immobilisé, regardez de quel côté "
                    "pointe un cône pour savoir s'il parle du moteur ou de l'engin de "
                    "pêche, et prenez un cylindre pour un avertissement de profondeur."
                ),
            },
        },
    },
]


def concepts_for(bank_id: str, langs) -> list[Concept]:
    """Return the approved Concept objects to load into one bank.

    ``bank_id`` is the country/option bank key (e.g. "fr_cotiere", "ch", "de",
    "int"); only seeds that list it in ``applies`` are returned, in the requested
    languages. Empty list when nothing applies — the build then ships no concept
    file for that bank, and the player simply shows no card (graceful).
    """
    out: list[Concept] = []
    for e in _SEED:
        if bank_id not in e["applies"]:
            continue
        for lg in langs:
            loc = e["lang"].get(lg)
            if not loc:
                continue
            p = e["prov"]
            out.append(Concept(
                id=f"{e['principle']}.{lg}", principle=e["principle"],
                kind=e["kind"], title=loc["title"], body=loc["body"], lang=lg,
                prov_ref=p["ref"], prov_source=p["source"], prov_url=p["url"],
                prov_as_of=p["as_of"], prov_licence=p["licence"],
                review_status="approved"))
    return out
