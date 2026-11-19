# OPEN ROUTE #321 — Counter / OrderedDict / defaultdict MODEL: seed keyed on SOURCE TEXT, keyword seeds dropped, factory ignored, read does not insert
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day), Severity 1.** Red-team round 18 (stdlib/builtin model); driver-reproduced on main 3b07a838 (rc=0; CPython violates).
Witnesses `witnesses-r321/`: (a) `pycsl_seeded_map_%d % stable_hash(repr(seed))` (expressions.py ~11825): `Counter(xs); xs = [2]; Counter(xs)` share
one constant -> `c1[1] != c2[1]` decided False (d09, d12; across a dict-param mutation d13) — the README's "seeded-map constant (L3-tc-closed)"
residual is NOT closed once annotated `c: Dict[int,int] = Counter(..)`; (b) keyword seeds dropped: `Counter(a=5)`, `OrderedDict(a=5)`,
`defaultdict(int, a=5)` -> empty map, `d["a"] == 0` proves (n03, n04, n06); (c) defaultdict factory ignored, missing-key default hard-wired 0:
`defaultdict(lambda: 7)[5] == 0` (j05), `defaultdict(str)[5] == 0` (j06), `d[1] = d[1] + 4; return d[1] - 4` proves 0 (j08); (d) a defaultdict read
does not insert the key: `x = d[5]; 5 in d` proves False (j03; SEV-2).
Repair: seeded maps must be keyed on the seed's VALUE (evaluate the seed; model Counter(xs) as a function of the seed's contents, or refuse a
non-literal seed); refuse keyword seeds (as plain dict(a=..) is); model only `defaultdict(int)` (factory 0) or refuse other factories; a
defaultdict subscript read must insert (or refuse reads of defaultdicts whose membership is later observed).

## REPAIR (2026-10-23, r321 executor, detached off 67edf13c; commits 9f153cc6, 40e2c287 + docs)
Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`):

| shape | 67edf13c | after |
|---|---|---|
| `Counter(xs)` around `xs = [2]`, `c1[1] != c2[1]` decided False (d09 / 4150) | PROVED | REFUSED (non-literal seed) |
| `defaultdict(int, d)` around `d = {1: 6}` (d12 / 4151) | PROVED | REFUSED |
| `OrderedDict(d)` around `d[1] = 9`, `d` a param (d13 / 4152) | PROVED | REFUSED |
| `x = d[5]; 5 in d` decided False (j03 / 4153) | PROVED | REFUSED (unfused read + observation) |
| `defaultdict(lambda: 7)[5] == 0` (j05 / 4154), `defaultdict(str)` (j06 / 4155), `lambda: 3` bound (j08 / 4156) | PROVED | REFUSED (factory) |
| `defaultdict(int, a=5)` / `Counter(a=5)` / `OrderedDict(a=5)`, `['a'] == 0` (n03/n04/n06 / 4157-4159) | PROVED | REFUSED (keyword) |
| NEW: `e = d; x = e[5]; 5 in d` decided False (4160) | PROVED | REFUSED (alias) |
| NEW: `d[5] = d[5] + len(d)` (4161; base fails L3-tc) | FAIL | REFUSED |
| NEW: `Counter([(1, 1)])[1] == OrderedDict([(1, 1)])[1]` (4162; shared constant) | PROVED | FAIL (Counter keyed apart) |
| NEW: `defaultdict()` (no factory, CPython KeyError) `d[5] == 0` (4163) | PROVED | REFUSED |
| NEW: `def f(k, d = defaultdict(lambda: 0))` read-then-`in` via `f(5)` (4175; base FAIL) | FAIL | REFUSED (arm outside a scanned body) |
| controls: fused reads + `in` (4170), equal literal seeds (4171), unobserved read (4172), `lambda: 0` (4173); corpus 0498, 1079 | PASS (4170 base L3-tc FAIL) | PASS |
| `collections.defaultdict(lambda: 7)` dotted (probe w04), module-level `D = defaultdict(lambda: 7)` (probe w06) | FAIL | FAIL (not reached by this arm) |

Rules (inline, no new def/field, ledger 3, no axiom; the two edited live methods have `\trusted` mirror twins):
- seeded-map arm (`_call_named_builtins`): REFUSE a keyword or starred argument and an arity CPython rejects; REFUSE a
  non-LITERAL seed (literal = Number/String/Bool/None, negated Number, ArrayLit/Tuple/SetLit/DictLit of literals — a
  literal's IR repr is its value, so equal constants now mean equal maps); `Counter` seeds hashed as `("Counter", seed)`
  (a Counter counts the pairs an OrderedDict unpacks); `defaultdict` factory only `int` (not user-shadowed) or `lambda: 0`;
  a `defaultdict` is lowered only when `_r249_scope["r321_dd"]` says the current body was scanned.
- scan (`_reset_function_state`, before route #275's prescan): every `defaultdict(...)` Call in a body must be the value
  of a plain local `Assign` to `D` with either (A) every `D` occurrence a subscript base, or (B) only non-aliasing
  observations (`in`/`not in` right operand, `len(D)`, `del D[k]`, `D.get/keys/values/items`) and every read FUSED into
  `D[k] = ...` with the same Number/String/Var index and no other mention of `D` / walrus in the value; else REFUSED.
  A user `defaultdict` (route #75) is not scanned. The result rides on the existing per-function `_r249_scope` dict.
- CENSUS before the rule: corpus seeded constructions = 1076/1077/1078 only (literal seeds, expected FAIL, unchanged
  verdicts); factory forms 0498/1079 (`defaultdict(int)`, subscript-only -> mode A); ~20 `Counter()` (unseeded, untouched);
  mirror/live `defaultdict(list)` in `frontend/ir_resolve.py` is not a mirror file.
Blast radius: corpus root 1 MOVED (1076: the seeded constant renamed `pycsl_seeded_map_1841076074` ->
`_1949712395` by the Counter tag; re-proved: FAIL -> FAIL, same L3-tc failure as base, expected FAIL), 0 GONE,
0 APPEARED (2156 base / 2165 candidate .mlw, 26 new sources); pyref 0/0/0 (2186/2186). Mirror 2 MOVED
(`module6_whyml__expressions`, `Module6_WhyMLTranspiler`: exactly `raises { PyCSLIRError -> true }` on the
`_call_named_builtins` / `_iter_len_expr` vals, added for the raises-honesty ratchet); both L3-tc OK; neither val has a
call site in any mirror body, so no VC changes — whole-file proofs OWED for form:
`HEAVY_LOW=1 heavy.sh .venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/module6_whyml/expressions.py --import-path src/pycsl`
and the same for `src/self-annotate/src/Module6_WhyMLTranspiler.py`.
Gates: see route #323's REPAIR (shared run).
Residuals: the scan is per-function and syntactic (closures over a defaultdict local are lifted out of the body and
not seen — none in the corpus; global/attribute defaultdicts are refused or never reach the arm); `collections.<X>(..)`
dotted spellings are not this arm's (they fall to the generic opaque path and fail L3-tc today — no proof);
`OrderedDict` order and `Counter` arithmetic remain unmodelled (opaque).
