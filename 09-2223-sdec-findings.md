# 09-2223-sdec-findings.md — extended S-dec spike: MEASURED verdict

*Executed 2026-07-09 per `09-2223-fix.md` Appendix. A **falsifier spike** for M1+M2 of `09-2223-plan.md`.
All work is hand-written `.mlw` (zero source edits); the spike measures whether the decoder-based **target
WhyML** is reachable, well-typed, dischargeable, and axiom-clean — the make-or-break for the composition
wall. Every verdict below was **independently re-verified** (re-emitted / re-proved with Alt-Ergo + Z3 /
ledger-audited). Evidence `.mlw` in `getting-better/composition-wall/`.*

## Verdict: M1+M2 CONFIRMED at the target level — the composition wall is dissolvable for B-comp

The plan's diagnosis holds under measurement. My fix's two blocker-concerns (C1 certificate, C2 clash
relocation) are **answered by the spike**, not by argument.

### M1 — two-theory hosting works (rename); collision is real (`sdec-m1-two-theory.mlw`)
- **Control** (no rename): a module hosting both the `pyval` theory and the `emit_ir` ADT fails —
  `Symbol size is already defined in the current scope` (why3 exit 1). The collision is real.
- **Spike** (rename pyval `size`→`pv_size`): the two-theory module **type-checks** and **all goals
  discharge under best-of-N** — the `pv_size` lemma pack via Alt-Ergo; the four `emit_ir` size-decrease
  lemmas Alt-Ergo times out on but **Z3 discharges in 0.02s each** (matching PyCSL's Alt-Ergo→Z3 policy).
  Re-verified: `why3 prove -P z3` → `size_left/right/svalue/sindex/object_dec` all Valid.
- **Rename is WhyML-emission-only.** The Rocq/Lean certs define their *own* `size` (`def size : PyVal →
  Nat`), independent of the emitted measure — renaming the WhyML measure changes **no** `.v`/`.lean`
  proposition, so `Print Assumptions`/`#print axioms` are unchanged *by construction*, no recompile. Cost:
  a name-correspondence note (`pv_size` ↔ cert `size`).

### C2 linchpin — `_collect_calls` is `pyval`-NATIVE (the clash does NOT relocate)
Verified from the actual emitted mirror (`ir_resolve.mlw`), and its mirror is **already verified (0
`\trusted`)**:
```
let rec _collect_calls (obj: pyval) : map string bool   variant { size obj }
```
It consumes **`pyval`** (a full pydict catamorphism `__pre`/`__dict`/`__list`), NOT `array int`/`emit_ir` as
the plan/brief hypothesized. So the decoder's `fn_body : pyval` feeds it directly — **C2 is REFUTED for
B-comp**: the composition type-checks *and* proves through the sibling. (The general C2 risk still holds for
methods whose sibling is NOT pyval-native — those need the decoder to hit `array int`/`emit_ir`.)

### M2 — through-the-sibling-chain, whole B-comp body proves (`sdec-m2-bcomp-target.mlw`)
Hand-built the decoder-based lowering of the FULL `_build_soundness_report` body: `decode_func`/
`decode_func_list : pyval → list ir_func`, the `for f` loop with `fn_name`/`fn_ensures`/…, `counts[bucket]
+= 1` (variable-key option-map update), `set_inter`/`set_diff`, `sorted`, and **`deps = sorted(
_collect_calls(f.fn_body) & trusted_names - {name} )`**.
- **20/20 goals Valid** (Alt-Ergo), including `_collect_calls'vc` AND **`_build_soundness_report'vc`** (the
  whole-body VC: type-safety + termination + `ensures True`). Re-verified independently.
- **One correction to the plan's §5:** `sorted → array string` is a WhyML **region/aliasing violation** when
  embedded in the immutable return (`sdec-m2-array-control-fails.mlw` dies at `let deps = …`: *"prohibits
  further usage of vcs"*). Fix: the sorted payload is an immutable `seq`/`list string`, not a mutable
  `array` — PyCSL's known nested-mutable-container rule (an already-solved class), the sole diff between the
  failing and passing spikes.

### C1 certificate — branch (a), no new certificate (measured)
`decode_func` is non-recursive (leaf/opaque projections); `decode_func_list` is a structural
`size`-decreasing fold on `pyval` producing `list ir_func`. The new types (`ir_func`, `vc_entry`,
`soundness_report`) are **records over already-certified fields** (string/bool/pyval/list/int) — certified
by construction (`Phase2b_RecordVal`). No new Rocq/Lean theorem is introduced; the **20 SMT `'vc` goals ARE
the per-instance proof**, discharged first-order using the *already-certified* pyval `size` measure. Ledger
diff **empty**. **No axiom is needed for the discharge.** (Honest nuance: the spike shows no axiom is
*needed*; a real build should still confirm the meta-theory formally covers a `pyval → list<record>`
*eliminator* — not just records and not just pyval-endofunctors — under the coupling rule.)

## Corrections to `09-2223-plan.md` (both verified)
1. **M1 is UNEXERCISED by B-comp.** B-comp's module (`pycsl.py`) has **0** references to `emit_ir`/
   `_expr_to_whyml`/`@mutable_state`; its only sibling is the pyval-native `_collect_calls`. So B-comp needs
   only **M2**. M1 enables a *different* class (a method calling an emit_ir-consuming sibling AND needing
   pyval in one module). The plan's "M1 → … → B-comp" ordering overstates M1's role on this benchmark.
2. **`sorted` payload must be immutable** (`seq`/`list string`), not `array string` (§5) — the region wall.

## What this does and does NOT establish (the critical scope)
- **DOES:** the decoder-based TARGET WhyML for B-comp is reachable, well-typed, **whole-body provable
  (20/20)**, and **axiom-clean (ledger 3)**. My brief's pessimism ("the composition is the wall, maybe
  research-grade") is **overturned at the target level for IR-shaped reflection with a pyval-native sibling**.
- **Does NOT:** prove PyCSL's **emitter** can GENERATE this decoder-based lowering from the verbatim Python
  source. That is the **M2 emitter build** (a recognizer that hoists the reflective read to a `decode_*`
  boundary, mirror-gated, byte-diff-0, fidelity-verbatim) — deliberately not done here. The spike de-risks
  its make-or-break; the build itself is the next phase.

## Campaign consequence
The question shifts from *"is the composition wall crossable?"* (answered: **yes**, for IR-shaped reflection
with pyval-native siblings, at the target level, no new axiom) to *"can the emitter produce the decoder
lowering, and for how many of the ~70 methods?"* — i.e. the **M2 emitter build** + the **C5 census**
(IR-shaped vs non-IR-shaped; and per-method: is the sibling pyval-native, or does the decoder need
`array int`/`emit_ir` targets?). B-null narrows to: non-IR-shaped reflection, non-pyval-native-sibling
methods, semantic-guard-dominated safety, frame-inexpressible siblings.
