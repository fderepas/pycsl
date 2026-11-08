# B-comp composition wall — TypedDict-route wall map (2026-07-10): NOT research-grade, ~5 bounded features

**Major finding (verified).** The composition wall (`_build_soundness_report` / B-comp — the value-model-wall
report's canonical hard method) is **NOT research-grade via the TypedDict route.** Monomorphizing each dict to
a native WhyML record UP FRONT sidesteps the `pyval` decoder synthesis entirely, and B-comp decomposes into an
incremental sequence of **~5 BOUNDED recognizer/type-plumbing features** — the same family as the shipped
G1/G2 / WL-04b / compound-const-map work. The variable-key map-fold (`counts[bucket]+=1`) the brief flagged is
ALREADY handled (`map string (option int)` + `map_update_some`).

## The ordered wall map (statement → blocker → class), verified
- **Already handled (not walls):** variable-key `counts[bucket]+=1`; scalar record `.get` (G1); string-field
  `str_eq_op` (G2); option-of-record (0891); `List[dataclass]` attribute access `a[i].field` (WL-04b);
  set-algebra `& -`, `sorted`, the pyval-native `_collect_calls` (S-dec 20/20).
- **WALL 1 (stmt 1/5) — `List[<record>]` field + element access. BOUNDED.** VERIFIED: `IrData.functions:
  List[FuncNode]` emits `{ functions: array int }` — element type dropped to int (funcnode record IS emitted).
  WL-04b's `array <record>` fires only for attribute `a[i].field` on a `List[dataclass]` PARAM, not a
  `List[TypedDict]` FIELD, subscript `a[i]["k"]`, or a `.get`-bound local. Fix = extend WL-04b to TypedDict
  fields + route dict-style element access to the field read + propagate the `.get` result type.
- **WALL 2 (stmt 2) — set-comprehension over List[record]. BOUNDED-but-SYNTHESIS (heaviest, zero infra).**
  VERIFIED: `{x for x in a if x>0}` → one opaque `val set_comp (x:int):int`. No faithful set-comprehension
  lowering exists. Fix = generate a recursive fold (iterate array → filter predicate → project str → `set_add`
  into `map string bool`) — the `build_trusted` the S-dec target hand-wrote; the `map string bool` A-set target
  MODEL exists + proves, just isn't WIRED to comprehension lowering. A comprehension→fold synthesis pattern
  (well-understood), NOT an open research problem.
- **WALL 3 (stmt 6) — nested `.get(...).get(...)` + `bool()`. BOUNDED.** G1 fires on a bare record var, not a
  `.get`-RESULT receiver. Fix = compose G1 on a `.get`-result of static record type + faithful `bool()` truthiness.
- **WALL 4 (stmt 9) — list-of-record append/return. BOUNDED (minor).** `vcs=[]; vcs.append(...); return vcs` →
  `seq vcentry` works; only the `materialize` return-cast stub is hardcoded `seq int -> array int`. Fix =
  specialize its element type.
- **WALL 5 (stmt 10) — nested-heterogeneous record return. BOUNDED.** A TypedDict return with a map/list-typed
  field (`summary: Dict[str,int]`, `vcs: List[VcEntry]`) fails construction (T9 "missing key" false positive on
  compound-typed fields). Fix = extend the TypedDict-construction recognizer to compound field types.

## Verdict + build order
**B-comp is reachable via ~5 bounded features (build order): WALL 1 → WALL 3 → WALL 4 → WALL 5 → WALL 2**
(WALL 2 heaviest, measure-first, but depends on WALL 1 for `funcs` to be a list-of-record to fold). Each is a
recognizer + Why3-stdlib model, byte-diff-gated (TypedDict annotations are corpus-inert). This is an
ALL-OR-NOTHING build for B-comp (a facade until all land + B-comp converts) — do NOT land one wall alone
(no-unused-facade). But it converts B-comp (a real −1) AND templates to the composition-wall class
(the `_build_method_*_map` family, the walker methods). The pyval-decoder route (09-2223 M2) stays research-grade;
the TypedDict route does NOT.
