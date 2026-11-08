# Wall-plan-v2 Phase 2′b — verified NO-GO, and the wall's TRUE location (2026-07-07)

**Independently verified** (HEAD `7b877a85`, count 1248, tree clean, ledger==3; Phase 2′b landed no code — building any piece requires the missing subsystem below).

## The effort has now decomposed the wall into three layers — two SOLVED, one remaining

| layer | question | status |
|---|---|---|
| **L1 value modeling** | model a heterogeneous `Dict[str,Any]` in WhyML, SMT-tractably | **SOLVED** — Phase 0/1: `pydict` concrete + interned keys + compute-before-solve; axiom-free Rocq+Lean certificate, ledger==3 |
| **L2 target-shape provability** | do the benchmark walkers, *hand-written* as their target WhyML, prove? | **SOLVED** — Phase 2′a GO: S1 (generic iteration + unbounded recursion + by-ref mutation + `size`-variant) and S2 (`List[pydict]` recursion + `doc` string tail) both Valid on both provers |
| **L3 emitter code-generation** | can the emitter EMIT that proven shape from the verbatim imperative source? | **NO — this is the real wall** |

## Why L3 is not additive routing (the verified root cause)

The Phase-2′a-proven target shape is a **multi-helper structural recursion**; the emitter cannot produce it:

1. **1 Python function → 1 WhyML declaration.** The only multi-decl mechanism is cross-function SCC
   grouping (`scc.py`, `let rec … with …` across *distinct source functions*). There is **no mechanism to
   synthesize auxiliary verified helpers from a single method.** The proven S1 shape needs **5 synthesized
   symbols from one method** (`walk` + `walk_dict` + `walk_list` + `get_target` + `set_add`); S2 needs
   `find_rt` + `get_type` + `get_body` + the `get_body_lt` lemma + `render` + `doc`.
2. **`for` lowers to a `while`-loop, not a recursion — and termination REQUIRES the recursion.** Verified
   directly (`stmt_control_flow.py`: `for x in it` → `while !idx < iter_length it … iter_get it !idx`).
   A single-function while-loop lowering of `find_named_expr_targets` **cannot prove termination**: the
   self-call `walk v` needs `size v < size obj`, derivable ONLY when `v` is **spine-bound** as
   `DCons _ v rest` (via the proven `size_dict_mem`). In a `while`-loop, `v = iter_get obj i` is **opaque**,
   so the `size`-decrease VC is underivable. The Phase-2′a spike splits out `walk_dict` **precisely** to
   make iteration a structural cons-spine recursion. That helper is **mandatory**, and synthesizing it is a
   **new code generator**, not a routing rule. **The plan's E-iteration "generalize the `variant {size p}`
   synthesis" cannot substitute** — that synthesis adds a variant to a function *already recursive over its
   param*; it cannot turn a loop into a recursion.
3. `.items()` additionally collapses at IR emission (`Module5_IREmitter.py:1477`: a non-`ast.Name` `for`
   target → the single opaque `"_for_target"`; `k`/`v` are never bound) and is modelled as an opaque
   int-iterator — so even the source-level iteration variables don't survive to Module 6.
4. **F4 `doc`** likewise needs the `", ".join(...)` tail rewritten into a `DCat` fold + a synthesized
   `render` — body-structural, not a type route.

## Verified NO-GO evidence
Both benchmark methods fail at **L3 typecheck, before proving is reachable**: `find_named_expr_targets`
→ WL-05b method-exclusion rejection, then `unbound 'k'` (the `.items()` collapse); `find_return_type`
→ `int` vs `string` (dict reads default to int) + no synthesized `variant`. Count **1248, 0 converted**
(honest); byte-diff untouched (no emitter edit); ledger==3.

## The wall, finally located
It is **not** the value type (L1 solved, certified) and **not** the logic (L2 proven). It is a
**compiler-transformation gap**: PyCSL's emitter has no **loop→structural-recursion + per-method
helper-synthesis** pass, and the proven-provable target shape cannot be reached without one. This is a
well-posed, known-hard compilation problem (imperative→functional / recursion extraction, verified),
distinct in kind from everything Phases 0–2′a addressed.

## Options
1. **Phase 2′c — build the synthesis subsystem.** A loop→cons-spine-recursion transformer + per-method
   helper synthesis (emit `walk`/`walk_dict`/`walk_list` + monomorphic `get_<key>` + `render` as a
   verified `let rec … with …` group from one method), starting with **E5-for-methods** (clears blocker
   #1, tractable) then the `.items()`→`walk_dict` synthesis. A multi-day **new-subsystem** build, materially
   bigger and different from routing; its own go/no-go.
2. **Bank + close v2.** Keep the certified L1 foundation (real, axiom-free, banked at 1248), accept the
   generic-iteration walkers as `TRUSTED(essential)`, and fold the **precisely-located L3 question**
   (verified loop→recursion + helper synthesis for a `pydict` iteration protocol) into the external-review
   problem statement — it is now a sharp, well-posed compilation question with known prior art.
