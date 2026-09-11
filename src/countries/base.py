"""Country-model dataclasses — pure data, no logic.

A :class:`Country` bundles everything that varies between national exams: which
sources ground it, the exam-theme taxonomy + the tagger that sorts units into it,
the recreational-permit catalogue, the regional variance (cantons / Länder / a
shared-lake regime) and the legal basis for reuse. The Swiss instance
(:mod:`countries.ch`) is a thin adapter over the original flat modules; new
countries (:mod:`countries.de`) are defined natively against these types.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable


@dataclass(frozen=True)
class ExamBlock:
    """One scored section of a block-based exam (German SBF style): ``count``
    questions are drawn and at least ``min_correct`` must be right to pass."""
    name: str
    count: int
    min_correct: int


@dataclass(frozen=True)
class ExamSlot:
    """One question slot of an official test matrix (NL: the CBR *toetsmatrijs*):
    the toetsterm it draws from, the theme that toetsterm maps to, and the
    points that one question carries. A paper composed slot by slot has the
    official weighting — a give-way question is worth 3, a definitions one 1 —
    which is what ``total_points`` and the pass mark are stated against."""
    code: str                                      # toetsterm id, e.g. "A.11"
    label: str                                     # as printed in the matrix
    theme: str                                     # exam theme the slot draws from
    points: int


@dataclass(frozen=True)
class ExamRules:
    """How a sitting is assembled and graded. Two scoring regimes are modelled:

    * ``all_or_nothing`` — the Swiss VKS point system; ``pass_points`` of
      ``total_points`` are needed (per-question all-or-nothing).
    * ``blocks`` — the German SBF system; each :class:`ExamBlock` carries its own
      pass minimum and the candidate must clear every block.

    ``slots`` (optional, all_or_nothing only) is the official test matrix: when
    present the paper is one question per slot, each worth that slot's points,
    and the matrix must add up to ``questions`` / ``total_points`` exactly.
    """
    questions: int
    time_limit_min: int
    scoring: str                                   # "all_or_nothing" | "blocks"
    pass_points: int | None = None
    points_per_question: int | None = None
    total_points: int | None = None
    blocks: tuple[ExamBlock, ...] = ()
    slots: tuple[ExamSlot, ...] = ()               # official test matrix, if published
    note: str = ""

    def theme_weights(self) -> dict[str, int]:
        """Official points per theme from the matrix (empty without one)."""
        out: dict[str, int] = {}
        for sl in self.slots:
            out[sl.theme] = out.get(sl.theme, 0) + sl.points
        return out


@dataclass(frozen=True)
class Permit:
    """A recreational permit category and the exam that grants it."""
    code: str                                      # stable key, e.g. "A", "SBF-See"
    label: str
    themes: tuple[str, ...]                        # which taxonomy themes it draws on
    exam: ExamRules
    drive: str = ""                                # "motor" | "sail" | "motor+sail"
    track: str = ""                                # "inland" | "maritime"; "" ⇒ inferred
    mandatory: bool = True                         # legally required vs voluntary
    note: str = ""


@dataclass(frozen=True)
class Region:
    """A within-country variance unit: a Swiss canton, a German Bundesland, or a
    special regime such as a shared lake. ``time_limit_min`` overrides the exam
    timer where a region sets its own; ``None`` means it inherits the default."""
    code: str
    name: str
    time_limit_min: int | None = None
    primary: bool = False                          # the project's headline scope
    note: str = ""


@dataclass(frozen=True)
class Reference:
    """A source that is documented and legally cleared but not (yet) ingested —
    e.g. an official question catalogue. Records the reuse note so the legal
    finding lives in code, ready for a later ingestion task."""
    name: str
    url: str
    note: str = ""


@dataclass(frozen=True)
class PathStep:
    """One non-theory requirement on the road to the licence — the scaffolding
    the theory trainer alone doesn't cover: minimum age, the medical attestation,
    a recognised first-aid course, the on-water *practical* exam, the application
    to the issuing authority, the fees, and the certificate's validity/renewal.

    This is **procedural reference data**, not a quiz question, but it obeys the
    same discipline: every step is authored from an **official source** (never from
    memory) and carries ``source`` + ``url`` + ``as_of`` so the staleness check can
    flag drift and a reviewer knows when a fact was last verified. Facts that drift
    (fees, age thresholds, validity periods) are marked ``volatile`` so they can be
    re-verified first.

    ``body`` is keyed by language (``{"fr": "...", "de": "..."}``); the player and
    docs render the active language and fall back to the country ``default_lang``.
    A step applies country-wide unless ``region_scope`` names a region, and to every
    permit unless ``permit_scope`` lists specific permit codes.
    """
    code: str                                      # "age"|"medical"|"first_aid"|"practical"|"application"|"fees"|"validity"
    body: dict                                     # {lang: prose}; default_lang required
    source: str                                    # human label of the authority/document
    url: str                                       # official page the fact was read from
    as_of: str                                     # ISO date the fact was verified
    volatile: bool = False                         # fee/age/validity that drifts — re-verify first
    region_scope: str = ""                         # "" ⇒ country-wide; else a Region code
    permit_scope: tuple[str, ...] = ()             # () ⇒ all permits; else specific Permit codes


@dataclass(frozen=True)
class ReadingRef:
    """One place to *learn the theory* before drilling it: the official exam
    programme, the law itself, a published question catalogue, a sample exam,
    an official guide, or a commercial handbook. The player's Learn tab lists
    them under "where to study", each with a **coverage** figure — how much of
    what the exam asks the resource addresses.

    Same discipline as :class:`PathStep`: every entry is authored from a page
    that was actually read (``source`` + ``as_of``), never from memory. A
    commercial handbook is listed only where its own product page states what
    it covers, and is marked ``cost="paid"``; listing is not endorsement.

    Coverage is computed by the player from the bank it has loaded, so it
    respects the active permit/pool, on two axes:

    * ``themes`` — the exam themes the resource addresses. ``basis`` says how
      that list was established, so the reader can weigh it:
      ``"programme"`` (the resource *is* the official syllabus — covers all),
      ``"toc"`` (its table of contents was read), ``"publisher"`` (the
      publisher's own claim, no TOC seen), ``"units"`` (an ingested law: the
      themes its KB units are tagged with, filled at bundle time from
      ``source_id``).
    * ``match`` — a substring of ``provenance.source``; when set, the player
      also reports the share of questions that cite this very text.
    """
    code: str                                      # stable slug
    kind: str                                      # "programme"|"law"|"catalogue"|"sample_exam"|"guide"|"handbook"
    title: str
    publisher: str
    url: str
    lang: str                                      # language(s) of the resource, e.g. "fr" / "de/fr/it"
    cost: str                                      # "free" | "paid"
    official: bool                                 # published by the state / the exam authority
    themes: tuple[str, ...]                        # exam themes it addresses (see basis)
    basis: str                                     # "programme" | "toc" | "publisher" | "units"
    body: dict                                     # {lang: one sentence — what it is, why read it}
    source: str                                    # the page the entry was verified on
    as_of: str                                     # ISO date it was verified
    match: str = ""                                # provenance.source substring ⇒ citation share
    source_id: str = ""                            # ingested KB source id (basis "units")
    price: str = ""                                # as displayed on the source page (volatile)
    permit_scope: tuple[str, ...] = ()             # () ⇒ every permit; else specific codes


@dataclass(frozen=True)
class Country:
    """The full description of one country's exam domain."""
    code: str                                      # ISO 3166-1 alpha-2 ("CH", "DE")
    name: str
    default_lang: str
    langs: tuple[str, ...]
    sources: tuple                                 # tuple[sources.Source, ...]
    themes: dict                                   # {theme_id: human label}
    tagger: Callable                               # (ref, title, text, default) -> id
    permits: dict                                  # {code: Permit}
    regions: dict                                  # {code: Region}
    default_region: str
    extension_themes: frozenset = frozenset()      # scaffolded ahead of a source
    references: tuple = ()                         # tuple[Reference, ...]
    # The path-to-permit scaffolding: the non-theory steps (medical / first-aid /
    # practical exam / application / fees / validity) that turn a passed theory
    # paper into an actual licence. Empty for sourcing-only members (INT).
    path: tuple = ()                               # tuple[PathStep, ...]
    # Where to learn the theory: programme, law, catalogues, guides, handbooks.
    reading: tuple = ()                            # tuple[ReadingRef, ...]
    legal_basis: str = ""
    # Maps a prose-drafted question's theme -> the exam-block id it belongs to,
    # for countries whose prose pool feeds a block-structured exam (DE: the BSO
    # prose seeds the Bodensee-Schifferpatent Sachgebiete). None -> prose carries
    # no block (CH point-scored, INT sourcing-only).
    prose_block_for: Callable | None = None
    # Drafting knobs for countries whose law does not fit the default assumptions
    # of src/questions/prose.py:
    #   draft_len  — (min, max) source-chunk length for select_units. None keeps
    #                the default window, which was tuned on Swiss/German law.
    #   examinable — (ref) -> bool: is this KB unit inside the country's official
    #                exam programme? None means "everything the taxonomy holds".
    #                NL uses it: its KB carries the professional-crewing corpus
    #                too, which no recreational paper can ask about.
    draft_len: tuple | None = None
    examinable: Callable | None = None

    def region_manifest(self) -> list[dict]:
        """Regions for the player picker, primary scope first then by code."""
        ordered = sorted(self.regions.values(), key=lambda r: (not r.primary, r.code))
        return [{"code": r.code, "name": r.name, "time_limit_min": r.time_limit_min,
                 "primary": r.primary, "note": r.note} for r in ordered]

    # Stable display order for the path panel: the chronological road to the permit.
    _PATH_ORDER = ("age", "medical", "first_aid", "practical", "application",
                   "fees", "validity")

    def path_manifest(self) -> list[dict]:
        """Path-to-permit steps for the player/docs, in road-to-the-permit order
        (known codes first by :data:`_PATH_ORDER`, then any extra codes by code).
        ``body`` is emitted whole (per-language); the player picks the active
        language and falls back to ``default_lang``."""
        order = {c: i for i, c in enumerate(self._PATH_ORDER)}
        steps = sorted(self.path, key=lambda s: (order.get(s.code, 99), s.code))
        return [{"code": s.code, "body": dict(s.body), "source": s.source,
                 "url": s.url, "as_of": s.as_of, "volatile": s.volatile,
                 "region_scope": s.region_scope,
                 "permit_scope": list(s.permit_scope)} for s in steps]

    # Display order for the reading list: the syllabus first, then what is free
    # and official, then the rest — a learner should meet the programme and the
    # law before any commercial handbook.
    _READING_ORDER = ("programme", "catalogue", "sample_exam", "law", "guide", "handbook")

    def reading_manifest(self) -> list[dict]:
        """Reading references for the player/docs. ``themes`` for ``basis ==
        "units"`` entries is left empty here and filled by the bundler from the
        KB (it needs the ingested units); everything else ships as authored."""
        order = {k: i for i, k in enumerate(self._READING_ORDER)}
        refs = sorted(self.reading,
                      key=lambda r: (order.get(r.kind, 99), not r.official,
                                     r.cost != "free", r.code))
        return [{"code": r.code, "kind": r.kind, "title": r.title,
                 "publisher": r.publisher, "url": r.url, "lang": r.lang,
                 "cost": r.cost, "official": r.official,
                 "themes": list(r.themes), "basis": r.basis, "body": dict(r.body),
                 "source": r.source, "as_of": r.as_of, "match": r.match,
                 "source_id": r.source_id, "price": r.price,
                 "permit_scope": list(r.permit_scope)} for r in refs]
