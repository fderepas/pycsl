# OPEN ROUTE #351 — A READ-ONLY VIEW ESCAPES THROUGH A MUTABLE-TYPED RETURN SLOT
**Status: REPAIRED, candidate (gen #37, 2026-10-25; opened 2026-10-24), Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r351/`: `n03_view_returned_as_list.py`.

`as_list(xs: Sequence[int]) -> List[int]: return xs` PROVES; a separate verified `poke(ys: List[int])` under `no_exception` stores `ys[0] = 5`; CPython `poke(as_list((1, 2)))` TypeError. Route #336's READONLY-VIEW-STORE covers stores on the parameter, not its escape. Weaker (two functions); the one-driver chain n09 FAILs.

Repair: Refuse returning (or storing / passing into a mutable-typed slot) a read-only view parameter where the declared type is a mutable container.

## REPAIR (2026-10-25, r350 executor off 5c3b3413; code 2bfdb686, corpus 24945d20, census c40dd1dd, docs 656526be)
**Design: refuse the escape, keep route #336's model.** One inline block of `_run_pipeline` right after
route #350's (mirror twin `\trusted`; no new def; no emission change; ledger 3), over the same fresh parse
of the source (Module 5 has rewritten `Sequence` -> `List` in place, so the unified AST no longer shows the
view), restricted to route #273's lowered trees. A new code rather than R336's: R336 lives in Module 5
(a mirrored, converted file) and refuses stores on the parameter itself; this one is the flow out of it.
CENSUS before landing: 44 corpus / pyref files mention `Sequence` / `Mapping` / `tuple[T, ...]`; a
`--no-proof` run of all of them on the candidate tripped the new rule on NONE (only 0698, route #350's);
mirror 0 (no mirror file changed verdict but Module2_Parser, route #350's); `pycsl_lib` via
check-stdlib-modules-verify (below).
RULE (`PYCSL-SEM-READONLY-VIEW-ESCAPE`): VIEW names = the read-only-view parameters of any def of the tree
(`Sequence[..]` / `Mapping[..]` / `tuple[T, ...]` through module aliases, `Optional`, `Annotated`, string
annotations) plus, to a fixpoint, every name bound (`=`, walrus, annotated, `for y in (display)`) to an
expression whose value may be a view (the name, a slice of it, `+` / `*` on it, a conditional / `and` /
`or` / walrus / starred / display position holding one). REFUSED: (a) `return e` (a lambda body) unless the
innermost def's return annotation is view-safe (`Sequence`, `Mapping`, `tuple[T, ...]`, `Iterable`,
`Collection`, `Reversible`, `Container`, `Iterator`, `AbstractSet`, `Any`, `object`, `None`, a TypeVar,
through `Optional` / `Union` / `|`) and `e` holds no display; (b) `e` stored into an attribute / subscript
target, or bound to a name annotated outside that set (`ys: List[int] = xs`); (c) `e` passed to a call other
than route #336's read-only builtins (a bare view PARAMETER there stays route #336's Module 5 refusal);
(d) a subscript store / `del` / augmented assignment / mutating method call through an ALIAS.

**Probe table** (full pycsl proof via heavy.sh; base = 5c3b3413 worktree; CPython from `__main__`):
| probe | corpus | CPython | base | after |
|---|---|---|---|---|
| n03 `as_list(xs: Sequence[int]) -> List[int]: return xs` + verified `poke` store | 4722 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| b04 `return xs if c else xs` into `-> List[int]` | 4723 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| b06 `Mapping[str, int]` returned as `Dict[str, int]` + verified store | 4724 | TypeError (mappingproxy) | rc=0 PROVED | rc=1 REFUSED |
| b01 `ys = xs; return ys` into `-> List[int]` | 4725 | TypeError | rc=1 FAIL | rc=1 REFUSED |
| b03 `ys: List[int] = xs; ys[0] = 5` | 4726 | TypeError | rc=1 FAIL | rc=1 REFUSED |
| b07 `self.items: List[int] = xs`, later store | 4727 | TypeError | rc=1 FAIL | rc=1 REFUSED |
| b02 `ys = xs; ys[0] = 5` | 4728 | TypeError | REFUSED (abstract `subscript_set`) | REFUSED (#351 first) |
| b05 one-driver chain `ys = as_list(xs); ys[0] = 5` (route file's n09) | — | TypeError | REFUSED (R336) | REFUSED (R336) |
| b08 closure `def g() -> List[int]: return xs` | — | TypeError | REFUSED (closure lift) | REFUSED (same) |
| control: view reads; `-> Sequence[int]` / `-> Mapping[str, int]` returning the view | 4729 | ok | rc=0 PROVED | rc=0 PROVED |
**Blast radius** (shared run with route #350): root 0 MOVED / 1 GONE (0698, route #350) / 0 APPEARED;
pyref 2186/2186 0/0/0; mirror 53/53 1 MOVED (`frontend__Module2_Parser`, route #350's `expect_name`
default; whole-file PROVED) / 0 GONE. No OWED proof.
**Gates** (routes #350 + #351, one run, all rc=0): 18 corpus witnesses (4710-4720, 4722-4728) all REFUSED
after — at base 12 PROVED (9 #350 + 3 #351), 5 VERIFY-FAIL, 1 REFUSED — plus 0698 PROVED -> REFUSED, controls 4721 / 4729 PROVED at base and after; byte-diff root (`--expect-gone
0698`) / pyref / mirror (`--expect-moved frontend__Module2_Parser`, `--min-files 50`) above; fidelity
`check-self-annotate-sync.sh` (926 verbatim) + `self-annotate-mirror-check.sh` (53/53); `run-soundness-planes.sh`
fast 61/61 green; check-getattr-erasure OK (DECLARED 0); STDLIB_GATE; doc-coherency --check OK;
ASSUMED_GATE; check-dropped-mutation OK (0/51/5/0); check-refusal-witness-coverage OK (291 demonstrated, 5
undemonstrated = ceiling; rows via `_census_row`); check-trusted-reasons OK (420/420, unclassified 259);
check-trusted-raises-honesty OK (ratchet 61); check-assigns-underdeclaration --transitive OK (TRAP 3, HOLE 0).
**Residuals.** (1) View names are syntactic: a nested def's parameter shadowing an outer view name is
over-refused; a view reached through a container element (`Sequence[Sequence[int]]`'s `xs[0]` returned as
`List[int]`), an attribute of an object holding one, or a call result (`id_(xs)` with a view-typed
`id_`) is not followed. (2) A view-safe return annotation that wraps the view (`-> Tuple[Sequence[int],
int]: return (xs, 1)`) is over-refused (display rule). (3) `*args` (a tuple) is not a view parameter here.
(4) Over-refusal: passing an alias of a view to any user function, even one that only reads it (the same
bluntness as route #336 for the parameter itself); 0 users measured.
