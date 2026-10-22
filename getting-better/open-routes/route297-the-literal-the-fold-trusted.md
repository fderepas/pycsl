# OPEN ROUTE #297 — THE COMPILE-TIME COLLECTION-LITERAL FOLD IGNORES NON-LITERAL KEYS/ELEMENTS AND STARRED ELEMENTS
**Status: REPAIRED (gen #37, 2026-10-22; opened the same day), Severity 1.** Red-team round 9; driver-reproduced at d1389605 (7 probes rc=0; CPython violates each).
Witnesses `witnesses-r297/`. The emitter tracks literal-bound locals in `_known_collection_elements` / `_known_collection_sizes`
(src/pycsl/module6_whyml/types.py) and replaces `d[0]`, `t[1]`, `len(s)` by a constant from the literal's source text, ignoring the
correctly built WhyML map/array. (F1) DictLit: `elem_map` keeps Number/Bool-keyed entries and SKIPS non-literal keys, so
`{0: 1, k: 2}[0]` folds to 1 though k == 0 at runtime gives 2 (y01; also local k, `2-1`, `+1`, `-0`, `len("")`, `n-1`, unannotated)
— route #61's NOT-YET-MEASURED element-fold residue. (F2) SetLit: a non-literal element is a distinct `("id", id(e))`, so
`len({"x", a}) == 2` proves (a == "x" gives 1; z12, z11 with `requires a == b`). (F3) Starred: `(*ys, 5)[1] == 5`, `len((*ys, 5)) == 2`,
`len({*ys}) == 1` prove (z04, z07, z10). Repair: drop the element/size fold whenever ANY key/element is non-literal or Starred
(refuse-not-guess, route #61's own principle), census every fold consumer (dict/set/list/tuple, len, subscript, in, iteration).

## REPAIR (2026-10-22, r297 executor off 2850cbbf; commit c0a9eca0 + docs)
Probe table (`src/pycsl/pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`; extra probes under the r297
scratchpad `probes/`):

| shape | 2850cbbf | after |
|---|---|---|
| dict literal, non-literal key equal at runtime: `-0` (d13/3510), `2 - 1` (x01/3511), `+1` (x02/3512), local `k = 0` (x04/3513), unannotated (x06/3514), param `k` (y01/3515), read via local (y03/3516), `len("")` (z05/3518), `n - 1` (z06/3519) | PROVED | FAIL (goal unproven) |
| `t = (*ys, 5); t[1] == 5` (z04/3517), `len(t) == 2` (z07/3520), `len({*ys}) == 1` (z10/3521) | PROVED | FAIL |
| set literal, non-literal element: `requires a == b; len({a, b}) == 2` (z11/3522), `len({"x", a}) == 2` (z12/3523) | PROVED | FAIL |
| INLINE `len(<literal>)` (census find): `len({1, 1}) == 2` (3524), `len({0: 1, k: 2}) == 2` (3525), `len((*ys, 5)) == 2` (3526), `len({a, b})`, `len({1: 2, 1: 3}) == 2`, `len([*ys, 5]) == 2` (probes p02/p03/p06) | PROVED | FAIL |
| float index truncated onto an int slot (census find): `a = [4, 5]; a[1.0] == 5` (3527; CPython TypeError), `{1: 4}[1.5] == 4` (p20; KeyError) | PROVED | FAIL |
| rebinding after a refused literal: `if c: t = (*ys, 5) else: t = (1, 2); t[1] == 2` and the set/dict twins (p23-p25) | FAIL | FAIL (the refusal blacklists the name; without it the first cut PROVED these) |
| controls 3528 (all-literal dict/tuple/set local + inline, distinct-counted; list/tuple with a plain non-literal element keeps size + literal positions) | FAIL (inline `len({1, 2, 1})` / `len({1: 2, True: 3})` were syntactic) | PASS |
| true twin 3529 (`requires k == 0; {0: 1, k: 2}[0] == 2`, from the map) | FAIL | PASS |
| `in` / iteration / `sum` / truthiness over a Starred or non-literal-key literal (p11, p12, p14-p16) | FAIL | FAIL |

Rules (inline, no new def/field, no axiom — ledger 3; the three edited methods `_track_collection_metadata`,
`_handle_len_call`, `_handle_subscript` are `\trusted` in the mirror):
- `_track_collection_metadata` (the ONLY producer of `_known_collection_sizes` / `_known_collection_elements`; the
  only other writer is route #60's whitelisted store increment, which can only grow a registered entry): a
  list/tuple/set literal with ANY `Starred` element, a set literal with any non-literal element, a dict literal with
  any non-literal key (route #61 already withheld the SIZE; now the element map too) or a non-integral float key
  registers NOTHING and adds the name to `_rebound_collections`, so a later literal binding (another arm) cannot
  register either. A plain non-literal list/tuple element stays foldable (size and the other positions are exact).
- `_handle_len_call` inline arms: Tuple/ArrayLit fold only with no Starred; SetLit/DictLit only when every
  element/key is a literal, counted DISTINCT under Python equality (Bool = 1/0, `1 == 1.0`) — this also fixes the
  inline twin of route #54 (`len({1: 2, 1: 3})`), which only the local had received.
- `_handle_subscript` element fold: index must be an `int` Number (not float, not bool).
CENSUS of consumers (all read the two maps, so the producer change closes them): truthiness (`expressions.py`
`_r31_sizes`), `len` (Var arm), `sum`, the indexed read, the all/any oracle decline and the route #159 bounds
`length 0` (size 0 only — no refused literal can have syntactic size 0 that matters, `[*ys]` was size 1 and is now
unregistered), the statement-side store bounds and route #60 increment. `in` and `for` never consulted the fold
(probes p14-p16 fail at base and after). No other literal-text fold of `len`/subscript exists (`sum` inline folds
only all-Number list literals — exact).
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (1913 base / 1933 candidate, 20 new sources), pyref 0/0/0
(2186/2186), mirror 0/0/0 (53/53). No mover: no M1 re-proof and no mirror proof OWED. The stale "stated residue"
paragraph in `docs/pycsl-translational-reference.md` §T.5.12 (non-constant dict key takes the syntactic count —
false since route #61) is replaced by the rule above.
Gates (logs under the r297 scratchpad): 14 route witnesses rc=0 -> rc=1; corpus 3510-3527 rc=1 after (base rc=0 for
the shapes they carry), 3528/3529 rc=0 after (rc=1 base); byte-diff-sweep base/after rc=0; byte-diff-compare root
rc=0, pyref rc=0; mirror-emit-sweep base/after rc=0, compare `--min-files 50` rc=0; check-self-annotate-sync.sh
rc=0 (925 verbatim); self-annotate-mirror-check.sh rc=0 (53); run-soundness-planes.sh fast rc=0 (61 green);
--slow: see README entry.
Residuals: (1) PRE-EXISTING, not introduced here — the rebinding blacklist only fires when the FIRST binding
registered or was refused by this function; a first binding that is not a literal at all (`t = g()`) followed by a
literal binding in another arm is outside this route (unmeasured; worth a probe). (2) A dict index `d[1.0]` /
`d[True]` no longer folds (completeness only; the map answers). (3) Witness probes p02/p03/p06/p20/p23-p25 live in
the scratchpad only (corpus range 3510-3529 exhausted).
