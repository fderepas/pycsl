# OPEN ROUTE #432 — AN Optional / Union RECEIVER OF AN ATTRIBUTE OR METHOD ACCESS OWES NO AttributeError
**Status: REPAIRED (executor g4, driver run #3, 2026-10-28), Severity 1.** Red-team round 34 (2026-10-28, convergence measurement after #418-#431 + R-gate on 78b519f63; 497 written / 474 fully proved / 63 confirmed; FINDINGS salvaged by the driver from the stalled executor's on-disk outputs); driver-reproduced on main (see `scratchpad/rt34/FINDINGS.txt` and the driver repro line below).
Witnesses `witnesses-r432/` (8): `on00_strip.py`, `on05_method.py`, `on07_dict_get.py`, `on09_int_bitlen.py`, `on10_upper_ens.py`, `on11_union_int_str_upper.py`, `on13_pipe_none.py`, `op16_upper_opt.py`.

Driver repro: 9/9 family samples rc=0 Verification SUCCESS on main 78b519f63 at 2026-10-28T10:12Z, each violating under CPython (scratchpad/rt34/driver-repro.txt).

```
#432 AN Optional / Union RECEIVER OF AN ATTRIBUTE OR METHOD ACCESS OWES NO AttributeError   (8)
  on00  x: Optional[str]; len(x.strip()) under no_exception \all PROVED; f(None)              CPython AttributeError
  on05 user method on Optional[C]   on07 Optional[dict].get   on09 Optional[int].bit_length   on10 .upper in an ensures-bearing f
  on11 Union[int, str].upper   on13 `str | None` (PEP 604) .lower   op16 Optional[str].upper
  (CONTRAST: all 18 Optional/Union OPERATOR probes un00-un17 (+ < - * [] range abs // aug-assign) are REFUSED; only the
  attribute / method-call receiver is unchecked.)
  REPAIR (proposed, allow-list / refuse by default): An attribute load / method call whose receiver's derived class set contains NoneType (or more than one class of which
  some lacks the attribute) is admitted only where the receiver is flow-narrowed (`is not None` / isinstance guard on the
  path) or under an obligation; otherwise refused under `no_exception` (AttributeError). Allow-list the admitted forms.
```

## REPAIR (executor g4, driver run #3, 2026-10-28, off 1c083dcbe; annotations §7.133, translational §T.6.144)

Code inline in `_run_pipeline` (src/pycsl/pycsl.py), right after the #349-#383 hashing pass of each function, over the
classes that pass derives (`_ex346` / `_eh372`); no new def in a mirrored file (`_run_pipeline` is `\trusted` in the mirror),
no axiom, no emission change. ALLOW-LIST: in a function that is not `\trusted` / `\abstract` and claims AttributeError
(`\all` / AttributeError / Exception / BaseException), an attribute load `R.a` is ADMITTED iff the classes `R` may have at
that point are (i) at most one class and not `None`, or (ii) only builtin classes (NoneType included) that each have `a`
(`hasattr` on the real type); everything else is REFUSED (`PYCSL-R432-OPTIONAL-RECEIVER-ATTRIBUTE`). The derivation now
gives `Optional[T]` its `None` arm (it already did for `Union[T, None]` / `T | None`), a parameter defaulted to `None` holds
`None`, and `a or b` contributes `None` only through its last operand. FLOW NARROWING (names and attribute paths only) climbs
from the access to the function entry collecting guards -- enclosing `if` / `while` / `x if T else y` tests, earlier `and` /
`or` operands, comprehension `if`s, earlier `assert T`, earlier `if T:` blocks ending in return / raise / continue / break --
decomposed through `not` / `and` / `or` into `is (not) None`, `== / != None`, `isinstance(R, C..)` (not `object` / `Any`) and
bare-truthiness leaves; it stops at a nested def / lambda and at any code that may rebind `R` (a store / del of the root name;
for an attribute path or a global / nonlocal name also an attribute store on the path or ANY call), and a loop crossed on
the way must not contain such code anywhere. `R = v` and `if R is None: ...; R = v` give a fact instead.

Witnesses 6500-6507 (the 8 red-team probes) and g4 probes 6508 (`v = d.get(k); v.strip()`), 6514 (`or` does not narrow),
6548 (`isinstance(x, object)`): PROVED at base, REFUSED at the candidate. Rule witnesses 6509 (`x: str = None`), 6510
(`n.next.v`), 6511 (rebinding after the guard), 6512 (a loop rebinding after the use), 6513 (a call between an attribute-path
guard and the use), 6549 (a generator expression consumed after a rebinding): NOT proved at base either (another refusal, or
Why3 rejecting the rebinding of a Union parameter), now refused by #432 first -- they pin the narrowing's stop conditions.
Every witness is a CPython AttributeError (`__main__` drivers). Controls 6515-6518, 6520-6524 (if-not-None, early return,
isinstance on a Union, a guarded user method, IfExp, a guarded `d.get` local, a local rebound from a narrowed method,
`continue` in a loop, unclaimed): PROVED at base and candidate. 6519 (`assert x is not None` then the access): the assert
narrows (no #432 refusal) and the assert's own AssertionError obligation FAILS at base and candidate (expected FAIL).

GATES (final candidate = commit a2749e12d + this commit's census / audit rows; logs getting-better/systematic-soundness-r3/g4-r432-437/gates/):
fidelity check-self-annotate-sync rc=0, self-annotate-mirror-check rc=0; root byte-diff vs the driver's 78b519f63 base sweep
(v8/cb): 2518 -> 2531 .mlw, 0 MOVED / 1 GONE (4810, expected FAIL: FAIL at base -> REFUSED by #433, `''.join([self])`) /
0 APPEARED, 14 new sources, rc=0 with --expect-gone; pyref 2186 / 2186 0/0/0 rc=0; mirrors 53 / 53 0/0/0 rc=0 (own base
sweep; no mirror refusal, no OWED proof); pycsl_lib refusal screen identical (104 files); planes (fast 61) 61/61 rc=0;
refusal-witness-coverage rc=0 (334 demonstrated, +3); refusal-advice-audited rc=0 (162 audited, +3 FOLLOWABLE: advice/
a432_*, a433_*, a437_* all PROVED); getattr-erasure / clause-survival --emit-dir / assumed-facts --emit-dir /
open-route-carriers / doc-coherency rc=0. Census: 37 new rows (36 REFUSAL + 6519 VERIFY-FAIL) via the tool's _census_row
(census.py; `--append-new` was aborted: it would also run 329 older row-less witnesses), 4621 re-measured (erased-value
message -> #437 `max(self, 0)`, REFUSED both) and 4810 (VERIFY-FAIL -> REFUSAL). Cost measured on the 902 claimed corpus
files (no-proof screen, base vs candidate): exactly 4621 / 4810 change; a first candidate also refused 3282 (PASS,
`(rec.get(..) or {}).get`) and 3345 (PASS, `key=lambda v: v + 1`) -- fixed (an `or`'s earlier operands are not None; a
lambda key's arithmetic over numbers is a number) before landing. \trusted count 442 unchanged; no axiom.

## RESIDUALS (honest)

Not judged by this rule (admitted as before): a receiver whose classes are underivable (`#UND` / `#UNK`), `Any` or `object`
(the R-gate analogue for attributes is not built -- BUILT since by route #443, executor h442: an underivable
receiver is now refused under an AttributeError claim; and #442 restricts `isinstance` narrowing to resolved builtin classes); the attribute's EXISTENCE on a single user class (pre-existing checks);
`isinstance(R, Sequence)`-style narrowing to an abstract class. Over-refusal (sound direction, measured cost 0 in the
corpus): narrowing by `type(R) is C`, `R == "lit"`, `hasattr`, TypeGuard functions, `match` patterns, a `try` /
`except AttributeError` around the access, a guard on an attribute path followed by any call (`self.l.size() +
self.r.size()` under one guard), and a receiver of two or more user classes even when all define the attribute.
