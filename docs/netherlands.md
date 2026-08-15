# Nederland — Klein Vaarbewijs (uitbreiding van het leerinstrument)

Dit document beschrijft het Nederlandse deel van het boating-licence-leerinstrument.
De juridische en redactionele grens is **dezelfde als bij de Zwitserse kern**: elke
vraag wordt *uit primaire bronnen afgeleid* en draagt een bronvermelding terug naar
de tekst waaruit zij komt.

Eén verschil met Duitsland is bepalend voor de aanpak: er is **géén officiële
vragenbank**. Het CBR publiceert alleen voorbeeldexamens, geen catalogus zoals het
Duitse ELWIS. De Nederlandse vragen worden daarom **uit de wet zelf afgeleid**
(law-seeded, achter de review gate) — dezelfde route die het project al voor de
Bodensee/BSO-set volgt. Dit document beschrijft de ingestie en het examenmodel
waarop die vragenset gebouwd wordt.

## De juridische grond — geen auteursrecht, geen licentie nodig

Nederland is de schoonste bron die het project tot nu toe heeft. Waar Duitsland een
*beperking* op het auteursrecht kent (§5(1) UrhG) en Frankrijk een *open licentie*
(Licence Ouverte / Etalab), zegt **Auteurswet art. 11** dat het recht er eenvoudigweg
niet is:

> Er bestaat geen auteursrecht op wetten, besluiten en verordeningen, door de
> openbare macht uitgevaardigd, noch op rechterlijke uitspraken en administratieve
> beslissingen.

De geconsolideerde teksten én de bijbehorende bijlage-illustraties worden door KOOP
(wetten.overheid.nl) als open data gepubliceerd.

## Vaarbewijzen

Wanneer een klein vaarbewijs vereist is, staat in **Binnenvaartbesluit art. 16 lid 1**:
schepen van 15 tot 20 m, pleziervaartuigen van 15 tot 25 m, en elk schip korter dan
15 m dat sneller dan 20 km/u door het water kan. *Welk* vaarbewijs volgt uit lid 2–4.

| Code | Vaarbewijs | Vaargebied | Grondslag |
|------|-----------|-----------|-----------|
| `KVB-1` | Klein Vaarbewijs I | rivieren, kanalen en meren | Binnenvaartbesluit art. 16 lid 2 |
| `KVB-2` | Klein Vaarbewijs II | de overige binnenwateren (wateren van maritieme aard) | art. 16 lid 3 |

De grens tussen beide is een **wettelijke opsomming**, geen inschatting
(Binnenvaartregeling art. 7.11b lid 2): Westerschelde, Oosterschelde, Waddenzee,
Eems, Dollard, IJsselmeer, IJmeer en Markermeer — met uitzondering van de Gouwzee.

Het klein vaarbewijs wordt afgegeven volgens het model **"klein vaarbewijs/ICC voor
de binnenvaart"** (Binnenvaartregeling bijlage 7.3) en geldt daarmee tevens als
International Certificate for Operators of Pleasure Craft.

> **Geen praktijkexamen.** Anders dan in CH, DE en FR is het theorie-examen het hele
> examen. In `src/countries/nl.py` ontbreekt daarom bewust een `practical`-stap: die
> toevoegen zou een wettelijke eis verzinnen.

## Examenstructuur — gewogen punten, 70 %

De wet noemt wél de onderwerpen maar niet het format. Aantallen, wegingen en
slaaggrenzen komen van het **CBR** en zijn als zodanig gemarkeerd (`volatile`):

| Vaarbewijs | Vragen | Tijd | Punten | Geslaagd vanaf |
|-----------|--------|------|--------|----------------|
| KVB I | 40 meerkeuze | 60 min | 1–3 per vraag, totaal 80 | 56 (70 %) |
| KVB II | 27 (23 meerkeuze + 4 open) | 90 min | 1–4 per vraag, totaal 50 | 35 (70 %) |

Omdat per vraag een ander gewicht geldt, wordt dit gemodelleerd als
`scoring="all_or_nothing"` op punten (net als het Zwitserse VKS-examen) en niet als
blokken (het Duitse SBF-model).

## Onderwerpen (thema-taxonomie)

