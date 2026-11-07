# OPEN ROUTE #443 — AN Any / BARE-CONTAINER ELEMENT AS A METHOD RECEIVER OWES NO AttributeError
**Status: REPAIRED (executor h442, driver run #3, 2026-10-28), Severity 1.** Red-team round 35 (2026-10-28, SYSTEMATIC BUILTIN-PRECONDITION CENSUS after #432-#439 on daaf6ea78: 860 probes / 452 fully proved / 175 confirmed (156 new + 19 inside #432's documented residual); rt34's 63 all closed). Census TSV `scratchpad/rt35/census.tsv`; findings `scratchpad/rt35/FINDINGS.txt` (the family text below is quoted from it).
Witnesses `witnesses-r443/` (19): `m034_strip_dictval_any.py`, `m035_upper_listelem_any.py`, `m037_upper_tuple_any.py`, `m038_upper_bare_list.py`, `b000_any_elem_recv.py`, `b001_any_elem_recv.py`, `b002_any_elem_recv.py`, `b004_any_elem_recv.py`, `b006_any_elem_recv.py`, `b007_any_elem_recv.py`, `b008_any_elem_recv.py`, `b011_any_elem_recv.py`, `b012_any_elem_recv.py`, `b015_any_elem_recv.py`, `b016_any_elem_recv.py`, `b017_any_elem_recv.py`, `b019_any_elem_recv.py`, `b020_any_elem_recv.py`, `x010_any_elem_realistic.py`.

Driver repro: 7/7 family exemplars (A1 n002, A2 s106, B1 k001 + e017, B2 a001, C c007, D b000) rc=0 Verification SUCCESS on main f1c249c4e at 2026-10-28T19:25Z, each violating under CPython (scratchpad/rt35/driver-repro.txt).

```
#443 AN Any / BARE-CONTAINER ELEMENT AS A METHOD RECEIVER OWES NO AttributeError   (19)
  x010  `row: List[Any]`; `len(row[0].strip())` PROVED; f([42])                       CPython AttributeError.
  (Inside #432's DOCUMENTED residual -- Any / object receivers admitted; a direct `x: Any` receiver is not proved, only
  ELEMENTS of Any-typed containers slip; bare list / dict / tuple elements (int under BARE-CONTAINER-INT) belong to A2.)
  REPAIR (proposed, allow-list / refuse by default): the R-gate analogue: an attribute / method on an underivable (#UND / Any / object) receiver is refused under a claim
  covering AttributeError.
```

## REPAIR (executor h442, driver run #3, 2026-10-28, off fa7cbb1aa; annotations §7.150, translational §T.6.160)

WHY A DIRECT `x: Any` WAS NOT PROVED WHILE ELEMENTS SLIPPED (measured with a log-mode instrumentation of #432 over the
1054 claim-bearing corpus / mirror files): #432 computed `K(S)` = the receiver's derived classes MINUS the underivable
marks, `Any` and `object`, and admitted `|K(S)| <= 1`. Every underivable receiver therefore had `K(S) = {}` and was
ADMITTED -- `x: Any` (S = {Any}) exactly as `xs[0]` on `List[Any]` (S = {#UND, Any}), a bare `list` element
(S = {#UND}) or a `for` target over `d.values()` (S = {#UND}). No rule refused either one; the direct `Any`
parameter only failed later, by accident of its lowering (a goal Unknown), while an element lowers int-erased with
an input-blind method `val`, which proves. The gap was the rule's admission of the EMPTY known set, not a spelling.

RULE (code inline in `_run_pipeline`, #432's judgement; no new def in a mirrored file, no axiom, no emission change):
in a function covered by #432's claim test, an attribute load `R.a` is REFUSED
(`PYCSL-R443-UNDERIVABLE-RECEIVER-ATTRIBUTE`) when the classes `R` may have at that point (after #432's flow narrowing)
are EMPTY, contain `#UND` / `#UNK` / `#UNKT` / `#UB`, `Any` or `object`, or a class name that is not KNOWN (a builtin
of #432's table; a file class never otherwise bound; a `from M import C` of a real class with metaclass `type` from
`pathlib` / `decimal` / `fractions` / `collections` / `datetime` / `io` / `re` / `array` / `ipaddress` / `uuid`) -- an
alias `PyVal = Any`, a TypeVar, a `typing` name are not known. Not judged: a module object (`import m`; the name bound
only by `Import`), and the receiver-form `(N.get(k) or {}).get(k2, D)` / `N.get(k).get(k2, D)` on a `Dict[str, PyVal]`
name `N` (IR `dict_value_types[N] == "hval"`), which Module 6 lowers with the `PyCSL-DVW-R5` assertion that the
receiver IS a map (in the function's own code, not a nested def / lambda; owed, not assumed: 3280 / 3281 stay FAIL on it, 3282 PROVED). ROOT FIX in the type propagation
(`_ty383`): a method call on the `None` arm of a receiver, when `NoneType` lacks the method, contributes no class
(bottom: AttributeError before any use, the rule `str` / `bytes` already had) instead of `#UND`; without it
`w = v.strip()` after `if v is None: return` derived `{#UND, str}` and g4's control 6522 was refused.

Witnesses 6756-6774 (the 19 red-team probes): PROVED at base fa7cbb1aa, REFUSED at the candidate. Rule witnesses
6775 (`PyVal = Any` parameter), 6776 (an element of `List[T]`, PROVED at base), 6777 (a `for` target over `List[Any]`),
6778 (`x: Any`), 6779 (`x: object`): 6776 PROVED at base, the others not proved at base (Unknown / Timeout), all
REFUSED now. 6784 (expected FAIL): an `Any` element bound to a local and narrowed by `isinstance(v, str)` is ADMITTED
by #443; the erased value's route #343 obligation stays Unknown (base and candidate) -- so the advice is a concrete
source type or dropping the claim. Every witness is a CPython AttributeError (`__main__` drivers). Controls 6783
(`List[str]` / `Dict[str, str]` elements), 6785 (an element of `List[C]`, C a file class), 6786 (`p: Path` from
`pathlib`): PROVED at base and candidate; 3282, 6515-6518, 6522 PROVED at the candidate.

GATES: (final candidate = this commit; logs in the executor's scratchpad h442/gates, h442/gates-final): fidelity
check-self-annotate-sync rc=0, self-annotate-mirror-check rc=0; root byte-diff vs the driver's v10/ca base sweep (= emission
of c53b5e381 = main fa7cbb1aa, docs-only since): 2563 -> 2566 .mlw, 0 MOVED / 4 GONE / 0 APPEARED, 37 new sources (7 emit),
rc=0 with --expect-gone; GONE = 3289 / 4812 / 4813 / 4825, all expected FAIL, VERIFY-FAIL at base (full proof FAIL) ->
REFUSED by #443 at the candidate (M1: verdict kept, not proved both); pyref 2186 / 2186 0/0/0 rc=0; mirrors 53 / 53
0/0/0 rc=0 (v10/ma; no mirror refusal, no OWED proof); pycsl_lib refusal screen identical (104 files); planes (fast 61)
61/61 rc=0; refusal-witness-coverage rc=0 (342 demonstrated, +1); refusal-advice-audited rc=0 (169 audited, +1
FOLLOWABLE: advice/a443_typed_source, a443_drop_claim PROVED); dropped-mutation / getattr-erasure / open-route-carriers /
trusted-frame-honesty / trusted-raises-honesty / stdlib-modules-verify / trusted-reasons (414 <-> 414) / doc-coherency /
clause-survival --emit-dir / assumed-facts --emit-dir rc=0. Census: 31 new rows (30 REFUSAL + 6784 VERIFY-FAIL) via the
tool's `_census_row` (h442-r442-443/census.py, paths written with the /home/fabrice/git/pycsl/ prefix); 7 rows re-measured
in place: 4812 / 4813 / 4825 (VERIFY-FAIL -> REFUSAL) and 4765 / 4766 / 5013 / 5018 (REFUSAL, the base enum-member
message -> the #443 message, which now fires first; refused at base and candidate). OVER-REFUSAL COST, measured on the
1054 claim-bearing files (every corpus / pyref / mirror / pycsl_lib file containing `no_exception`; --no-proof screen,
base vs candidate): exactly 8 files change, all expected FAIL (the 4 GONE + the 4 re-messaged); 0 PASS files, 0 mirror
files. A first candidate refused 6522 (PASS, `w = v.strip()` after a None guard: the None arm derived `#UND`; fixed at
the root in `_ty383`), 3282 (PASS, the DVW-R5-obligated receiver `.get`; exempted as owed) and re-messaged 6620 (a user
module object `hl.h`; module objects exempted). \trusted count 442 unchanged; no axiom.

## RESIDUALS (honest)

Over-refusal by design: a receiver annotated by a type alias of a concrete class (`Num = int`), a `NewType`, an
imported class outside the ten-module list (`from enum import Enum`-typed values whose class is not a file class), an
ABC / Protocol from `typing` / `collections.abc` used as a parameter annotation (`x: Sequence[str]` then `x.index(..)`),
and any underivable value even where every possible class has the attribute. Measured cost 0 in the corpus / mirror /
pycsl_lib. Still NOT judged (outside this rule): the attribute's EXISTENCE on a single known class (`n: int`;
`n.upper()` -- route #440's A2, h440's (class, method) table), and a receiver whose derived classes are wrong rather
than underivable (the derivation trusts annotations).
