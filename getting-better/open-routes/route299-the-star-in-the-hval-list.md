# OPEN ROUTE #299 — A STARRED ELEMENT IN A LIST LITERAL STORED AS AN hval BECOMES ONE ELEMENT
**Status: REPAIRED (gen #37, 2026-10-22; opened the same day), Severity 1.** Red-team round 10; driver-reproduced at 2cef1801 (4 probes rc=0; CPython violates).
Witnesses `witnesses-r299/`: `{"a": [*range(2), 3]}` gives `len(d.get("a")) == 2` (CPython 3, b10); `bool([*range(0)])` true (m01);
`"q" in [*"q"]` false (m02); `[*(...), {...}]` through the ch30 `hval_to_seq` bridge counts 2 (CPython 3, g01). `_pyval_wrap`
(src/pycsl/module6_whyml/expressions.py ~1320) wraps each ArrayLit element as one HCons, so a Starred element becomes a single
`HInt <...>`. #297 fixed only the types.py fold. Repair: a list/tuple/set/dict literal with any Starred (or **) element must not be
wrapped element-wise (opaque/uninterpreted hval or refuse); census every literal->hval wrapping path.

## REPAIR (2026-10-22, r299/r300 executor off f11bba0e; commits 56175045 + 8ee6ee54 + route docs)
Probe table (`src/pycsl/pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`):

| shape | f11bba0e | after |
|---|---|---|
| route witnesses b10, g01, m01, m02 | rc=0 PROVED | rc=1 (Timeout / Unknown) |
| 3570 `{"a": [*range(2), 3]}`, `len(d.get("a")) == 2` (CPython 3) | PROVED | FAIL |
| 3571 `bool([*range(0)])` hval truthy (CPython False) | PROVED | FAIL |
| 3572 `"q" in [*"q"]` nested hval false (CPython True) | PROVED | FAIL |
| 3573 starred record list through the ch30 `hval_to_seq` bridge counts 2 (CPython 3) | PROVED | FAIL |
| 3574 `{**m, "b": 1}` as an hval, `"k" in` it false (CPython True) | FAIL (L3-tc: the `**` key lowered as a `None` key) | FAIL (well-typed, goal unproven) |
| 3575 CONTROLS: plain hval list `len == 3`, plain `in`, `isinstance(<starred list>, list)` | PASS | PASS |
| census: `{**m, 1: 2}` / `{**m, "a": 2}` top-level (int map and PyVal map), `Dict[int, List[int]] = {0: [*ys, 5]}` | FAIL (L3-tc) | FAIL (L3-tc, unchanged) |

Rule (inline in `_pyval_wrap`, not mirrored; no new def/field, no axiom — ledger 3): a list literal with ANY
`Starred` element, or a dict literal with ANY `**` entry (key IR `None`), lowers to an unconstrained carrier of
the right constructor, `(HArr (any hval_list))` / `(HMap (any hpairs))` — `isinstance(x, list|dict)` stays decided,
length / truthiness / membership / the `hval_to_seq` bridge are unknown; a fresh `any` per evaluation; in a spec
(no `any`) the literal is refused (`PyCSLSemanticError`). Nested literals recurse, so `[[*ys]]` is
`HArr (HCons (HArr (any hval_list)) HNil)`.
CENSUS of literal->hval wrapping paths: every one goes through `_pyval_wrap` — `_build_dict_literal_map` (ν =
hval), `_build_pyval_inner_map` (`Dict[str, Dict[str, PyVal]]`), the `PyVal`-argument wrap in statements.py
(~3595/3608, call arguments into `hval_to_seq` / `hval_to_map` callees), the `.get(k, D)` default (four sites in
expressions.py), the `or`-default. Tuple / set literals (starred or not) were already the erased `HInt (any int)`
carrier (every test on it opaque). A `**` entry OUTSIDE the hval model (int-keyed / str-keyed maps) and a starred
list inside a non-hval dict value lower ill-typed (L3-tc refusal, fail-closed) at base and after.
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (1963 base / 1978 candidate, 15 new sources), pyref
0/0/0 (2186/2186), mirror 0/0/0 (53/53). No mover: no M1 re-proof and no mirror proof OWED.
Gates (logs under the r299 executor scratchpad): byte-diff-sweep base/after rc=0; byte-diff-compare root rc=0,
pyref rc=0; mirror-emit-sweep base/after rc=0, compare `--min-files 50` rc=0; check-self-annotate-sync.sh rc=0
(925 verbatim); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast rc=0 (61 green); `--slow` rc=0, all 84 green.
Residuals: (1) the carrier is opaque, so a TRUE claim about a starred hval list (its length) no longer proves
(completeness only). (2) Census find, not this route: a starred assignment TARGET `[*h, t] = e` and a nested
`TupleUnpack` target `(u, (v1, v2)) = ...` are DROPPED by the front-end (IR keeps `TupleUnpack targets ["u"]`
only; the starred form emits nothing). MEASURED: `t = 0; [*h, t] = e` under `requires len(e) == 1` PROVES
`\result == 0` (rc=0; CPython g([5]) == 5) — a NEW suspected false proof, outside this route, handed to the
driver (probe `u1.py` in the r299 executor scratchpad `probes/`); the nested form (`u2.py`) fails L3-tc (closed).
