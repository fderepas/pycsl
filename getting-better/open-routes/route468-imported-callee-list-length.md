# OPEN ROUTE #468 — IMPORTED (stub) CALLEE GROWS / SHRINKS a list argument: an un-contracted helper of another module is a bodyless `val g (x: array int) : unit writes { x }` (route #317), but Why3's `array` length is immutable under `writes`, so `len(a)` after `g(a)` is still the entry length (append / pop / clear / del / += / slice assignment / heappush / insort / aliases through the helper) -- the route #49 defect, repaired for local callees, survives at the import boundary (contract broken)
**Status: REPAIRED (executor x1, driver run #3, 2026-10-29), Severity 1.** Red-team round 38 (2026-10-29, on a9eac4a08 after #460-#462: 688 probes / 155 proved / 142 confirmed; rt37's 83 all closed except #463 / #464). Census TSV `scratchpad/rt38/census.tsv`; the family block below is quoted from `scratchpad/rt38/FINDINGS.txt`.
Witnesses `witnesses-r468/` (34): `g2_m270_append.py`, `g2_m271_unbound_append.py`, `g2_m272_iadd.py`, `g2_m273_slice_grow.py`, `g2_m274_heappush.py`, `g2_m275_bisect_insort.py`, `g2_m276_getattr_append.py`, `g2_m277_alias.py`, `g2_m278_container_alias.py`, `g2_m279_for_alias.py`, `g2_m280_closure.py`, `g2_m281_lambda.py`, `g2_m282_map_append.py`, `g2_m283_operator_iadd.py`, `g2_m284_dunder_iadd.py`, `g2_m285_bound_method_alias.py`, `g2_m286_forward_to_other_helper.py`, `g2_m287_forward_to_third_file.py`, `g2_m288_extend_self.py`, `g2_m289_insert.py`, `g2_m290_imul.py`, `g2_m291_walrus.py`, `g2_m292_star_call.py`, `g2_m293_setdefault_alias.py`, `g2_m294_class_method.py`, `g2_m300_pop.py`, `g2_m301_clear.py`, `g2_m302_del_item.py`, `g2_m303_slice_clear.py`, `g2_m304_remove.py`, `g2_m306_claimed_helper_assigns_list.py`, `g2_m314_abstract_assigns_append_same_file.py`, `g2_m317_index_after_grow.py`, `g21_l216_abstract_assigns_pop.py`.

Driver repro: 17/17 family exemplars (scratchpad/rt38/verify/, F8 without --import-path) rc=0 Verification SUCCESS on main a9eac4a08 at 2026-10-29T14:55Z, each violating under CPython (scratchpad/rt38/driver-repro.txt).

```
F4 IMPORTED (stub) CALLEE GROWS / SHRINKS a list argument: an un-contracted helper of another module is a bodyless `val g (x: array int) : unit writes { x }` (route #317), but Why3's `array` length is immutable under `writes`, so `len(a)` after `g(a)` is still the entry length (append / pop / clear / del / += / slice assignment / heappush / insort / aliases through the helper) -- the route #49 defect, repaired for local callees, survives at the import boundary (contract broken) (34)
  EXEMPLAR: g2/m270_append.py (h270: un-contracted `def g(x: List[int]) -> None: x.append(1)`; f: `#@ requires \length(a) == 2` `#@ ensures \result == 2` `g(a); return len(a)`)
  CPYTHON: f([0, 0]) returns 3 (VIOLATION contract 3); pop / clear / del / slice-clear / remove return 1 or 0
  WHY IT PROVES: the stub is emitted `val g (x: array int) : unit writes { x }` (route #317's default frame) but a Why3 `array`'s length is not a mutable field, so `writes { x }` havocs the cells and keeps `Array.length a = 2`: every length-changing helper body is invisible (24 / 25 spellings PROVE, incl. heappush, insort, aliases, closures, map(x.append, ..)). The local-callee version of this defect was route #49 (corpus 1081) and is repaired by the local lowering; the import boundary still uses the fixed-length array. The same holds in ONE file at an `\abstract` boundary whose (true) `#@ assigns x` lets the body append / pop (g2/m314, g21/l216); a plain same-file callee (m307, g21 l210-l214 l217-l220: recursion, interface, verify_module, no_inline, sibling stubs) is refused.
  PROPOSED SYSTEMATIC REPAIR: MODEL THE LENGTH AT THE STUB BOUNDARY: a `writes { x }` on a list parameter of a bodyless val must also havoc its length -- emit the stub over the same resizable list model the local lowering uses since #49 (or a `{ mutable elts: array int }` wrapper whose `writes { x.elts }` replaces the whole array), or else, until that exists, REFUSE a stub whose (route #317) default frame writes a list parameter when the caller reads the length / indexes it after the call (PYCSL-VAL-ARG-LENGTH-UNFRAMED). Witnesses m270-m304 (refused / not proved); control: a helper that only stores x[0] = 1 (PASS, cells havoced).
  PROBES: g2/m270_append.py g2/m271_unbound_append.py g2/m272_iadd.py g2/m273_slice_grow.py g2/m274_heappush.py g2/m275_bisect_insort.py g2/m276_getattr_append.py g2/m277_alias.py g2/m278_container_alias.py g2/m279_for_alias.py g2/m280_closure.py g2/m281_lambda.py g2/m282_map_append.py g2/m283_operator_iadd.py g2/m284_dunder_iadd.py g2/m285_bound_method_alias.py g2/m286_forward_to_other_helper.py g2/m287_forward_to_third_file.py g2/m288_extend_self.py g2/m289_insert.py g2/m290_imul.py g2/m291_walrus.py g2/m292_star_call.py g2/m293_setdefault_alias.py g2/m294_class_method.py g2/m300_pop.py g2/m301_clear.py g2/m302_del_item.py g2/m303_slice_clear.py g2/m304_remove.py g2/m306_claimed_helper_assigns_list.py g2/m314_abstract_assigns_append_same_file.py g2/m317_index_after_grow.py g21/l216_abstract_assigns_pop.py
```

## REPAIR (executor x1, driver run #3, 2026-10-29, off daf5c3d1f; annotations §7.282, translational §T.6.292)

Code inline at the end of `_run_pipeline` (no gate: a contract defect, not a claim): for each IR function emitted
as a bodyless `val` (`trusted` -- every imported function --, or `abstract`) and each `list` / `bytearray` parameter,
the function's SOURCE body (this file and the files its imports resolve to, transitively; the IR body only when no
source is found -- the IR drops a closure, a lambda, `getattr(x, "append")(1)`) must keep the length: the parameter
occurs only as an element store / element or slice read, an argument of a non-mutating builtin (`len`, `sorted`,
`sum`, `list`, `enumerate` ...), a comparison or fresh-list `+` / `*` operand, a loop iterable, or the receiver of
`sort` / `reverse` / `copy` / `count` / `index`. Anything else is REFUSED, `PYCSL-R468-VAL-LIST-LENGTH` -- the route #49
rule (a verified body's `append` / `pop` / ... on a list parameter is refused) applied to the bodyless boundary. Every
list parameter is checked, written or not: route #317's fixpoint misses spellings (`list.append(x, 1)`) and a `val`
without `writes { x }` keeps the length just the same.

Red-team witnesses (`witnesses-r468/`): 34/34 PROVED on daf5c3d1f, 34/34 REFUSED by #468. Corpus witnesses 7275-7281
(append, pop, closure, getattr-append, a truthful `#@ assigns x`, a same-file `\abstract` with `assigns x`, heappush):
PROVED at base, REFUSED. Control 7287 (`x[0] = 1` only): PROVED at base and candidate.

GATES (worktree pycsl-x1 off daf5c3d1f; bases = v13/ca, v13/ma, the emission of 33f7ac681, docs-only since):
fidelity check-self-annotate-sync rc=0 (938 un-trusted mirror functions verbatim), self-annotate-mirror-check rc=0
(53); doc-coherency rc=0. Byte-diff root 2604 -> 2609 .mlw, 0 MOVED / 0 GONE / 0 APPEARED (5 new controls); pyref
2186 / 2186 0/0/0; mirror 53 / 53 0/0/0 (no OWED proof). Planes / ledgers: see the x1 commit message (fast planes
61/61 after naming the import-raising fixtures in check-corpus-executes; trusted-reasons, assumed-facts,
refusal-witness-coverage, refusal-advice-audited, dropped-mutation, getattr-erasure, open-route-carriers,
frame-honesty, raises-honesty, clause-survival, stdlib-modules-verify all rc=0; trusted 437 unchanged).
OVER-REFUSAL COST, measured: the 24 claimed corpus files that import a non-standard-library module (23 expected
FAIL, 1 PASS = 6642) -- 6642 still PROVES (its un-claimed `inc` is on the #467 allow-list); 0 pyref / mirror /
pycsl_lib files carry a claim, so #466 / #467 / #472 cannot fire there. #466's judge run over every multi_file_lib
helper imported under a claim: 51 of 58 accepted, 1 refused by #466 (`circ_b` imported first: CPython raises
ImportError too, the plane's KNOWN_LOAD_FAILURES says so), 6 refused by older routes. #468 (no claim gate): a wide
first cut refused corpus 3382 (a `\trusted` `tid(x): return x`) and 11 mirror files (all through explicit
`\trusted` stubs or stubs no verified code of the file calls) -> narrowed (returning the list is a read; an explicit
`\trusted` def is a declared assumption; only vals the verified code references are judged): 0 GONE.

## RESIDUALS
- An EXPLICIT `#@ \trusted` def (here or in its own module) is a declared assumption, its frame included (the
  trusted surface's frames are check-trusted-frame-honesty's ledger): its length is not judged. Measured: the
  wide rule (every bodyless `val`) refused 11 mirror files, all through `\trusted` stubs or stubs no verified code
  of the file calls; narrowed to (a) not explicitly trusted, (b) read by verified code of the file.
- A list FIELD of a record written by a bodyless method (`self.xs.append`) is not covered (parameters only).
- The source body is found by name (`name`, `<class>__name`) over this file and its transitive imports; with no
  source the IR body is scanned (the IR drops some spellings).
