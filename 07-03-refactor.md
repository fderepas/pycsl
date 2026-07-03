# 07-03-refactor.md — Refactoring `src/pycsl` for provability

**Author:** Claude (after ~20 iterations of the self-tcb-reduction Squeeze Loop)
**Question:** now that the process is understood, is it worth refactoring `src/pycsl` functions to be
smaller and easier to prove? **Answer: yes, and the data says exactly which ones and how.**

This is scoped to reducing the self-annotation trusted core (`src/self-annotate/src` mirrors
`src/pycsl` verbatim; every `\trusted` stub we convert must transcribe a live emitter method and
discharge a `requires True / ensures True / assigns <frame>` contract under Why3). Refactoring the
**live** emitter automatically reshapes the mirror (the verbatim-sync gate enforces it), so
"make the live function provable" and "make the mirror function provable" are the same act.

---

## 1. The empirical thesis (why this is worth doing)

Convertibility is not mysterious. Across the 17 handlers converted this campaign vs. the 7 still
blocked, one measurement separates them almost perfectly:

| Group | Count | Median size | Max size | Returns | Nested fns | Slice-loops |
|-------|-------|-------------|----------|---------|-----------|-------------|
| **Converted** (unaryop … field_get) | 17 | **13 L** | 29 L | ≤ 4 | **0** | **0** |
| **Blocked** (var, attribute, slice_access, fstring, ifexpr, call, subscript) | 7 | **63 L** | **304 L** | 5–26 | fstring, ifexpr have 1 | var has 1 |

The converted set has **zero nested functions and (essentially) zero loops**. The blocked set is
big multi-branch dispatchers, or small handlers carrying **one** poison construct.

**The load-bearing insight: one hard branch poisons the whole function's proof.**
`_handle_var_expr` is 63 lines with **14 return branches**. Thirteen of them are trivial pure
string returns (`return whyml_ident(name)`) that would convert instantly. The fourteenth — the
`_todict_aliases` branch with a `for _p in _parts[1:]` seq-slice loop whose `variant {}` references a
program `val` in a logic context — is un-provable. Because they share one function body and one
contract, that single branch makes **all 63 lines trusted**. Decomposed, var becomes *13 converted
leaves + 1 small trusted leaf*.

This is the whole strategy: **decomposition localizes the irreducible.** The item-3 ceiling
(Gödel/Löb: the recursion leaves `_expr_to_whyml`/`_stmts_to_whyml` and the D2 axioms must stay
trusted) is real, but today it is *smeared* across large handlers. Refactoring pushes the trusted
boundary **down** to exactly the irreducible constructs, converting everything above them.

**Why this is low-risk here (unusually so).** These are behaviour-preserving extractions in an
**output-deterministic** emitter guarded by two mechanical gates:
- **byte-diff 0** across the 627-file corpus (`bin/byte-diff-sweep.sh` + `diff -rq`), and
- **verbatim mirror-sync** (`bin/check-self-annotate-mirror-sync.py`).

An extraction that returns the same string is *provably* inert. Refactoring-for-provability is the
**safest** kind of change in this codebase — the gates catch any drift the instant it happens.

---

## 2. The five provability anti-patterns (each grounded in a real handler)

