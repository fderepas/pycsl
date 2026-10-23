# S-ext findings — richer-contracts-bridge spike 1 (2026-07-09)

**Verdict: GREEN** (independently re-verified: export `.mlw` proves 9/9 Valid Alt-Ergo; collision control
fails as designed; `src/pycsl` untouched; ledger 3 untouched). The bridge's foundational feasibility
(export a per-arm emitter + a certified predicate into WhyML, co-host with the emitter's own theories under
M1 namespacing) holds. Two corrections to `richer-contracts-bridge-plan.md`:

1. **Extraction is OCaml-ONLY — no Rocq→WhyML path.** `Phase6L_EmitExtract.v` sets `Extraction Language
   OCaml`. So the export is a **faithful WhyML RE-STATEMENT** of `Phase6L_EmitAssign.v::emit_assign` (as
   `emit_F_assign`), NOT auto-extraction. **Material consequence:** the plan's P0 "generate-don't-write ⇒
   cannot drift" (§1.2, §4) is WEAKER than stated — a hand-transcribed re-statement IS a drift vector. The
   anti-drift discipline must therefore be a **mechanized cross-check** (the WhyML re-statement byte-diffed
   against the EXISTING OCaml extraction on shared `extraction-byte-diff` cases), NOT "generation prevents
   drift." Named bridge-audit obligation: `EmitAssignExport.emit_F_assign ≡ Phase6L_EmitAssign.emit_assign`
   — an obligation to audit, NOT a soundness axiom (ledger stays 3).
2. **The predicate is `wf_ir`, not `wf_pyval`** (`Phase2c_PyValDict.v`; `wf_val`/`wf_dict` + `Theorem
   wf_ir_binds`, axiom-free). No `wf_pyval` exists. Exported `wf_ir` + `size`/`size_pos`.

**Measured:** `why3 prove -P alt-ergo src/formal-semantics/pycsl-formal-export.mlw` → 9/9 Valid, exit 0.
Co-hosts `PyValExport`(size) + `EmitIrAdt`(size) + `EmitAssignExport` via qualified `use … as PV/EI/FX`;
`size_coexist` Valid. Collision control (inlined sizes): `Symbol size is already defined in the current
scope`. Usability proved: `wf_ir_usable` (C1 shape), `emit_usable` (`emit_F_assign … = "let x = ref y in\n"`,
the C3 shape). Evidence: `src/formal-semantics/pycsl-formal-export.mlw`.

**Consequence for the plan:** P0/P1 unblocked. Add to P0 the anti-drift cross-check (re-statement ↔ OCaml
extraction). Next gate: **S-c1** (does `ensures wf_ir \result` discharge on a real mirror pyval/record
output within SMT budget?).
