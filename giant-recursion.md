# giant-recursion.md — a plan to convert the three giants without growing the trusted count

**Targets.** `_handle_call_expr` (285 L), `_handle_subscript` (304 L), `_call_named_builtins` (399 L)
— the last trusted `_handle_*`/dispatch handlers, currently **3 `\trusted` markers**.

**Verdict up front.** The giants are *convertible* net-neutral-to-negative — but ONLY with the right
decomposition. My first attempt failed on the METHOD, not the difficulty: I isolated one **116-line
chunk** (`_call_special_shapes`) as a single trusted leaf without trying to convert it, then needed a
**second** leaf (`_handle_string_value_method`), landing at net **+1 marker**. That is an artifact of
**coarse** isolation. The fix is **fine-grained, bottom-up decomposition + convert each piece** —
because, with the recognizers already built this campaign, *most* sub-branches convert, and the
truly-irreducible content is the item-3 recursion leaves (`_expr_to_whyml`/`_stmts_to_whyml`), which
are **already trusted at the ceiling and are not new markers**.

---

## 1. The marker math (why method matters)

Decomposing a giant (1 marker) into a thin dispatcher + N sub-handlers, K of which stay trusted:

> **net markers = −1 + K**  (the giant's marker disappears; each irreducible sub-handler is +1)

- **K = 0** (everything convertible) → **−1** (a win).
- **K = 1** → **0** (neutral; big surface reduction).
- **K ≥ 2** → **positive** (worse — my coarse attempt).

So the entire game is **minimize K** — the count of sub-handlers that genuinely cannot type-check +
prove even with the recognizers. Coarse isolation maximizes K (each big chunk is 1 leaf); fine-grained
decomposition + conversion drives K toward 0.

**Corollary — calls to the recursion leaves are FREE.** `_expr_to_whyml`/`_stmts_to_whyml` are already
trusted `val`s (the Gödel/Löb ceiling, item 3). A sub-handler that *calls* them does not add a marker;
it converts as long as its own body type-checks. Likewise every abstract op (`findall_str`,
`ir_shared_vars`, `subscript_get`, `str_replace_op`) is a declared `val` — a branch that *emits* one
still converts; the op is not a trusted `\trusted`-stub method.

**So a branch is only irreducible (K+1) if its own body has a construct that can't type/prove** — a
hard reflection type-mismatch with no recognizer, a nested closure (all hoisted now), a
logic-vs-program crossing, or a value-faithful contract the ceiling forbids. That set is small.

---

## 2. What the campaign already built (the toolbox)

Every giant sub-branch draws on capabilities that now exist (committed, byte-diff 0, proven):

- **emit_ir reflection**: IR-node params → `emit_ir`; `_EMIT_IR_STR_ATTRS` (`.kind`/`.var`/`.op`/
  `.base`/…); node-LIST attrs (`.elts`/`.parts`/`.args` → `args_of`, incl. the SUBSCRIPT form
  `expr["args"]`); the emit_ir sub-node truthiness; `object_of`/`svalue_of`/`arg0_of` projections.
- **cross-file wiring**: `#@ requires_method <m>: (self, …) -> τ` synthesizes a correctly-typed
  pseudo-signature (params AND return, incl. `-> str` propagation) — kills the int-defaulted stub.
- **nested containers**: `Dict[str,Dict]` (nested-map), `Dict[str,List[T]]` (#15, → `map int (option
  (seq T))`), `Dict[str,Dict[str,ExprIR]]` (inner `emit_ir`), with the `.get`/subscript/membership +
  `_dv_missing_default` for `seq`/`map`/`emit_ir` empties.
- **seq↔array coercion**: `_coerce_dotted_args` bridges a `seq` arg (list-comp result) into a
  `List[_]` param via `materialize`/`materialize_str`; `str_join_seq`; bare-`ListComp`→`seq`;
  loop-var-over-a-seq-slice → `string`.
- **Optional/sentinel**: `""`-sentinel + truthiness convention for `Optional[str]` returns.
- **field declarations**: the ~30-field mixin declaration set (so `x in self._field` hashes).

**What's still missing (build on demand, per branch):** a `seq`-typed *return* surface (a helper that
returns a list-comp → `seq`, currently only `List[_]`→`array`); a couple more `_dv_store_value`/value-
type inferences for `emit_ir`-valued dict-locals; possibly a `Dict[str,Dict[str,str]]` inner-string
path (param_whyml_types). Each is a small, local recognizer — none is a new *feature*.

---

## 3. The strategy: bottom-up, fine-grained, convert-then-measure

> **⚠️ SUPERSEDED (2026-07-03).** §3–§5 below describe a *dispatcher-first* fine-grained conversion
> with the claim "K≈0, net −1." **The execution log (bottom of file) empirically disproved this**:
> even the easiest giant lands net **+2** dispatcher-first, because a giant is a dispatcher over a
> fan-out of helpers and converting it drags each not-yet-mirrored helper in as a new stub. §1 (marker
> math) and §2 (toolbox) remain valid; §6 (gates) remains valid. The correct strategy is **bottom-up
> over the helper DAG** — see the new **§8 (Helper-DAG inventory)** and the execution log. Read those
> two, not §3–§5.

**Do NOT** extract big chunks (`_call_special_shapes`) as trusted leaves. **DO**:

**S1 — Enumerate branches.** For each giant, list its top-level `if <guard>: return …` branches (call
≈ 26, subscript ≈ 23, builtins ≈ per-builtin). Each becomes a candidate sub-handler `_call_<shape>` /
`_sub_<kind>` returning `str` (`""` = fall-through, per the sentinel convention).

**S2 — Extract one branch → one small method (byte-diff 0).** Behaviour-preserving; the dispatcher
becomes `_r = self._<shape>(…); if _r: return _r`. Watch the side-effect ordering trap: the
`args = […]` lowering and any `_add_abstract_op` must keep their position (the boundary rule from the
R3 log — cut *before* the side-effecting `args = […]`).

**S3 — Try to CONVERT the extracted method** with the toolbox. Full proof, byte-diff 0. If it converts
→ it's a converted leaf (0 markers). If it leaks, apply the matching recognizer from §2; escalate per
the per-stub attempt budget.

**S4 — Only if a branch genuinely can't convert** (after the budget) does it stay `\trusted` — that's
a K-leaf. Record WHY (which irreducible construct).

**S5 — Consolidate the K-leaves.** The irreducible branches across the THREE giants overlap heavily
(they all bottom out at the same handful of reflection primitives). Merge shared irreducible logic
into ONE trusted helper reused by all three, so K is counted once, not per-giant. This is where a
net **negative** is won: 3 giant markers → converted dispatchers + M converted sub-handlers + **1
shared reflection-primitive leaf**.

**S6 — Measure after each giant.** The net is `−1 + K` per giant; keep K ≤ 1 or stop and re-plan.

---

## 4. Per-giant branch triage (from the structure dumps)

### `_handle_call_expr` (285 L) — CONVERT most, watch 2 spots
| Branch | Verdict | Note |
|--------|---------|------|
| `.to_dict()` identity, `.copy()` | **C** | returns the receiver emit_ir/map — pure |
| `.findall`, `.split`, `__str__`, `IRScanner.<pred>`, `ir.get` | **C** | emit a declared abstract op; args via `expr["args"]` (recognizer exists) |
| `len(...)`, `decode`, constructors, inductive/axiom preds, `struct.*` | **C** | formatting + declared ops |
| default-arg-fill (`formal_params`/`defaults`/`param_whyml_types`) | **C\*** | nested containers — recognizers built this campaign; needs the emit_ir-dict-local value-type inference finished |
| dotted / module-fn / user-fn dispatch (`_handle_dotted_call`, `_coerce_dotted_args`) | **C** | seq↔array coercion + `requires_method` for the facade wraps |
| `_handle_string_value_method` (`.replace`/`.lower`/`.upper`/`.strip`) | **C** | faithful-string ops are modelled (`str_replace_op` …) — CONVERT it, don't leaf it |
| `_call_named_builtins` call | delegates to giant 3 | |

**Expected K for call ≈ 0–1** (the residual is at most the `ir.get`-shared_vars `sharedvar`-typed
reflection, if that specific type resists).

### `_handle_subscript` (304 L, 47 ifs) — per-receiver-kind
Body-dict get, self-field-dict get (incl. nested-map), array index, string-split `[i]`,
tuple-destructure, `emit_ir` projection subscript (`arr["value"]["name"]`), opaque fallback. Almost
all have recognizers (the emit_ir subscript projections, the nested-map/#15 subscript, str_split_elem).
**Expected K ≈ 0–1** (the opaque `subscript_get` fallback branch, which is *already* just emitting a
declared op — likely convertible).

### `_call_named_builtins` (399 L) — per-builtin
`chr`/`ord`/`len`/`str`/`int`/`abs`/`min`/`max`/`sorted`/… each maps to a specific op or fold. These
are the MOST convertible (fixed-arity, faithful ops). The size is breadth, not depth.
**Expected K ≈ 0.** This is the biggest *surface* win and likely a clean *count* win too.

---

## 5. Sequencing

1. **`_call_named_builtins` first** (399 L, K≈0) — biggest surface, cleanest conversion, no dependants;
   proves the fine-grained method on the largest body and likely lands a **−1**.
2. **`_handle_subscript`** — per-receiver decomposition; recognizers mostly exist.
3. **`_handle_call_expr` last** — it *calls* the other two, so convert them first; finish the emit_ir-
   dict-local value-type inference (§2 "still missing") before its default-fill branch.
4. **S5 consolidation pass** — after all three, merge any shared K-leaves into one reflection-primitive
   helper; re-measure.

---

## 6. Gates (unchanged, per stub)

Per extracted/converted branch: **byte-diff 0** across the 627-corpus (each extraction is behaviour-
preserving; each recognizer is `@mutable_state`-gated) · **verbatim mirror-sync** · **full Why3 proof**
(NOT `--no-proof` — the nested-fn/logic false-positive lesson) · `\trusted` `wc -l` **measured** (must
end ≤ its start per giant). Abstract-op registration ORDER preserved (byte-diff catches drift).

---

## 7. The metric caveat (decide once)

If, after honest fine-grained conversion, a giant still lands **K ≥ 2** (net positive markers), that is
a genuine **surface-vs-marker** choice: converting it shrinks trusted *code* (285 L → ~100 L) but grows
the *marker* count. Default: **keep K ≤ 1** (convert only when net ≤ 0). Override only with an explicit
decision to optimize trusted-surface over marker-count — and record it, because it moves the campaign's
headline number the wrong way.

**Expected outcome if executed:** `_call_named_builtins` −1, `_handle_subscript` −1, `_handle_call_expr`
0 to −1 → the giants go from 3 markers to **~0–1**, with ~1000 L of trusted code converted, and the
last `_handle_*` handlers off the trusted core — the natural end of the self-tcb-reduction campaign.

---

## EXECUTION LOG — `_call_named_builtins` attempt (2026-07-03): the K≈0 prediction was wrong

Executed §5 step 1 on the "easiest" giant. Got a long way, and learned the plan's optimism was
misplaced in one specific, measurable way.

**What worked (as predicted):**
- The `Optional[str]`-return desugar: `-> str` + `return ""` sentinel + caller `if named:` truthiness.
- Isolating the ONE genuinely-hard branch — the getattr-field `.get` rewrite, which *mutates* the IR
  (`expr = dict(expr); expr["func"]=…; expr.pop("receiver")`) and so reassigns the `expr`/`func_name`
  params (dropping them from the signature). Extracted to a trusted leaf `_call_dict_get_shape`. **+1.**

**The tool gap the plan missed — a trusted stub CALLED BY VERIFIED CODE.** `_call_dict_get_shape` is the
first trusted stub ever *called from a converted body*. That exposed a latent disagreement: the verified
`let` signature lowered a `List[str]` param to `array int`, while the abstract-`val` path
(`_build_method_param_types_map`) lowered it to `array string`. A `self.m(args)` call where one side is
verified and the other abstract then fails to type-check. **Diagnosed and fixed** (`_param_type_str` now
applies the same `@mutable_state`-gated `List[str]`→`array string` refinement) — a real, reusable fix,
but a *prerequisite* the plan didn't list. **This will recur for every giant** (they all call helpers).

**Why K is NOT ≈0 — the helper-stub cascade.** The plan's "calls to recursion leaves are FREE" corollary
is true, but the giants mostly call **helper methods**, not the `_expr_to_whyml` recursion leaf. Each
helper must be a mirror stub with a correct signature. `_call_named_builtins` calls **16** helpers; 14 are
already in-mirror (need only `expr: Dict`→`"ExprIR"` signature touch-ups, byte-diff 0), but **2 were
missing** (`_call_returns_seq_string`, `_lower_getattr`) → **+2 new stub markers**. Plus the getattr leaf
(**+1**). So converting `_call_named_builtins` is **net +2**, not the predicted −1 — before counting the
leaks still ahead.

**Revised verdict (empirical, supersedes §7's optimism).** Even the easiest giant is **net-marker-positive**
to convert, because a giant is a *dispatcher over a fan-out of helpers*, and pulling its body into the
verified set drags each not-yet-mirrored helper in as a new leaf. `K` is not the count of *irreducible*
branches — it's the count of **not-yet-converted transitive helper callees**, which for a top-level
dispatcher is large. The giants are the LAST handlers precisely because they sit atop the helper DAG:
converting them first maximizes K. **If the giants are ever converted, it must be bottom-up over the whole
helper DAG** (convert every leaf helper first, so by the time the dispatcher is done its callees are all
already-converted = free), NOT dispatcher-first. That is a much larger campaign than one giant.

**Landed from this attempt:** nothing to the mirror (reverted to clean 1273). The one reusable artifact —
the `_param_type_str` `List[str]`→`array string` agreement fix — is documented here as the first
prerequisite for a future bottom-up DAG pass, not landed orphaned.

---

## 8. Helper-DAG inventory (2026-07-03) — the actual work behind the giants

Built by transitive `self._x(...)` call-graph closure over the emitter (`src/pycsl/module6_whyml/*.py`
+ `Module6_WhyMLTranspiler.py`), cross-referenced against mirror status. Reproduce with the analysis
script pattern in this session (parse defs → closure per giant → STUB/CONVERTED/MISSING per callee).

### The scale — "the giants" ≡ a 77-helper closure, not 3 methods
| Giant | transitive emitter-helpers | STUB | MISSING | CONVERTED |
|-------|---------------------------:|-----:|--------:|----------:|
| `_handle_call_expr`      | 73 | 46 | 23 | 4 |
| `_handle_subscript`      | 35 | 17 | 14 | 4 |
| `_call_named_builtins`   | 49 | 28 | 17 | 4 |
| **UNION (distinct)**     | **77** | **49** | **24** | **4** |

Subscript's closure is almost a subset of call's; the three share heavily. Converting all three ≡
converting/adding **80 methods** (77 helpers + 3 dispatchers).

### The marker arithmetic (why bottom-up flips the sign)
- **49 STUB helpers** are *existing* `\trusted` markers → converting each is **−1**. (These are ordinary
  self-tcb campaign work; the giants just sit atop them.)
- **24 MISSING helpers** aren't in the mirror → to convert any caller they must be added: **±0** if
  convertible (added as a verified body, no marker), **+1** if irreducible (added as a stub).
- **3 dispatchers** → **−3** once their callees are all in-mirror.
- **Best case** (all stubs + all missing convert): ≈ **−52**. **Worst case** (all 24 missing irreducible):
  −49 −3 +24 = **−28**. **Either way NET-NEGATIVE** — the dispatcher-first +2 was an artifact of stubbing
  the missing helpers instead of converting them.

**So bottom-up over the DAG is a genuine count win** — but it is a large campaign (≈80 methods, a real
fraction of the remaining 1273), not "one giant." The giants are the capstone of finishing most of the
expression-emitter mirror.

### Bottom-up start set — the 27 DAG leaves (callees all CONVERTED/EXTERNAL)
Convert these FIRST; each unblocks its parents.

**18 STUB leaves — immediate −1 each (do these first, lowest risk):**
`_add_abstract_op` · `_array_coerce_arg` · `_coerce_str_arg` · `_coerce_to_int` · `_dv_missing_default` ·
`_field_label` · `_field_type_of` · `_handle_sum_call` · `_inductive_sig_whyml` · `_is_null_byte_lit` ·
`_maybe_emit_no_exception_assert` · `_pop_quant_binder` · `_push_quant_binder` · `_quant_binder_whyml` ·
`_resolve_dotted_signature` · `_strip_outer_parens` · `_symtype_to_whyml` · `_tag_of_type`

**9 MISSING leaves — add as verified bodies (±0 if convertible; this is the go/no-go probe):**
`_alias_self_field` · `_getattr_self_field` · `_is_seq_arg` · `_iter_elem_class` · `_self_field_dict_nu` ·
`_str_method_recv_and_tail` · `_todict_recv_node_ir` · `_todict_routed_ir` ·
`_wrap_unannotated_call_with_strict_assert`

### The 24 MISSING helpers (the risk set — each must convert at ±0 or cost +1)
leaf-now: `_alias_self_field` · `_getattr_self_field` · `_is_seq_arg` · `_iter_elem_class` ·
`_self_field_dict_nu` · `_str_method_recv_and_tail` · `_todict_recv_node_ir` · `_todict_routed_ir` ·
`_wrap_unannotated_call_with_strict_assert`
non-leaf: `_call_returns_seq_string` · `_emit_ir_args_recv_ir` · `_handle_string_value_method` ·
`_is_literal_string_join` · `_is_str_value_method` · `_join_arg_elem_is_string` · `_lower_dict_get_call` ·
`_lower_getattr` · `_lower_irnode_construction` · `_render_callee_condition` · `_seq_snapshot_op` ·
`_split_call_recv_sep` · `_todict_emit_ir_projection` · `_wrap_call_with_callee_raises_assert` ·
`_wrap_with_no_exception_assert`
(4 of these live in `Module6_WhyMLTranspiler.py` / `statements.py` — cross-file, need `#@ requires_method`
wiring or their own mirror stubs.)

### Prerequisites before ANY of the above (from the execution log)
- **P1** — land `_param_type_str`'s `@mutable_state`-gated `List[str]`→`array string` refinement (the
  trusted-stub-called-by-verified-code agreement). Gates every helper that passes a `List[str]`.
- **P2** — the IR-mutation isolate recipe (`expr = dict(expr)…` → trusted leaf), applied per-helper.

### Go/No-Go — the next concrete step
Probe the **9 MISSING leaves**: can they be added as *verified* bodies (±0), or are they irreducible
(+1)? That verdict decides whether the whole bottom-up campaign nets negative. Start the probe with the
smallest — `_getattr_self_field`, `_self_field_dict_nu`, `_str_method_recv_and_tail`, `_todict_recv_node_ir`
(all leaf, all read-only reflection) — plus land P1. If they convert, proceed up the DAG via the 18 STUB
leaves; if they don't, the giants stay net-positive and 1273 is the endpoint.