| # | Anti-pattern | Where it hurts today | Why it blocks the proof |
|---|--------------|----------------------|-------------------------|
| **A** | **Multi-return dispatcher** | `_handle_var_expr` (14 ret), `_handle_call_expr` (26 ret), `_handle_subscript` (23 ret / 47 if), `_handle_attribute_expr` (10 ret) | N independent concerns share 1 contract + 1 frame; the union of their VCs is huge and any one hard branch fails the whole. |
| **B** | **Nested closure** | `_handle_fstring_expr` (`_sp` inner fn), `_handle_ifexpr_expr` (1 nested fn) | A nested `def` types differently under proof mode than under `--no-proof` (the iter-14 false-positive); its captured refs cross the value/logic boundary. |
| **C** | **Loop whose bound/variant uses a program `val`** | `_handle_var_expr` `_todict_aliases` (`_parts[1:]` → `variant { seq_sub … }`) | A `variant {}` / `invariant {}` is a **logic** term; a program `val` (`seq_sub`) is unbound there. Fixing via `function`+axiom would *smuggle an axiom* (forbidden). |
| **D** | **Deep reflection chain** | `_handle_call_expr` (285 L), `_handle_subscript` (304 L), `_call_named_builtins` (399 L) | Long `.get(...)`/subscript projection chains over `emit_ir` make wide, brittle VCs; a single mis-typed projection deep in the chain fails typecheck. |
| **E** | **Union / nested data in one value** | `_handle_field_get_expr` (`_class_constants: Dict[str,Dict]`), `_handle_var_expr` (`_module_constants: Union[str,int]`) | The int-collapse can't carry two shapes in one slot. **Both are now solved** (nested-map feature; union→string modeling) — they show the pattern and that it's tractable. |

---

## 3. Concrete proposals, prioritized by ROI

Each is a **refactor** (byte-diff 0). Sketches are illustrative, not literal.

### R1 — Split `_handle_var_expr` into a dispatcher + per-branch resolvers  ⭐ highest ROI/effort
`expressions.py:3993`, 63 L, 14 returns, 1 loop, 2 `_add_abstract_op`.
The 14 branches are already disjoint (`if name in X: return …`). Extract each:

```python
def _handle_var_expr(self, node, local_refs, subst=None):
    name = self._var_name(node, subst)
    for resolve in (self._var_todict_alias, self._var_quant_binder, self._var_local_kind,
                    self._var_param, self._var_shared, self._var_module_const,
                    self._var_global_class, self._var_constructor, self._var_class_name):
        r = resolve(name, local_refs, subst)
        if r is not None:
            return r
    return self._var_opaque_constant(name)
```

**Payoff:** ~12 of the 13 non-loop resolvers are pure `assigns \nothing` string returns → convert
immediately. Only `_var_todict_alias` (the seq-slice loop, anti-pattern C) stays trusted, and it
shrinks to ~8 lines. `_var_module_const` converts once its value is modelled as string (the
union-narrowing work, already validated). **var: 63 trusted lines → ~8.**

### R2 — Hoist nested closures to methods (fstring, ifexpr)  ⭐ unblocks an entire class
`_handle_fstring_expr` (`expressions.py:4154`, `_sp`), `_handle_ifexpr_expr` (`:4270`).
Replace the inner `def _sp(p): …` with a real method `_fstring_str_part(self, p, …)`. A top-level
method has a stable signature that proof-mode and `--no-proof` type **identically** (killing the
iter-14 false-positive class), and its frame is explicit.

**Payoff:** fstring's parts-loop and ifexpr become provable modulo their own (now-small) bodies.
Also makes the auto-try harness trustworthy again (no nested-fn false positives).

### R3 — Decompose the two giants: `_handle_call_expr` (285 L) + `_call_named_builtins` (399 L)  ⭐ biggest line payoff
`expressions.py:2371` and `_call_named_builtins` (399 L, the single largest function in the package).
Split by **call shape** into named helpers: `_call_method`, `_call_builtin`, `_call_constructor`,
`_call_abstract_op`, `_call_contract_predicate`, … each dispatched from a thin `_handle_call_expr`.

**Payoff:** ~680 lines of the trusted core fragment into bounded helpers. The pure-formatting shapes
(constructor application, arity-fixed builtins) convert; the deep-reflection shapes (varargs,
`emit_ir` args splat) isolate as small trusted leaves. Highest absolute trusted-line reduction, but
most effort — do it **after** the pattern is proven on R1/R2.

### R4 — `_handle_slice_access_expr` → one helper per slice kind
`expressions.py:4342`, 77 L, 5 returns (seq-slice, string-slice, array-slice, opaque, …).
Each return is a distinct slice model already. Extract `_slice_seq`, `_slice_string`, `_slice_array`.

