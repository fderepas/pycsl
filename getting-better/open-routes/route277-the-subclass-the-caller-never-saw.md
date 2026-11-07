# OPEN ROUTE #277 — A USER-CLASS-TYPED VALUE IS ASSUMED EXACT (override refinement is opt-in only)
**Status: REPAIRED (gen #37, 2026-10-19; opened the same day), Severity 1.** Decision (A) by measurement: the override check is the DEFAULT; `--assume-class-exact` is the declared opt-out (CLASS-EXACT). Red-team round 6; driver-reproduced at 78162575 (rc=0; CPython AssertionError).
Witnesses `witnesses-r277/` (p039 local subclass; p260 base+caller in imported module `rt6lib/base.py`, subclass local).
`use(a: A)` proves `\result == 1` over `a.m()` while `B(A).m` returns 2. The refinement goal exists only under
`--check-behavioral-subtyping` (which catches both), and `--soundness-report` lists NO assumption for this:
it is the user-class twin of BUILTIN-EXACT, undeclared. Repair options: (A) refinement check on by default
(measure corpus cost), or (B) declare a model assumption (e.g. CLASS-EXACT) in `--soundness-report` with
relied_on_by = every method call on a user-class-typed receiver whose class has (or may have) subclasses, plus docs.

## REPAIR (2026-10-19, r277 executor, off 72ab1c57) — option (A), chosen by measurement

**Measurement (A) vs (B).** Turning the existing check on by default (`--check-behavioral-subtyping`
forced, at 72ab1c57): root corpus 10 of 1791 emitting files gain goals, python-reference 1 of 2186
(the rest byte-identical); of those, PASS -> FAIL: **0445** (the negative Layer-D test, which had no
FAIL marker because it was meant to be run with the flag), **1348** (C3 diamond: `C.m == 3` vs
`A.m == 1`) and **pyref 0206** (`C(A, B)`: `A.who == 1` vs `B.who == 2`) — each a GENUINE Liskov
violation of its own program, not a model artefact. The other 8 movers keep their verdict (0444,
1453, 2781 PASS; 1347/1448/1449/1568/1582 expected FAIL). Mirror: 2 of 53 files gain goals (25
goals, every one `(true -> true) /\ (true -> true)`); after the #278 rules one further genuine
debt surfaced (below). Stdlib (`src/pycsl_lib`, 93 emitting): 0 moved. Compared with LATIN1-STR's
rejected strict default (3 of 12 PASS -> FAIL + every os codec proof), (A) is proportionate, so it
is the default and (B) — the declared assumption — is the opt-out.

**Rules (inline; `_run_pipeline`, `_render_refinement_goal`, `_emit_subtyping_goals`,
`apply_inheritance`, `_build_soundness_report` all have `\trusted` mirror twins; no new def;
ledger 3, no axiom).**
- `_run_pipeline` entry: `args.check_behavioral_subtyping = True` unless `--assume-class-exact`
  (new flag). `--check-behavioral-subtyping` is kept (now a no-op).
- `--soundness-report` under `--assume-class-exact` lists **CLASS-EXACT** (`strict_mode`: the
  default) with relied_on_by = every override pair of the unit ("refinement not checked") and every
  method call whose method name is a method of a class of the unit (receiver not resolved:
  over-, never under-reported). Not listed by default (nothing is assumed).
- The route #216 dunder refusal and the PYCSL-SUBTYPING-PAIR refusal now advise
  `--assume-class-exact` instead of "drop `--check-behavioral-subtyping`".
- Corpus: 0445 gains `# pycsl-expected: FAIL` (docstring rewritten in the same line count — its
  frontend golden keys on line numbers); 1348 and pyref 0206 run with
  `# pycsl-flags: --assume-class-exact` (their C3/MRO claims are tested under the declared
  assumption; the default now FAILS them, correctly).
- Docs: README (declared-assumptions paragraph), static semantics App. C.1 row + "What the default
  override check covers" + the P2/P4 conforms_to rule text, translational §T.10.1 row + §T.10.5
  CLASS-EXACT entry, `bin/check-assumed-facts.py` docstring.

**Probe table** (`pycsl.py`, rc; CPython ground truth in each file's `__main__`):

| shape | 72ab1c57 | after |
|---|---|---|
| p039 / **3100** local `B(A).m == 2`, `use(a: A) == 1` | PROVED (0) | FAIL (1, `b__m_refines_a`) |
| p260 (`--import-path witnesses-r277`) / **3101** base+caller imported, subclass local | PROVED (0) | FAIL (1) |
| **3102** = 3100 under `--assume-class-exact` | flag unknown (2) | PASS (0), CLASS-EXACT reported |
| **3103** control: weaker pre / stronger post override, `use(a: A, k)` | PASS | PASS |

Residuals: an override defined in a module that does NOT import-resolve the base's class (a
subclass the verifier never sees, e.g. built by unverified code) is outside any check — modular
behavioural subtyping holds for VERIFIED subclasses only (stated in App. C.1). Aliasing one object
through two differently-typed receivers is not modelled (FIELD-DISJOINT's residue). Gates and
blast radius: see route #278's REPAIR (one landing).
