# Wall: for-loop TUPLE-UNPACK target lowering (the residual writer/collector frontier)

**Status:** OPEN — escalated by the self-tcb-reduction-driver after Phase 1 drained to
`no_cheap_remaining` at count 721 (session 736→721). This is the single dominant blocker across the
residual frontier: ≥6 `\trusted` stubs are stuck on it and nothing else.

## 1. The wall, precisely

A `for`-loop whose **target is a tuple** (`for a, b in <iterable>`) does NOT bind its unpack targets
in the emitted WhyML for several iterable shapes — the targets emit as UNBOUND symbols
(`unbound function or predicate symbol 'symtype'`), so the whole method fails to type-check/prove.

The emitter ALREADY lowers two tuple-unpack shapes (so this is an EXTENSION frontier, not a greenfield
capability — see `src/pycsl/module6_whyml/stmt_control_flow.py`):
- `_enumerate_over` / `_enumerate_seq_recv` (lines ~671, ~700): `for i, ch in enumerate(<seq-string
  LOCAL>)` → a dedicated dual-binding while-loop binding `i` (counter) and `ch` (`Seq.get s !idx`).
- `_classify_iterable` `.items()` twins (lines ~243-383): `for k, v in <hval self-field OR hval
  local>.items()` → over-approx binding on the certified hval/pydict theory (`_for_target_is_pyval`).

## 2. The uncovered sub-cases (measured with `--fun`, 2026-08-14)

| Stub | File | Iterable shape | First blocker (`--fun`) |
|------|------|----------------|-------------------------|
| `_find_abstract_val_insert_idx` | abstract_ops.py | `for i, line in enumerate(out)` where `out` is NOT a seq-string local (param/array) | targets `i`/`line` UNBOUND; also `line.strip()`/`.startswith((tuple))` string-facades |
| `_build_method_*_map` family | functions.py | direct `for nm, ty in params` over a **list-of-pairs** (no enumerate, no items) | dict-comp tuple-unpack targets UNBOUND |
| `_emit_union_arm_vc` | functions.py | `for var, symtype in symbol_table.items()` where `symbol_table` is **int-erased** to `map string (option int)` | targets UNBOUND **AND** value `symtype` is int-erased (value-model) + nested `vinfo["whyml_name"]` opaque facades |

Three DISTINCT extensions, of increasing risk:
- **(b) enumerate over a param/array string** — pure binding extension of `_enumerate_over` to a
  non-seq-local receiver. Element type is REAL (string). *Tractable.*
- **(c) direct pair-unpack over a seq-of-pairs** (`for nm, ty in params`) — a new dual-binding
  while-loop over `Seq.get params !idx` projected into `.0`/`.1`. Element types REAL if `params` is a
  faithful `seq (string, τ)`. *Tractable IF the pair element type is faithful (not int-erased).*
- **(a) items over an int-erased map** — the map VALUE `symtype` is erased to `option int`, so even
  with the binder, any real use of `symtype` as a type-string fails. This is a VALUE-MODEL erasure,
  not a binding gap. *Boundary-risk: needs the map to carry a faithful value type first.*

## 3. What L (the oracles) already says

- The binding machinery works for adjacent cases (enumerate-over-seq-local + items-over-hval both
  PROVE today) → the dual-binding while-loop pattern is sound and reusable.
- `_emit_union_arm_vc`'s blocker is NOT only binding: `symbol_table` int-erasure means the value is
  gone. Confirmed by the `unbound 'symtype'` + the `map string (option int)` type in the emitted mlw.
- Several of these ALSO carry orthogonal blockers (string-facades, nested-def closures) that would
  remain even if tuple-unpack were solved — so the wall break unblocks a stub ONLY where tuple-unpack
  is its SOLE blocker.

## 4. Make-or-break question (for the impl plan's spike)

**Can the existing dual-binding while-loop pattern be extended to (b) enumerate-over-param-array and
(c) direct seq-of-pairs unpack, with the unpack element types kept FAITHFUL (string / faithful pair),
proving termination + the bindings — WITHOUT a new axiom/ADT/cert and byte-inert on the corpus?**

- If the spike PROVES a hand-`.mlw` for a `for a,b in <seq-of-string-pairs>` dual-binding loop
  (faithful element projection + provable variant) → BUILD the (b)/(c) extensions, gated on the
  emitting-method sentinel; each unblocks its stub only if tuple-unpack is the sole blocker.
- If the spike cannot keep the pair element faithful (forced int-erasure like case (a)) → that
  sub-family is a CERTIFIED-BOUNDARY pending the heterogeneous-map faithful-value build (already
  noted in memory as review-gated); record it and stop.

## 5. Scope / non-goals

- IN: (b) enumerate-over-array, (c) seq-of-faithful-pairs unpack — the binding extensions.
- OUT (this cycle): (a) items-over-int-erased-map (value-model dependency), string-facade elimination
  (`.strip()`/`.startswith(tuple)`), nested-def closures — each its own wall.
- Ledger stays 3; contract shape `requires True/ensures True/assigns <tight>`; corpus byte-diff 0
  (gate every new emitter branch on `_uses_/_emitting_<method>`); drift stays 2.

---
## VERDICT (2026-08-15): CERTIFIED-BOUNDARY (compound) — binder PROVEN + banked, ZERO consumers
The pytuple-projection binder was BUILT + validated END-TO-END through the real emitter (probe
`count_eq_pairs(params: List[Tuple[str,str]])` → faithful `.field0/.field1` bindings + faithful
string compares (NOT int-hash) + arithmetic variant → Verification SUCCESS, no new axiom). But an
exhaustive AST census of all 721 trusted stubs' LIVE bodies found: 105 have tuple-unpack, ZERO
iterate a `List[Tuple[τ,τ]]`-typed array PARAM or list-of-record-literal LOCAL (the only shapes the
pytuple binder recognizes). Every consumer's iterable is `.items()` (dict→hval), `zip()` (irlist),
`enumerate()`, a `Set`, a module-level constant (already unrolled), or an opaque cross-call result
(e.g. `_maybe_emit_no_exception_assert`'s `triggers = triggers_for(op_key)` → `array string`, binder
never fires). Landing the binder standalone = unused-facade (Gate C reject) → REVERTED clean, count 721.
The binder is BANKED for the day a `List[Tuple]`-param consumer appears.

**NEXT actionable vein (different binder):** `.items()`-over-`Dict[str,str]` consumers. Review §5.2:
`Dict[str,str]` ALREADY lowers to `map string (option string)` today; the residual is an ITEMS-binder
over a NATIVE map (keys_get/values_get over-approx — the device already banked for hval items). This
is a SEPARATE build from the pytuple projection and must itself be measured for un-co-blocked consumers
before escalation (many `.items()` consumers also carry Dict[str,Any] int-erasure or nested facades).