De taxonomie is niet verzonnen: **Binnenvaartregeling art. 7.15** somt de
examenonderwerpen op, en het **Binnenvaartpolitiereglement** ordent de "wettelijke
bepalingen" in hoofdstukken. De themalijst (`src/countries/nl_themes.py`) is de
combinatie van beide — één thema per BPR-hoofdstuk in plaats van één ondoorzichtige
bak "wettelijke bepalingen":

`algemene_bepalingen` · `optische_tekens` · `geluidsseinen` · `marifoon_radar` ·
`verkeerstekens` · `betonning` · `vaarregels` · `ligplaats` ·
`bijzondere_vaarwegen` · `vaarbewijs` · `voortstuwing` · `veiligheid` ·
`vaarwater` · `manoeuvreren` · `milieu` · `navigatie` · `weerkunde`

KVB II is **cumulatief** ("de in het eerste lid genoemde onderwerpen alsmede …"):
KVB I plus `navigatie` en `weerkunde`.

De onderwerpen die de wet noemt maar geen verordening uitschrijft — motoren,
manoeuvreren, vaarwateromstandigheden, koers- en plaatsbepaling, weerkunde — zijn
**extension themes**: bewust leeg in een wet-alleen-build, zodat de normalize-stap
er niet over waarschuwt.

### Waarom de tagger deterministisch is

Een Nederlands artikelnummer draagt altijd zijn hoofdstuk ("Artikel 5.01" staat in
hoofdstuk 5) — in het hele BPR wijkt geen enkel artikellabel af van het
`<hoofdstuk>` waarin het staat. Het thema wordt dus rechtstreeks van de verwijzing
afgelezen; trefwoorden zijn alleen de terugval voor de wet/besluit/regeling-
laag. De hoofdstukregel geldt **alleen** voor de twee politiereglementen: "Artikel
7.15" van de Binnenvaartregeling is een examenregel, geen ligplaatsregel.

## Bronnen (`kind="bwb"`)

KOOP publiceert elke geconsolideerde toestand van elke wet als gestructureerde XML,
geïndexeerd door een manifest dat de geldende toestand aanwijst. De fetcher leest
dat manifest en gokt dus nooit een datum.

| id | Wet | BWB-id |
|----|-----|--------|
| `bpr` | Binnenvaartpolitiereglement | BWBR0003628 |
| `rpr` | Rijnvaartpolitiereglement 1995 | BWBR0006923 |
| `stz` | Scheepvaartreglement territoriale zee | BWBR0007914 |
| `binnenvaartwet` | Binnenvaartwet | BWBR0023009 |
| `binnenvaartbesluit` | Binnenvaartbesluit | BWBR0025631 |
| `binnenvaartregeling` | Binnenvaartregeling | BWBR0025958 |

Huidige omvang: **782 eenheden, 686 illustraties** (`data/kb.nl.sqlite`).

### De bijlagen zijn een figurenschat

Alleen al het BPR levert ruim 400 officiële PNG's mee: bijlage 3 (optische tekens),
6 (geluidsseinen), 7 (verkeerstekens) en 8 (markering van het vaarwater — de
IALA-A-betonning). Dat zijn precies vier van de families waarvoor
`src/questions/diagrams.py` tekeningen genereert; hier zitten de officiële platen in
de wet zelf.

## Grensregimes

Drie Nederlandse grenswateren hebben hun eigen reglement. Ze zijn ingedeeld naar de
**structuur van het reglement zelf**, niet naar de ligging op de kaart
(`src/jurisdictions.py`):

| Regime | Landen | Basis | Waarom |
|--------|--------|-------|--------|
| `WESTERSCHELDE` | NL/BE | COLREGS | hoofdstukken *uitwijken*, *lichten en dagmerken*, *geluids- en lichtseinen*; verwijst naar de Internationale Bepalingen ter voorkoming van aanvaringen op zee |
| `EEMSMONDING` | NL/DE | COLREGS | idem, op de Eems en de Dollard |
| `GEMEENSCHAPPELIJKE-MAAS` | NL/BE | CEVNI | hoofdstukken als het BPR (kentekens, optische tekens, verkeerstekens, vaarregels) |

Alle drie **wijken af** (`diverges`) in plaats van uit te sluiten: zij voegen lokale
regels toe aan een geharmoniseerde basis, dus hun tekens blijven overdraagbaar. De
Rijn (`RHINE`, RPR/CCR) telt Nederland al als deelnemer.