**Payoff:** the string/array cases convert; the subscript-on-`emit_ir` reflection case isolates.

### R5 — Extract pure string-assembly / escaping helpers  ⭐ free wins, do first
Recurring inline fragments that are trivially `assigns \nothing`:
- the WhyML string-literal escaper `'"' + s.replace("\\","\\\\").replace('"','\\"') + '"'`
  (in `_handle_var_expr` and elsewhere) → `_whyml_string_literal(s)`.
- projection formatters like `f"({proj} {rv})"` → tiny named formatters.

**Payoff:** each extracted pure function converts on sight (no state, no branching), DRYs duplicated
logic, and shrinks every caller. Low effort, builds confidence, and immediately drops the trusted
count. **Start here.**

### R6 — `_handle_subscript` (304 L, 47 ifs) → per-receiver-kind helpers
`expressions.py:3619`. The largest branch-count in the package. Split by receiver: body-dict,
self-field-dict, nested-map (the new path), array, string-split, tuple-destructure, opaque.

**Payoff:** large fragmentation; several receiver kinds convert. High effort — pair with R3 as the
"giants" phase.

### R7 — Emit a logic-safe loop variant for slice/seq loops (structural, unblocks anti-pattern C)
Not an extraction but a targeted emitter change: for a for-loop over a seq/array **slice**, emit the
`variant {}` using the base collection's `Seq.length`/`Array.length` (pure **logic** functions) minus
the index, instead of re-lowering the slice with the program `val seq_sub`. The measure still
decreases (the base length is loop-invariant; the index rises), and it lives entirely in logic.

