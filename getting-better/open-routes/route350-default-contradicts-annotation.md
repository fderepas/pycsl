# OPEN ROUTE #350 — A PARAMETER DEFAULT THAT CONTRADICTS ITS ANNOTATION IS NOT CHECKED
**Status: REPAIRED, candidate (gen #37, 2026-10-25; opened 2026-10-24), Severity 1.** Red-team round 25 (2026-10-24, probes around the #336-#342 repairs); driver-reproduced on main 78c92b39 (rc=0 "Verification SUCCESS"; CPython violates; see `scratchpad/rt25/driver-repro.txt`).
Witnesses `witnesses-r350/`: `n06_default_float_for_int.py`, `n07_default_none_for_str.py`.

`def f(x: int = 0.5)` PROVES `ensures x % 1 == 0` (CPython `f()` = 0.5); `def f(s: str = None)` PROVES `len(s)` under `no_exception` (CPython TypeError). The body is verified for the annotation while the default is outside it.

Repair: Require each default to type-check against its annotation (literal kind check, or a precondition obligation at the default), else refuse.

## REPAIR (2026-10-25, r350 executor off 5c3b3413; code 2bfdb686 / b67bbe0f, corpus 24945d20, census c40dd1dd, docs 656526be)
**Design: refuse, not obligate.** One inline block of `_run_pipeline` after route #273's definition-time
block (mirror twin `\trusted`; no new def; no emission change; ledger 3), over a FRESH parse of the source
(Module 5 has already rewritten annotations in place, route #336), restricted to the defs of route #273's
lowered trees. CENSUS before landing (CPython-`ast` prototype over pycsl-reference, python-reference, the
self-annotate mirror, `pycsl_lib`): every contradicting default in a LOWERED body was 0698 (`sep: str =
None`, the call-site `""` fill, i.e. the model of this defect) and the mirror's
`Module2_Parser.expect_name(val: str = None)`; 23 mirror + 1 `pycsl_lib` (`strmod.capwords`) `int`/`str =
None` defaults sit on `\trusted` stubs (outside: their contract is assumed). Non-literal defaults of a
scalar arm: only route #273's already-refused nested-def calls / arithmetic (2960-2966) and bare names
(module constants 1478 / 4606, never-rebound outer parameters 2967 / 4606: resolved and admitted), so an
obligation at the default (def-time state) was not worth building; they are refused. `expect_name`'s
default became `""` in the live parser AND the mirror (every caller passes a literal name or nothing;
`val != ""` replaces `val is not None`; `Optional[str]` was measured: the vararg `at_name(val)` and the
f-string do not type-check on the union) — its mirror emission moved one line and was re-proved whole-file.
RULE (`PYCSL-SEM-DEFAULT-ANNOTATION-MISMATCH`): every annotated positional / positional-only / keyword-only
parameter default of every def in a lowered tree (functions, methods, nested defs) must be admitted by one
ARM of its annotation (split through once-bound module aliases, `Optional`, `Union`, `|`, `Annotated`,
string forward references): `None` only by a `None` arm / `Any` / `object` / a TypeVar; `int` <- int/bool
literal, `float` <- int/float/bool, `bool` <- bool, `str` <- str, `bytes` <- bytes, `Literal[..]` <- one of
its values; `List` <- list display, `tuple` <- tuple display, `Dict`/`Mapping` <- dict display, `Set` <- set
display, `Sequence` <- list/tuple display or string; a container / class / other arm <- a non-literal
expression, never `None` or a scalar literal for a container or a class of the file. A bare-name default
resolves to a once-bound module constant or an outer parameter of the same annotation; any other
non-literal default of a scalar / Literal arm is refused. Display elements are checked when one arm
admits the display.

**Probe table** (full pycsl proof via heavy.sh; base = 5c3b3413 worktree; CPython from `__main__`):
| probe | corpus | CPython | base | after |
|---|---|---|---|---|
| n06 `def f(x: int = 0.5)`, `\result == 0` for `x % 1` | 4710 | 0.5 | rc=0 PROVED | rc=1 REFUSED |
| n07 `def f(s: str = None)`, `len(s)` under no_exception | 4711 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| a01 method `m(self, x: int = 0.5)` | 4712 | 0.5 | rc=0 PROVED | rc=1 REFUSED |
| a02 kw-only `*, x: int = None`, no_exception | 4713 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| a03 nested `def g(x: int = "a")`, no_exception | 4714 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| a06 `K = 0.5; def f(x: int = K)` | 4715 | 0.5 | rc=0 PROVED | rc=1 REFUSED |
| a07 `s: str = False`, `len(s)` under no_exception | 4716 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| a09 `Num = int; def f(x: Num = None)`, no_exception | 4717 | TypeError | rc=0 PROVED | rc=1 REFUSED |
| a10 `x: Literal[1, 2] = 3`, `\result in {1, 2}` | 4718 | 3 | rc=0 PROVED | rc=1 REFUSED |
| a05 `xs: List[int] = (1, 2)`, store, no_exception | 4719 | TypeError | rc=1 FAIL | rc=1 REFUSED |
| a04 positional-only `x: int = 0.5`, caller omits it | 4720 | 0.5 | rc=1 FAIL | rc=1 REFUSED |
| a08 `xs: List[int] = [0.5]` | — | 0.5 | REFUSED (R2 mutable default) | REFUSED (same) |
| control: int/float/bool/str/module-constant/Optional/signed/kw-only `int = True`/outer-param defaults | 4721 | ok | rc=0 PROVED | rc=0 PROVED |
| 0698 `sep: str = None` filled `""` (was PASS) | 0698 | — | emitted, PROVED | rc=1 REFUSED (now expected FAIL) |
**Blast radius** (shared run with route #351): root 0 MOVED / 1 GONE (0698, intended, `--expect-gone 0698`)
/ 0 APPEARED; pyref 2186/2186 0/0/0; mirror 53/53 1 MOVED (`frontend__Module2_Parser`: the `expect_name`
default, `pycsl_none_str` -> `""` in one guard) / 0 GONE — whole-file PROVED via heavy.sh `HEAVY_LOW=1`
(868 goals Valid, rc=0): no OWED proof.
**Gates** (routes #350 + #351, one run, all rc=0): see route #351's REPAIR (shared).
**Residuals.** (1) `\trusted` / `\abstract` defs are not checked (their contract is assumed; the call-site
fill of an omitted `None` as `0` / `""` / `0.0` stays part of that trust — 23 mirror stubs, `strmod.capwords`).
(2) Dataclass / NamedTuple field defaults (`x: int = 0.5` in a class body, a synthesized `__init__`
parameter) are outside this parameter rule. (3) A non-literal default of a container / class arm (a call, a
name) is admitted on its head only (`xs: List[int] = make()` is not checked against `make`'s return type;
the wrong-class instance `c: C = D()` likewise). (4) An imported / unknown annotation head admits any
non-`None` literal (`x: Fraction = 0`), relying on route #336's erasure. (5) Over-refusal: a non-literal
scalar default (`x: int = 2 ** 10`, `x: float = math.pi`) — 0 users.
