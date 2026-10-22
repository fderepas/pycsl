# OPEN ROUTE #297 — THE COMPILE-TIME COLLECTION-LITERAL FOLD IGNORES NON-LITERAL KEYS/ELEMENTS AND STARRED ELEMENTS
**Status: OPEN (gen #37, 2026-10-22), Severity 1.** Red-team round 9; driver-reproduced at d1389605 (7 probes rc=0; CPython violates each).
Witnesses `witnesses-r297/`. The emitter tracks literal-bound locals in `_known_collection_elements` / `_known_collection_sizes`
(src/pycsl/module6_whyml/types.py) and replaces `d[0]`, `t[1]`, `len(s)` by a constant from the literal's source text, ignoring the
correctly built WhyML map/array. (F1) DictLit: `elem_map` keeps Number/Bool-keyed entries and SKIPS non-literal keys, so
`{0: 1, k: 2}[0]` folds to 1 though k == 0 at runtime gives 2 (y01; also local k, `2-1`, `+1`, `-0`, `len("")`, `n-1`, unannotated)
— route #61's NOT-YET-MEASURED element-fold residue. (F2) SetLit: a non-literal element is a distinct `("id", id(e))`, so
`len({"x", a}) == 2` proves (a == "x" gives 1; z12, z11 with `requires a == b`). (F3) Starred: `(*ys, 5)[1] == 5`, `len((*ys, 5)) == 2`,
`len({*ys}) == 1` prove (z04, z07, z10). Repair: drop the element/size fold whenever ANY key/element is non-literal or Starred
(refuse-not-guess, route #61's own principle), census every fold consumer (dict/set/list/tuple, len, subscript, in, iteration).
