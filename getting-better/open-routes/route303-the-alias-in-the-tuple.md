# OPEN ROUTE #303 — A DICT ALIASED THROUGH A TUPLE-UNPACKING ASSIGNMENT IS A VALUE COPY (bypasses #59 and r2c-local R1)
**Status: REPAIRED (gen #37, 2026-10-22; opened the same day), Severity 1.** Red-team round 11; driver-reproduced at 387d8da9 (4 probes rc=0; CPython violates).
Witnesses `witnesses-r303/`: `h, k = g, 1; h["G"] = 5; return g["G"]` proves `== 0` (CPython 5, l09); swap `g, h = h, h` (l12);
r2c-local path write-back through a tuple-bound alias of another local (l01) and of a PARAMETER root under `assigns \nothing`
(l08: the caller's dict is mutated). `h, k = g, 1` lowers to `let (_tu_h, _tu_k) = (!g, 1) in h := _tu_h` (a map copy). The
route #59 alias refusal (statements.py ~1459) and r2c-local's R1 ("every binding of the root is a dict literal") inspect plain
`x = y` assignments only. Repair: treat every TupleUnpack / swap / starred-free unpack whose value element is a mutable
collection name (or a call result per #283/#295) as an alias binding for #59/#279/#283/#295 AND for r2c R1; census every
binding form that can alias (tuple/list unpack, for-targets over containers of dicts, with-as, walrus inside tuples).

## REPAIR (2026-10-22, r303 executor off 388cd100; commits 264bc43f + f1ff44fe + 8991cb17 + 28f1e348 + route docs)
Probe table (`src/pycsl/pycsl.py`, full proof, rc; CPython ground truth in each corpus file's `__main__`):

| shape | 388cd100 | after |
|---|---|---|
| route witnesses `witnesses-r303/l01`, `l08`, `l09`, `l12` | rc=0 PROVED (x4) | rc=1 REFUSED (x4) |
| 3650 `h, k = g, 1; h["G"] = 5; return g["G"]` (= l09) | PROVED | REFUSED (#303) |
| 3651 swap `g, h = h, h` (= l12) | PROVED | REFUSED (#303) |
| 3652 r2c path write-back through a tuple-bound local root (= l01) | PROVED | REFUSED (#303; r2c R1 also refuses on its own) |
| 3653 r2c write-back through `h, k = p, 1`, PARAMETER root, `assigns \nothing` (= l08) | PROVED | REFUSED (#303; r2c R1 also) |
| 3654 REVERSE `h, k = g, 1; g["G"] = 5; return h["G"]` | PROVED | REFUSED (#303) |
| 3655 `h, k = p, 1; h["G"] = 5; return p["G"]` (dict param) | FAIL | REFUSED |
| 3656 / 3657 / 3658 list `append`, list element store, set `add` through a tuple alias | FAIL (L3-tc) | REFUSED |
| 3659 `h, k = idt(g)` (callee returns `(d, 1)`) / 3660 `h, k = g["G"], 1` (sub-collection read) | FAIL (L3-tc) | REFUSED |
| 3661 plain REBIND `h = g` of a declared dict, then `h["G"] = 5; return g["G"]` | PROVED | REFUSED (#59) |
| 3662 chained `h = k = g` (desugared to rebinds) | PROVED | REFUSED (#59) |
| 3664 dict rebind at the END of a loop body, store at the TOP (back-edge) | PROVED | REFUSED (#59) |
| 3663 CONTROLS: permutation swap `g, h = h, g` + store, read-only tuple alias, `a, b = b, a + b`, fresh literal slot + store, read-only rebind, read-only rebind in a loop | (new) | PASS |

Rules (inline, no new def/field/axiom -- ledger 3; mirror twins of the three touched methods are `\trusted` stubs that
already carry/need no new `raises` marker: `_reset_function_state` and `_handle_assign_stmt` already raise, `_handle_expr_stmt` already raises for r2c):
(1) `_reset_function_state` (where #301 refuses; lowered bodies only): every TupleUnpack slot whose value element (or,
for a non-literal RHS, the whole value) mentions a non-scalar name, a known-collection method receiver, or a
`self.` call/field is an ALIAS BINDING; its class is closed over every name-to-name `Assign` and every other such
slot; any in-place mutation through a class name anywhere in the function (element/slice store, `del`, a mutator
method on it or below it, an augmented assignment of a non-scalar, passing it to a user function that may write it)
refuses (`PYCSL-M6-MUTATION-THROUGH-UNPACK-ALIAS`). Flow-insensitive (may refuse a dead alias). A pure PERMUTATION
(distinct names, same set both sides) is exempt. Names under a CALL are kind-filtered (list vs dict/set; target kind
from its declared type, else its use) -- the first cut refused the mirror's own `_refine_tuple_return_type`
(`array_vars, dict_vars = IRScanner.find_array_and_dict_vars(body_stmts); array_vars |= ...`, GONE in the mirror
sweep), the #283/#295 precedent.
(2) r2c-local R1: a TupleUnpack target, a tuple `for` target (`tuple_targets`) or a walrus binding the root makes it
non-fresh (refused). Verified in isolation (rule 1 disabled): 3652/3653 refuse with "not fresh; route #303".
(3) Route #59's guard now runs for a REBIND of a declared dict/set local (`h := !g`, the same copy), and when the
binding is inside a loop its mutation walk covers the whole function body (a store before the binding runs again on
the next iteration), as #279's escape arm does.
CENSUS of binding forms that can alias: tuple/list unpack (literal, swap, call result, sub-collection read) -> rule 1;
plain rebind / chained `h = k = g` -> rule 3 (were PROVED false); rebind in a loop back-edge -> rule 3 (was PROVED
false); `for h in gs` over a list of dicts -> already refused (#289); walrus `(h := g)` -> L3-tc FAIL at base and after
(not a proof; r2c R1 covers it); `with ... as` -> already refused (with-as boundary); list-target `[h, k] = ...` and
starred/nested -> refused by #301; unannotated tuple target subscript-stored -> Module 4 rejects ("undefined variable").
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (1987 base / 1988 candidate, 15 new sources, 14 refused);
pyref 0/0/0 (2186/2186); mirror 0/0/0 (53/53). No mover: no M1 re-proof and NO mirror proof OWED.
Gates (logs in the r303 executor scratchpad `r303/`): byte-diff-sweep base/after rc=0; byte-diff-compare root rc=0,
pyref rc=0; mirror-emit-sweep base/after rc=0, compare `--min-files 45` rc=0; check-self-annotate-sync.sh rc=0 (926
verbatim); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast rc=0, 61/61 green (incl.
refusal-witness coverage 249 demonstrated, UNMATCHABLE 10). Census rows for 3650-3662, 3664 measured via `_census_row`.
`--slow` NOT run (time).
Residuals: (1) the call-argument kind filter follows #283/#295: a callee returning an ELEMENT of a differently-kinded
argument (`h, k = first(gs)`, `gs: List[Dict]`) is not treated as an alias -- measured today it FAILS (rc=1, no false
proof), but it is not refused by construction. (2) #59's rebind arm keys on `_current_sig_func_name` for the in-loop
whole-body walk; a method whose IR name does not match falls back to the `rest`-only walk. (3) Completeness: any
mutation in a function that tuple-binds a collection to another name is refused, even when the alias is dead
(flow-insensitive); bind collections with their own statement or copy them (`dict(g)`, `g.copy()`, `g[:]`).
