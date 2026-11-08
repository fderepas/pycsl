# `irgiven-impl.md` — impl plan: add the `IrGiven` clause constructor, convert `_parse_act_block`

Gate P requires: FIRST action is a make-or-break spike, an explicit refutation exit, the three-L-plane
battery, and honestly-costed scope. All four are below.

## Target
`src/self-annotate/src/frontend/Module2_Parser.py::_ContractParser._parse_act_block` (18 live LOC),
currently `#@ \trusted`. Expected yield: **1** marker (673 -> 672).

## Root cause (measured, not assumed)
`Requires`/`Ensures` lower to variant constructors `IrRequires`/`IrEnsures`; `Given` has no entry in
the CSL-class-to-ctor map, so it falls back to a bare record literal `{ given_expr = ... }`. The
`clauses` sequence is then heterogeneous and Why3 rejects it at L3-tc:
`Module2_Parser.mlw:1011 — This expression has type emit_ir, but is expected to have type int`.

## Soundness artifact — ALREADY EXISTS, no new certificate
`src/formal-semantics/rocq/Phase2k_CslClause.v` already defines
`CGiven (e:emit) | CRequires | CEnsures | CAssigns` with `clause_kind_of` / `is_K_node` /
`clause_expr_of`, self-audited axiom-free (Rocq 43/43 Closed / 0 axioms; Lean `{propext}` only).
The emitter simply never used the `CGiven` arm. **LEDGER MUST STAY 3 — do not add any axiom.**

## STEP 0 — MAKE-OR-BREAK SPIKE (do this FIRST, before any other edit)
Add ONLY the constructor plumbing, leave `_parse_act_block` still `\trusted`, and check emission:
1. `module6_whyml/expressions.py` ~line 1600: add `"Given": ("IrGiven", ["expr"])` beside
   `"Ensures"`/`"Requires"`.
2. `module6_whyml/preamble.py` ~line 4932: extend the **`_uses_clause_ir()`-gated** group to
   `" | IrInterfaceClause string emit_ir | IrEnsures emit_ir | IrRequires emit_ir | IrGiven emit_ir"`.
   Follow that gating EXACTLY — it is what keeps the corpus byte-inert.
3. Add the matching **`size`** arm and **`kind_of`** arm for `IrGiven`, gated identically (grep the
   file for how `IrRequires` gets its `size`/`kind_of` arms and copy that shape verbatim;
   `kind_of (IrGiven _) = "Given"`, matching `clause_kind_of` in the certificate).
Then run, in the FOREGROUND:
```bash
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py src/self-annotate/src/frontend/Module2_Parser.py \
    --import-path src/pycsl --no-proof --keep-mlw
```
**SPIKE PASSES** iff L3-tc is ✓ with the constructor added and nothing else broken.
**REFUTATION EXIT — if the spike FAILS, STOP.** Do NOT start widening matches to chase
exhaustiveness errors across the tree. Revert both files by exact path, and report the exact error.
That is a CERTIFIED-BOUNDARY result and is a fully successful outcome.

## STEP 1 — convert (only if STEP 0 passed)
Port the live `_parse_act_block` body VERBATIM into the mirror, drop the `#@ \trusted` line, keep
`#@ requires True / ensures True / assigns self.i`, and add the established loop-annotation idiom
immediately above the `while` (copy it verbatim from `_parse_qualname` in the same mirror file):
```
#@ loop invariant self.i >= \old(self.i)
#@ loop invariant 0 <= self.i and self.i < \length(self.toks)
#@ loop invariant self.toks[\length(self.toks) - 1].py_type == "EOF"
#@ loop variant \length(self.toks) - self.i
```
The class already carries `#@ class invariant self.toks[\length(self.toks) - 1].py_type == "EOF"`.

## STEP 2 — the three-L-plane battery (ALL required; a `--fun` pass is NOT a substitute)
**Use the CORRECTED prover flags everywhere — the bare default is degraded to Z3-only in this
environment and produces FALSE "unproven" verdicts:**
```bash
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py <file> --import-path src/pycsl \
    --provers "Alt-Ergo,2.6.3,,Z3,4.13.3,"
```
1. **Type-safety** — whole-file proof of `src/self-annotate/src/frontend/Module2_Parser.py` = 0
   non-Valid.
2. **§10c IMPORTER SWEEP — the trap that reverted a prior increment.** A change to the SHARED
   clause-IR theory must L3-tc on EVERY importer mirror, not just the changed file. At minimum
   re-check `Module5_IREmitter.py`, `Module3_Weaver.py`, `core_ir_semantic.py` and any other mirror
   whose `_uses_clause_ir()` is true. A prior tuple-return-exception build passed its own file and
   the corpus but broke `Module5_IREmitter` L3-tc, and had to be reverted.
3. **Fidelity** — `bin/check-self-annotate-sync.sh` must show EXACTLY the 2 known DIVERGED
   (`expressions.py::_handle_var_expr`, `stmt_control_flow.py::_handle_for_stmt`) and
   `bin/self-annotate-mirror-check.sh` EXACTLY the 3 known drifted mirrors
   (`expr_ghost_collections`, `statements`, `stmt_control_flow`). Both scripts exit 1 at HEAD —
   that is the accepted BASELINE. Do not "fix" it; just do not make it worse.
4. **Corpus inertness** — this touches `src/pycsl`, so byte-diff is a HARD gate, not by-construction.
   Worktree-at-HEAD baseline with `.venv` symlinked, ONE foreground sweep each side, and **read the
   `emitted N` line on BOTH sides and assert N is equal and NONZERO** (a sweep that emitted 0 files
   is a false green).
5. **Ledger == 3** — `proof_axiom_allowlist.py` untouched.
6. **Non-vacuity** — inspect the emitted WhyML: the `Given` branch must really construct
   `IrGiven (...)` over a real `_parse_expr` result. `bin/check-emitted-vacuity.py` exit 0.
7. **Count** — `grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l` = 673 -> 672.

## Refutation / revert policy
Any gate red that is not fixable in ONE bounded, obvious step => revert EVERYTHING by exact path
(`git checkout -- <one.exact.file>` naming each file you personally edited) and report the finding.
A clean CERTIFIED-BOUNDARY beats a half-landed build.
