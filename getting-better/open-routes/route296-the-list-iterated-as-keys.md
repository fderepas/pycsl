# OPEN ROUTE #296 — AN hval LOCAL HOLDING A LIST, ITERATED AS A BARE VARIABLE, IS ITERATED AS DICT KEYS
**Status: REPAIRED (gen #37, 2026-10-22; opened 2026-10-22), Severity 1.** Found by the ch30 drain; driver-reproduced at 873ead89 (rc=0; CPython False).
Witness `witnesses-r296/fp_list_as_keys.py`: `xs = d.get("xs") or []; for x in xs: return isinstance(x, str)` with
`ensures \result == True` proves; CPython `first_is_str({"xs": [{"k": 1}]})` is False. The bare `for x in <pyval local>`
branch of `_classify_iterable` (stmt_control_flow.py; the dict-KEY arm, Tier-5 union/match cluster) treats every pyval local as a
dict and binds x to an arbitrary key string. Repair: take the key path only when the local is provably a dict (HMap / dict
literal / dict-typed source); a list carrier must take the R2b element path (or decline). The same branch serves the converted
`_maybe_inject_union_return` -> corpus + mirror byte-diff and re-proof of movers required.

## REPAIR (2026-10-22, worktree pycsl-r296 off 9b84ec85)
Root cause (located on the witness emission): the bare `for x in <pyval local>` arm of `_classify_iterable` lowered
EVERY `hval` local as `hval_as_map xs` and bound `x` to `hval_keys_get (hval_as_map xs) !idx`, a `string`
(`_handle_for_stmt` then typed `x` symbol-type "str", so `isinstance(x, str)` folded to True). A pyval local is
only ever bound by a READ (`.get` / subscript / `or`-default / loop element) of an arbitrary `hval`, so its carrier
is never statically known to be an `HMap`; for an `HArr` the elements were replaced by arbitrary strings.

Probe table (`pycsl.py`, rc; CPython ground truth in each file's `__main__`; base = 9b84ec85; census probes and
logs under the session scratchpad `r296/{p,pb,pa,wit}`):

| shape | base | after |
|---|---|---|
| route witness `xs = d.get("xs") or []; for x in xs: return isinstance(x, str)` (3490) | PROVED | FAIL |
| `xs = d["xs"]` (3491), `xs = d.get("xs", [])` (3493), `xs = d.get("xs")` (probe c02) | PROVED | FAIL |
| `xs = d.get("xs") or {}` holding a list (3494) | PROVED | FAIL |
| NESTED `for row in d["rows"]: for x in row` (loop target iterated bare) (3492) | PROVED | FAIL |
| literal holder `[{"k": 1}]` false claim (3496), `[[1]]` nested false claim (3499) | PROVED / FAIL | FAIL / FAIL |
| int carrier under `no_exception \all` (3500, CPython TypeError); probes c20-c22 (`.items()` on a list, bare/direct int) | FAIL | FAIL |
| tuple target `for a, b in xs` (c23), str carrier `for c in s` (c16) | FAIL | FAIL |
| `.keys()` / `.values()` on a pyval local (c06/c07), `for x in d.get("xs") or []` direct (c04), conditional (c09), rebind (c11), comprehension / `all(...)` / `in` / `list(xs)` (c12-c15, c18) | FAIL | FAIL (untouched) |
| control 3495: `["a", "b"]` real elements, `isinstance(x, str)` | PROVED | PASS |
| control 3497: `{"a": 1}` dict carrier, keys are `str` | PROVED | PASS |
| control 3498: `[["a"]]` nested real elements | FAIL (incomplete) | PASS |

Rule (inline; mirror twins of `_classify_iterable` / `_handle_for_stmt` are `\trusted`; no new def/field; no
axiom): (i) the dict-KEY arm and the matching "str" loop-target typing (`_is_pyval_keys`) are REMOVED; (ii) the R2b
judgement in `_handle_for_stmt` now also admits a BARE pyval `Var` (same fail-closed guards: single target, no
in-place mutator/store in the body on the root, a pyval local or the target), so `x` binds a real `hval` and the
iterable is snapshotted once; (iii) for a bare `Var` the R2b match gains an `HMap` arm, so the dict-KEY view is
taken exactly when the carrier IS a dict: `HArr l` -> `hval_list_nth l !idx` with the exact `hval_list_len l`;
`HMap _` -> `HStr (hval_keys_get (hval_as_map _hv) !idx)` with `hval_values_len (hval_as_map _hv)` (the same
uninterpreted key over-approx as the `.items()` walk); any other carrier -> the uninterpreted
`hval_iter_len_other` / `hval_iter_get_other` (never a constant/empty iteration). Every non-`Var` R2b iterable keeps
its emission byte for byte; (iv) when R2b declines (a mutating body) the loop falls to the int-typed
`iter_length` fallback, which an `hval` fails at Why3 type-check (fail-closed); (v) `s.startswith(p)` /
`s.endswith(p)` with an `hval` argument projects `hstr_of p` (exact on `HStr`; CPython raises TypeError on any
other carrier) and is NOT projected under `no_exception` (raw `hval` -> L3-tc, fail-closed). A side defect fixed on
the way: the R2b marker key made a marked bare `Var` fail typed `VarExpr` normalisation and lower to `""`; the
arm now lowers a copy without the marker.

Census (iteration forms over pyval values): bare local bound by `.get(k)` / `.get(k, [])` / `.get(k) or []` /
`or {}` / subscript / nested loop target / rebind / conditional, tuple target, str and int carriers, `no_exception`;
`.keys()` / `.values()` / `.items()` on a local; direct `for x in d.get(..) or []`; comprehensions, generator
`all(...)`, membership `in`, `list(xs)`. Only the bare-local arm (5 binding shapes + nested target) proved; all now
FAIL or PASS faithfully; the rest were and stay fail-closed.

Blast radius (base = worktree at 9b84ec85, after = final tree; full sweeps via heavy.sh): corpus root 0 MOVED /
0 GONE / 0 APPEARED (1913 -> 1924 .mlw; the 11 extra are the new sources 3490-3500, `--new-source`), compare rc=0;
pyref 0/0/0 (2186/2186) rc=0; mirror 1 MOVED (53/53): `module6_whyml__stmt_control_flow` =
`_maybe_inject_union_return`'s `for ctor_name in constructors` now iterates per carrier (`HMap` keys as `HStr`) and
its `val.startswith(ctor_name)` reads `hstr_of ctor_name` — exactly the intended change (compare rc=0 with
`--expect-moved module6_whyml__stmt_control_flow`). That mirror type-checks (L3-tc ok) and
`--fun controlflowstmtmixin___maybe_inject_union_return` PROVES (rc=0, 535 goals). OWED to the driver, the
whole-file proof: `cd <tree> && . scratchpad/g29/env.sh && HEAVY_LOW=1 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh
.venv/bin/python3 src/pycsl/pycsl.py --import-path src/pycsl src/self-annotate/src/module6_whyml/stmt_control_flow.py`.
Gates (logs under the session scratchpad `r296/`): route witness rc=0 -> rc=1; witness table above (3490-3500, base
rc 0 for 3490-3497, after rc 1 for every false claim, rc 0 for controls 3495/3497/3498);
check-self-annotate-sync.sh rc=0 (925 verbatim); self-annotate-mirror-check.sh rc=0 (53);
`run-soundness-planes.sh` fast rc=0 (61/61) and `--slow` rc=0 (84/84 green, every plane). Ledger unchanged (3
axioms); no `\trusted` marker added; no new def/field; the witnesses are FAIL (not refusals), so the
refusal-witness census does not move.
Residuals: (1) MODEL ASSUMPTION, pre-existing and UNDECLARED: the `hval` model gives every nested dict STRING
keys (`HMap` over `hpairs` keyed by `string`), so `for k, v in xs.items(): return isinstance(k, str)` PROVES for
`d = {"xs": {1: 2}}` (CPython False) at base and after (repro: session scratchpad `r296/p/c08_items_local.py`).
The new `HMap` key arm of a bare loop inherits the same assumption (probe `r296/p/c24_intkey_bare.py`: base
PROVED via the old key arm, after FAIL because the carrier is unknown; a literal int-keyed holder is not
representable). Suggested follow-up route: declare it (`--soundness-report`, docs) or refuse int-keyed reads.
(2) A bare loop whose body mutates the root/target/a pyval local is no longer lowered (int fallback -> L3-tc):
coarser, fail-closed; population in root/pyref/mirror: 0 (byte-diff inert). (3) The `hstr_of` projection for an
`hval` startswith/endswith argument fires only where `_is_string_expr` already accepts the argument (the mirror's
`ctor_name`, symbol-typed `str` by its later `.items()` loop); elsewhere the call stays on its previous lowering.