> Nederland kent **geen** recreatief zeevaarbewijs, dus er is geen `NL-MARITIME`-knoop
> — beide vaarbewijzen zijn inland-track, ook die voor de wateren van maritieme aard,
> die in de wet binnenwateren zijn.

## Wat nog open staat

* **Vragen.** De bank is nog leeg: de law-seeded afleiding uit het BPR en de
  Binnenvaartregeling (achter de review gate) is de volgende stap.
* **Niet ingestiet.** Scheepvaartreglement Westerschelde 1990, Scheepvaartreglement
  Eemsmonding en Scheepvaartreglement Gemeenschappelijke Maas staan als
  :class:`Reference` vast (vrij van auteursrecht, maar nog niet nodig).
* **Illustraties.** De 686 platen zijn opgehaald en gekoppeld aan hun bijlage, maar
  nog niet aan losse tekens (zoals bij de Franse RGP-platen gebeurde).

<!-- path:auto:start — generated by `python run.py path-docs`; do not edit by hand -->

## Van theorie naar vaarbewijs: de stappen naast het examen

Het examen halen is niet genoeg. Deze stappen worden gegenereerd uit `src/countries/nl.py` (veld `path`) — elk feit komt uit een officiële bron en is gedateerd.

| Stap | Detail | Bron |
|---|---|---|
| **Minimumleeftijd** | Een vaarbewijs wordt niet afgegeven aan wie de leeftijd van 18 jaar nog niet heeft bereikt (Binnenvaartwet art. 27 lid 1 onder a). Voor het afleggen van het theorie-examen zelf stelt het CBR geen leeftijdsgrens — de grens zit op de afgifte. | [Binnenvaartwet art. 27 lid 1 onder a](https://wetten.overheid.nl/BWBR0023009#Hoofdstuk5_Paragraaf2_Artikel27) · gecontroleerd op 2026-08-15 |
| **Gezondheid & geschiktheid** | Voor het klein vaarbewijs volstaat een gezondheidsverklaring (niet ouder dan 26 weken) in plaats van een geneeskundige verklaring; een geneeskundig onderzoek blijft achterwege als daaruit blijkt dat u lichamelijk en geestelijk voldoende geschikt bent (Binnenvaartbesluit art. 20 lid 2, art. 26 lid 1). | [Binnenvaartbesluit art. 20 lid 2 en art. 26](https://wetten.overheid.nl/BWBR0025631#Hoofdstuk4_Paragraaf2_Artikel20) · gecontroleerd op 2026-08-15 |
| **Aanvraag & inschrijving** | Bij de aanvraag legt u de gezondheidsverklaring over en het getuigschrift van het afgelegde examen (Binnenvaartbesluit art. 20 lid 1). Het examen wordt afgenomen door het CBR (Centraal Bureau Rijvaardigheidsbewijzen, Binnenvaartregeling art. 1.1); het vaarbewijs zelf wordt door de minister afgegeven. | [Binnenvaartbesluit art. 20 lid 1](https://wetten.overheid.nl/BWBR0025631#Hoofdstuk4_Paragraaf2_Artikel20) · gecontroleerd op 2026-08-15 |
| **Examengeld** (kan wijzigen) | Examengeld CBR: € 53,15 voor het theorie-examen Klein Vaarbewijs I. Toeslagen voor extra tijd (€ 13,50) of individuele begeleiding (€ 41,60) komen daar bovenop. De kosten van een vaarschool of cursus staan hier los van. | [CBR — theorie-examen Klein Vaarbewijs I](https://www.cbr.nl/nl/recreatievaart-ppl-rzam/nl-1/theorie-examen-klein-vaarbewijs-1) · gecontroleerd op 2026-08-15 |
| **Geldigheid & vernieuwing** (kan wijzigen) | Het klein vaarbewijs wordt afgegeven volgens het model "klein vaarbewijs/ICC voor de binnenvaart" en geldt daarmee tevens als International Certificate for Operators of Pleasure Craft (Binnenvaartregeling bijlage 7.3). | [Binnenvaartregeling bijlage 7.3](https://wetten.overheid.nl/BWBR0025958#Bijlage7.3) · gecontroleerd op 2026-08-15 |

<!-- path:auto:end -->