**Payoff:** unblocks var's `_todict_alias` leaf **and** every future seq-slice loop, with **no added
axiom**. Note: this one *may* change emission (it's arguably a fix, not a pure refactor) — gate it as
a feature (byte-diff enumerates the changed set; it should be exactly the seq-slice-loop sites).

---

## 4. Gating discipline for provability refactors

Every extraction, per function, in order:
1. **Extract**, keeping the returned string byte-identical.
2. `--no-proof` typecheck of the mirror locally (fast).
3. **byte-diff 0** over the 627-corpus (`PYTHONHASHSEED=0 bin/byte-diff-sweep.sh` + `diff -rq`) —
   the authoritative "behaviour-preserving" check.
4. **verbatim mirror-sync** green.
5. Convert the new leaves that are now provable; **full proof** before commit (the `--no-proof` check
   is *not* sufficient for nested-fn/logic constructs — the iter-14 lesson).

**Two traps to respect:**
- **`_add_abstract_op` ordering is shared mutable state.** Several handlers register abstract ops as
  a side effect; extraction must preserve registration **order** or the preamble reorders → byte-diff
  ≠ 0. The gate catches it, but design extractions to keep the call order.
- **Don't disguise a feature as a refactor.** If an extraction changes emission, it is a feature;
  gate it as one (R7 is the honest example).

---

## 5. Recommended sequencing

1. **R5** (pure helpers) — free conversions, zero risk, warms up the workflow.
2. **R2** (hoist nested closures) — kills the nested-fn class + the auto-try false-positive.
3. **R1** (var dispatcher split) — high value, fully understood; lands var minus one small leaf.
4. **R7** (logic-safe variant) — structural, unblocks the seq-slice leaf R1 leaves behind.
5. **R4** (slice_access) — medium.
6. **R3 + R6** (the call/subscript/builtins giants) — biggest payoff, most effort; do last, once the
   pattern is proven and the harness is trustworthy.

---

## 6. Non-goals and risks

- **Do not decompose the Gödel-ceiling leaves.** `_expr_to_whyml` (264 L) and `_stmts_to_whyml` are
  the recursion cores that *must* stay trusted (item-3). Splitting them buys nothing — they are
  irreducible by construction. Leave them; decompose everything that *calls* them.
- **Over-fragmentation has a cost.** Each extraction carries a byte-diff verification and a readability
  budget. Stop when a function is one concern; don't shatter it into one-liners.
- **65 functions are ≥ 60 lines** package-wide, but most are *not* on the trusted-conversion path
  (e.g. `_emit_type_decls`, `_scan_preamble_needs` are preamble builders). Target the `_handle_*`
  dispatchers and their helpers first — they're what the mirror must prove.
- Some big functions earn their size (dense, single-concern table lowerings). Size is a *signal*, not
  a mandate; the real predictors are **branch count** and **presence of a poison construct**.

---

## 7. Expected outcome

Decomposition doesn't delete lines — it **re-partitions the trusted surface** so most of it converts:

- **var** (63 L) → ~55 L convert, ~8 L trusted leaf.
- **fstring / ifexpr** (~110 L) → mostly convert once closures are hoisted.
- **call / subscript / builtins** (~990 L) → est. 60–70 % convert, the reflection cores isolate.

Rough estimate: the ~600 lines of blocked `_handle_*` handlers become **~150 lines of small,
clearly-irreducible trusted leaves** — a genuine, honest shrink of the TCB, with each remaining
trusted leaf now *auditable at a glance* (which is itself a win: a 63-line trusted handler hides its
irreducible core; an 8-line one exposes it).

**Bottom line:** yes — refactor. Start with R5 + R2 (safe, fast), prove the pattern on R1, then take
the giants. The gates make it low-risk, and the empirical size/branch correlation makes the payoff
predictable.

---

## Execution log — 2026-07-03

| Step | Outcome | Commit | Count |
|------|---------|--------|-------|
| **R5** | `_whyml_string_literal` extracted; proven leaf. byte-diff 0. | df517398 | 1277 |
| **R2** | fstring `_sp` → `_fstring_str_part`, ifexpr `_cf5_arr` hoisted; both proven leaves. byte-diff 0. | ae1dbab1 | 1277 |
| **R1** | var's hard branch isolated to `_var_todict_alias`; `_handle_var_expr` (13 branches) CONVERTS. byte-diff 0. | 650ca7e3 | 1277 |
| **R7** | logic-safe seq-slice loop variant → `_var_todict_alias` CONVERTS → **var fully verified**. byte-diff 0. | ca26b2e5 | **1276** |
| **R4** | slice_access ESCALATED — deep-reflection cascade (slice-bound reflection + helper-arg emit_ir threading), beyond decomposition. | — | 1276 |
| R3/R6 | not attempted (the 285–399 L giants). | — | — |

**Headline: var fully converted (1277→1276, 18 handlers) via the R1+R7 isolate-then-fix pattern —
the refactor thesis validated in practice.**

### Key learning (refines the thesis)
Decomposition/hoisting **isolates** the hard construct but does **not by itself convert** the parent —
the isolated construct still needs its own targeted fix:
- **var**: R1 isolated the seq-slice branch; **R7** (logic-safe variant) was the actual fix. ✅ converted.
- **fstring**: R2 hoisted `_sp`, but the parent stays trusted on its **manual `while i_part < n_parts`
  loops** (bound in a local `n_parts=len(parts)`, no invariant relating it to `Array.length`) — needs
  a for-loop rewrite or an emitted bound invariant.
- **ifexpr**: R2 hoisted `_cf5_arr` + split its 4 tuple-unpacks, but the **seq-arm branch**
  (`_seq_operand` return-type + `local_refs or set()` map-or) blocks the parent.
- **slice_access**: the blocker is **shared** `node.slice` bound-reflection + helpers called with
  emit_ir args — not per-kind, so decomposition doesn't reach it; needs the reflection recognizers +
  emit_ir-threading through `_field_type_of`/`_self_field_dict_nu`.

So the refined recipe: **decompose to isolate → then apply the construct-specific fix** (a recognizer,
a logic-safe variant, a for-loop rewrite). R5/R2 landed as proven infrastructure (helper leaves) that
shrinks the trusted surface even where the parent stays trusted; R1+R7 is the full worked example.
