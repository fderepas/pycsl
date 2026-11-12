# OPEN ROUTE #595 — #582 BYPASS: A CLASS-BODY METHOD ALIAS BOUND BY A match CAPTURE (case n: / case _ as n) OR BY field(default_factory=lambda: m) IS NOT SEEN BY THE CLASS-BODY-ALIAS RULE, SO THE CALL'S WRITES ARE DROPPED
**Status: REPAIRED (driver run #6, executor u41, branch run6-u41 off ghost-assign-bc6 4e6004f3b after L6; annotations §7.595). Mechanism (front end, route #582's class-body walk in `pycsl.py::_run_pipeline`, twin `\trusted`; inline, no new def, no axiom): `match` captures (`case n`, `as n`, `*n`, `**n`) and `except ... as n` in a class body are possible-method bindings; a `field(...)` is plain data only when it is `dataclasses.field` with plain `default` and a builtin-constructor / plain-lambda `default_factory` and no `**`; a call of a name made a possible method only by these forms is refused with new `PYCSL-R595-CLASS-BODY-BINDING-CALL` (route #582's code otherwise).** Opened as: Status OPEN, Severity 1, pre-existing (red team rt56; proves on 822621340 and int55). Witnesses witnesses-r595/.

## The defect

Route #582 (annotations §7.582) refuses `c.n(...)` when `n` is bound in a class body by anything but a `def` whose
value may be callable. Its walk knew assignments, annotated / augmented assignments, loop / `with` / walrus targets
and imports, and its plain-data test took any `field(...)` without a non-plain `default` for data. So:

    class C:
        def m(self, v): self.a = v
        match m:
            case n: pass                 # also `case _ as n`; or  n: Any = field(default_factory=lambda: m)
    def caller(c): c.n(5); return c.a    # `ensures \result == 0` PROVED; CPython 5 (TypeError for the field)

(rt56 hh1718 / hh1719 / hh1729; the driver measured all three PROVED on pycsl-base6).

## The repair

RULE (annotations §7.595), inside route #582's walk (same population: every statement of a class body outside nested
`def` / `class` / `lambda`, nested blocks included):

- `MatchAs` / `MatchStar` with a name and `MatchMapping.rest` (so `case n`, `case _ as n`, a guarded or nested
  capture, `case [*n]`, `case {**n}`) and an `ExceptHandler` name bind that name with the pattern / handler as the
  value: never plain data, never an alias the `\nothing` admission can follow.
- `field(...)`: plain only when `field` is bound solely by the import `dataclasses.field` (a class-body `def field(q=None):
  return q` made `n = field(q=m)` the method), there is no `**` keyword, the `default` is plain data and the
  `default_factory`, if any, is a builtin constructor not rebound in the file (`list` `dict` `set` `tuple` `frozenset`
  `str` `int` `float` `bool` `bytes` `bytearray` `complex`) or a no-argument lambda whose body is plain data.
- The refusal at the call `<x>.n(...)` is route #582's (same receiver rules); its code is
  `PYCSL-R595-CLASS-BODY-BINDING-CALL` when the reported binding is one of these forms, route #582's code and message
  (unchanged, its audit key and hash intact) otherwise. Advice as #582: call the method by the name of its `def`, or
  give `n` its own `def` (with a contract) that calls it (audited FOLLOWABLE, below).

## Witnesses and measurements

- rt56 witnesses (`--no-proof`, default / typed / store): hh1718, hh1719, hh1729 9/9 REFUSED R595 (EMITTED at base).
- u41 probes `witnesses-r595/u41-probes/` (all CPython-breaching): a guarded capture (p595c), an `as` on an or-pattern
  then `case n:` (p595e), a class-body `def field(q=None): return q` with `n = field(q=m)` (p595f), `@dataclass` with `field(default_factory=lambda: C.m)` and
  `c.n(c, 5)` (p595g), `field(**{"default": m})` (p595h): 15/15 REFUSED R595. `case [*n]` (p595a), `case {**n}`
  (p595b) and a capture in a tuple pattern under `if True:` (p595d) are refused by the pure_ast PARSER (patterns not
  yet parsed) before the rule, at base and HEAD.
- CORPUS (expected FAIL): 9655 (hh1718), 9656 (hh1719), 9657 (hh1729), 9658 (p595c), 9659 (p595e), 9660 (p595f), 9662
  (p595h): PROVED at base 4e6004f3b in the default model (full proof, measured); 9661 (p595g, the `@dataclass`
  shape) REFUSED at base by the method / instance-attribute shadowing rule (kept as a hardening witness); all eight
  REFUSED R595 x 3 models at HEAD. CONTROLS (expected PASS, `\result == 5` resting on `m`'s contract): 9665 (a dataclass
  `field(default_factory=list)`), 9666 (advice 1: a class-body `match` capture kept, the caller calls `c.m(5)`; =
  `witnesses-r595/advice/a595_call_def_name.py`), 9667 (advice 2: `def n(self, v): self.m(v)` with a contract; =
  `advice/a595_own_def.py`) PROVED at base and HEAD (default model; under typed / store all five are a Why3 type error at base and HEAD
  alike, an existing model limit).
- rt56 families g1730 / g1740 (front end, default model, base vs HEAD on the 36 CPython-honest probes and every
  probe whose HEAD verdict is R593 / R595): R595 changes only hh1718 / hh1719 / hh1729 (EMITTED -> R595) and hh1720
  (`except ... as n` in the class body, CPython AttributeError: R582 -> R595, refused at both); the honest controls
  hh1722 / hh1730 keep their route #582 refusal.
- INERTNESS (own base = `git archive 4e6004f3b`, same scripts, launched from the tree root): mirror 53/53 0 MOVED / 0
  GONE / 0 APPEARED (after the `type`-store fix, see route #593); corpus root 3103 -> 3108 .mlw 0 MOVED / 0 GONE / 0
  APPEARED (`--new-source` the 17 u41 files: the 5 controls emit, the 12 witnesses are refused); python-reference
  2185 0 / 0 / 0. No existing corpus file is newly refused. Candidate pre-check (216 corpus files importing `ast` /
  IR modules with classes, using `default_factory` / a `field` binding, or a `match` statement): 0 R593 / R595.
- GATES on HEAD (u41, 2026-11-12): fidelity check-self-annotate-sync / self-annotate-mirror-check / doc-coherency
  --check rc 0 x3; run-soundness-planes.sh (fast) rc 0, 62/62 green; individually check-vacuous-drivers,
  check-dropped-mutation (0 dropped, CTXBIND 51 = ratchet: no `with ... as` added), check-claim-vacuity (1791 at the
  ceiling), check-refusal-witness-coverage (444 demonstrated, +12 census rows from `_census_row`),
  check-refusal-advice-audited (257 audited, +2 FOLLOWABLE: R593 / R595), check-open-route-carriers (14 carriers
  unchanged) all rc 0. Proof-axiom ledger 3 (`proof_axiom_allowlist.py` untouched); no new `#@ \trusted`.
- Rule 18 slow planes on HEAD (emit dir = the HEAD mirror sweep, byte-identical to the base one):
  check-assigns-writes-survival rc 0, check-getattr-erasure rc 0; check-trusted-frame-honesty rc 1 (model-visible
  ratchets 1 > 0 and 48 > 0) with output IDENTICAL to the same command on the base 4e6004f3b with the base mirror
  sweep: PRE-EXISTING, not moved by this change (nothing in the mirror or in a method frame changed).
