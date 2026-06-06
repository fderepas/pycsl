# Implementation Plan — Continue Executing `closer-to-code-execution-status.md` (post-2026-05-29)

> Next slice of execution against the multi-quarter plan. Three
> items, sequenced: (A) Lean Why3Trust cert-as-witness port for
> Lean/Rocq parity, (B) CC.4 self-annotate citations (add formal-
> semantics theorem refs to 4 mirror modules), (C) Q4 U.2 sketch —
> `ir_to_stmt` for the simple subset.

LEGACY (superseded, kept for context):
- The prior plan in this file covered Items 4/1/2/3 (Q3 Sub-β
  tightening + Q1 close-out + housekeeping + Q4 U.1). All landed
  2026-05-29. End state: zero axioms in the Rocq Why3-validation
  chain; `pycsl_soundness` on standard propext+funext only.
> Working directory: `/home/fabrice.derepas@canonical.com/git/pycsl/`
> Switch: `coq-4.14` (OCaml 4.14.2).

## Context

The `closer-to-code-execution-status.md` doc's "Next ticketable
actions (post 2026-05-29)" lists six items. This plan tackles the
three executable-in-one-session items, in priority order:

1. **Lean Why3Trust cert-as-witness port** — match the Rocq side's
   axiom-elimination on the Lean side. Currently Lean's
   `why3ImplementsWpW_derived` depends on `why3ValidatesEmitted`
   (Axiom). Rocq parity makes this axiom go away too.
2. **CC.4 self-annotate citations** — exploration found that
   citations don't exist YET in the 26 self-annotate mirrors (no
   stale citations to fix). The work is to ADD 4 new citations
   per `self-remains.md` §CC.2's table to anchor the trust chain.
3. **Q4 U.2 sketch — `ir_to_stmt` for the simple subset** — the
   plan estimates ~2 weeks for full U.2. This session covers the
   simple-subset slice (Skip/Assign/AugAssign/ArraySet/Seq plus
   helpers), reusing structure from `bin/ir-to-rocq-ast.py`. Full
   U.2 + U.3 + U.4 remain multi-week and continue beyond this
   session.

DEFERRED to future sessions:
- Q4 U.2 expanded subset + U.3 validate_ir_correspondence + U.4
  extraction byte-diff on real corpus (multi-week each).
- Class/method formal modelling (multi-week foundational work).

Current verified state (Rocq):
- `wp_gen_correct`, `vcg_sound`, `vcg_bridge`, `module6_encodes_mlw`,
  `why3_validates_emitted`, `why3_validates_vc_formula`,
  `why3_implements_wp_w_derived`: ALL closed under the global context
  (zero axioms).
- `pycsl_soundness`, `pycsl_soundness_verified`: propext + funext only.

Current Lean state:
- `why3ImplementsWpW_derived` depends on `[why3ValidatesEmitted,
  propext, Classical.choice, Quot.sound]`.
- `Why3Certificate` is still an opaque private structure
  (`Why3Trust.CertImpl`) with empty unit-like constructor.
- `Why3Trust.check` returns `Option (Why3Certificate _ws _Q)` by
  invoking the `why3` binary, parsing for "Prover result is:
  ... Valid" lines, returning `some ⟨⟩` on success.

The Lean port can completely eliminate `why3ValidatesEmitted` by
the same construction Rocq used: make `Why3Certificate` BE the
witness type, then `Why3Trust.check` constructs the witness by
threading what was previously the axiom statement through.

---

## Item A — Lean Why3Trust cert-as-witness port

### Problem

`why3ValidatesEmitted` (VcgSemBridge.lean:68-72) is an Axiom:
```lean
axiom why3ValidatesEmitted
    (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState) (f : VcFormula) :
    Why3Certificate ws Q →
    f ∈ emitVcList ws Q preEs es →
    evalVcFormula f es preEs
```

This axiom asserts "if you have a cert, every emitted VC's
`evalVcFormula` holds." On the Rocq side this was eliminated by
making the cert type itself BE that statement (as a function).
The same move works in Lean.

### Approach

Mirror the Rocq Phase 5 refactor (Phase6c_VcFormula.v →
Phase6j_Why3Trust.v ordering, witness-as-cert):

1. **File ordering** — currently `Why3Trust.lean` is upstream of
   `VcFormula.lean` (Why3Trust imports nothing PyCSL-internal that
   matters; VcFormula imports `Why3Vcg.lean`). To make `Why3Certificate`
   reference `VcFormula` types, we need to either:
   - (a) Move the cert definition INTO a new file
     `PyCSL/Why3CertWitness.lean` placed AFTER `VcFormula.lean`,
     OR
   - (b) Have `Why3Trust.lean` IMPORT `VcFormula.lean` directly
     (since `VcFormula.lean` doesn't depend on `Why3Trust`).

   **Recommended: (b)**. Simpler — keeps the cert type colocated
   with `Why3Trust.check`. Verify `VcFormula.lean` truly doesn't
   import `Why3Trust` (exploration says it doesn't).

2. **Replace `private structure CertImpl` with witness type
   definition** in `Why3Trust.lean`:
   ```lean
   def Why3Certificate (ws : WhyMLStmt) (Q : WpConts) : Type :=
     ∀ (preEs es : ExecState) (i : Nat) (f : VcFormula),
       vcFormulaOf ws Q preEs es i = some f →
       evalVcFormula f es preEs
   ```

3. **Rewrite `Why3Trust.check`** to construct the witness
   function on success. The body becomes:
   - Run `why3 prove` as before.
   - If all valid: return `some (fun preEs es i f hEq =>
       why3ValidatesEmitted_axiom ws Q preEs es f (... reified
       trust ...) (vcFormulaOf_mem_emitVcList hEq))`.
   - Else: return `none`.

   **The trust line moves into `check`'s body** — exactly the
   intended design. The construction-site axiom becomes the
   minimal `realWhy3Verdict` statement:
   ```lean
   axiom realWhy3Verdict
       (ws : WhyMLStmt) (Q : WpConts) (preEs es : ExecState)
       (f : VcFormula) :
     f ∈ emitVcList ws Q preEs es → evalVcFormula f es preEs
   ```
   Or even better — push the axiom into an `unsafe` opaque return
   so `check` is the trust boundary at the IO level (mirroring
   Lean's approach to `IO.unsafeIO` patterns).

4. **Update `why3ValidatesEmitted` in VcgSemBridge.lean**: was
   Axiom; becomes a PROVED Lemma applying the cert directly:
   ```lean
   theorem why3ValidatesEmitted ws Q preEs es f cert hMem :
     evalVcFormula f es preEs :=
     -- cert is now a function; apply it via the index witness
     let ⟨i, hEq⟩ := emitVcList_mem_imp_vcFormulaOf hMem
     cert preEs es i f hEq
   ```

   This requires the helper `emitVcList_mem_imp_vcFormulaOf`
   (reverse of `vcFormulaOf_mem_emitVcList`). If not already
   present in `EmitVcList.lean`, add it — mirror of Rocq's
   `vcf_emit_to_some`.

5. **Verify `#print axioms why3ImplementsWpW_derived`** after the
   refactor:
   - Expected (if step 3's recommended approach lands):
     `[realWhy3Verdict, propext, Classical.choice, Quot.sound]` —
     trades one named axiom for another, but the new one is at
     the cert construction site (where it should be), not at
     the projection site.
   - For full parity with Rocq's zero-axiom state: the cert
     construction in `check` is opaque IO; the proof side has
     no axiom. This is the cleanest end state.

### Critical files

- `src/formal-semantics/lean/PyCSL/Why3Trust.lean` (cert def + check)
- `src/formal-semantics/lean/PyCSL/VcgSemBridge.lean` (why3ValidatesEmitted axiom → proved Lemma)
- `src/formal-semantics/lean/PyCSL/EmitVcList.lean` (add reverse-of-mem helper if not present)

### Risk + fallback

If step 3's witness-construction-in-check turns out to require
heavier proof work than expected (e.g., the proof of the witness
function inside `check`'s body fails to typecheck because the IO
context blocks elaboration), fall back to:

- Keep `Why3Certificate` as the function type.
- Keep `why3ValidatesEmitted` as a (now-redundant) Lemma that
  just applies the cert.
- Make `Why3Trust.check`'s witness construction use a SINGLE
  axiom statement at the `if allValid then ...` branch.

End state in either case: cert is the witness; the trust line
sits at construction.

---

## Item B — CC.4 self-annotate citations (4 mirrors)

### Problem

Per `self-remains.md` §CC.2, four self-annotate mirror modules
should cite formal-semantics theorems to anchor the trust chain.
Currently NO citations exist (no stale citations to fix).

### Approach

Add `#@ proof rocq <theorem_path>` and `#@ proof lean
<theorem_path>` annotations at the module-level of four mirror
files. Per `self-remains.md` §CC.2's table:

| Mirror file | Rocq citation | Lean citation |
|---|---|---|
| `src/self-annotate/src/Module5_IREmitter.py` | `Phase6h_CorrMain.wp_gen_correct` | `PyCSL.CorrMain.wpGenCorrect` |
| `src/self-annotate/src/Module6_WhyMLTranspiler.py` | `Phase5b_Soundness.pycsl_soundness` | `PyCSL.Soundness.pycsl_soundness` |
| `src/self-annotate/src/module6_whyml/preamble.py` | `Phase6i_Soundness.why3_implements_wp_w_derived` | `PyCSL.Why3Vcg.vcgSound` |
| `src/self-annotate/src/Module4_SemanticAnalyzer.py` | `Phase1_AST.<wf_lemma>` (verify name during execution) | `PyCSL.AST.<wf_lemma>` |

### Steps

1. Locate the four mirror files. Verify paths during execution.
2. For each: find the existing `#@ \trusted reviewer: ...` line
   at the module preamble or the first function/method.
3. Add the two new citation lines AFTER the existing reviewer
   line.
4. For Module 4: search formal-semantics for a well-formedness
   lemma on `Phase1_AST` (or related). If none exists, drop
   citation #4 as "no relevant theorem yet" and document.
5. Run `bash bin/run-self-annotation-suite.sh` to confirm
   citations parse (if the suite supports proof-citation
   validation).

### Critical files

- `src/self-annotate/src/Module5_IREmitter.py`
- `src/self-annotate/src/Module6_WhyMLTranspiler.py`
- `src/self-annotate/src/module6_whyml/preamble.py`
- `src/self-annotate/src/Module4_SemanticAnalyzer.py`
- `self-remains.md` (mark CC.2 done after adding)

### Risk + fallback

If the self-annotate suite has strict citation validation and
rejects unknown theorem paths, fall back to adding citations as
free-text comments (not validated `#@` directives) until the
validator is extended.

---

## Item C — Q4 U.2 sketch: `ir_to_stmt` for the simple subset

### Problem

`pycsl_ir_json` (Phase0_IrJson.v) is just shape — no semantics.
U.2's `ir_to_stmt : pycsl_ir_json → option stmt` translates
well-formed IR into the formal `stmt` type. Full U.2 is a ~2-week
ticket. This session covers the simple-subset slice: enough to
parse Pass/Assign/AugAssign/ArraySet into the formal AST,
demonstrating the design. The remaining cases (If/While/Try/
GhostAssign/CriticalSection/etc.) defer to follow-up sessions.

### Approach — translate the converter's case layout

Mirror `bin/ir-to-rocq-ast.py`'s dispatch in Rocq:

1. **New file `src/formal-semantics/rocq/Phase0b_IrToStmt.v`**
   (slotted between Phase0_IrJson and Phase1_AST in `_CoqProject`,
   imports Phase0_IrJson + Phase1_AST). Actually defer: since
   Phase0_IrJson uses Z/String/List only, and Phase0b needs Phase1_AST,
   put Phase0b AFTER Phase1_AST instead. The slot becomes:
   ```
   Phase0_IrJson.v
   Phase1_AST.v
   Phase1b_IrToStmt.v   (NEW)
   Phase1_M234EnglishRefinements.v
   ...
   ```

2. **Helpers** (in Phase1b_IrToStmt.v):
   ```rocq
   Definition json_field_get (key : string) (obj : json_value)
       : option json_value :=
     match obj with
     | JsonObject kvs => find_assoc key kvs
     | _              => None
     end.

   Definition json_to_string (v : json_value) : option string :=
     match v with JsonString s => Some s | _ => None end.

   Definition json_to_z (v : json_value) : option Z :=
     match v with JsonInt n => Some n | _ => None end.
   ```

3. **Expression converter `ir_to_expr : json_value → option expr`**:
   - Dispatch on `json_field_get "type"` value.
   - Cases: `JsonString "Number"`, `JsonString "Var"`,
     `JsonString "BinOp"`, `JsonString "UnaryOp"` (Phase 0
     subset; comparisons/calls deferred).
   - Recursive sub-expression calls.

4. **Statement converter `ir_to_stmt : json_value → option stmt`**:
   - Dispatch on `json_field_get "stmt"` value.
   - Simple-subset cases (first slice):
     ```rocq
     | JsonString "Pass"      => Some SSkip
     | JsonString "Assign"    => ... extract target+value, build SAssign
     | JsonString "AugAssign" => ... build SAugAssign
     | JsonString "ArraySet"  => ... build SArraySet
     | JsonString "Return"    => ... build SReturn
     | _                      => None
     ```
   - Sequence wrapper: `ir_to_stmt_list : list json_value →
     option stmt` folds via `SSeq` right-leaning, returning `None`
     on the first failed sub-element.

5. **No semantic theorems yet** — pure converter. U.3 will prove
   `validate_ir_correspondence`; U.5 will prove
   `py_module5_emit ast = Some j → ir_to_stmt j ≠ None`.

6. **Smoke test** — add a `Phase1b_IrToStmt_Test` lemma at the end
   of the file applying `ir_to_stmt` to a hand-built `json_value`
   value for an `Assign` statement, and `Compute` the result.

### Critical files

- `src/formal-semantics/rocq/Phase1b_IrToStmt.v` (NEW)
- `src/formal-semantics/rocq/_CoqProject` (insert)
- `bin/ir-to-rocq-ast.py` (reference for dispatch structure;
  no code change)

### Risk + fallback

If `json_field_get` ends up requiring decidable equality on
`json_value` or a more elaborate option-monad threading than
expected, fall back to defining only the helpers + the empty
`ir_to_stmt` signature `Definition ir_to_stmt (_ : json_value)
: option stmt := None.` (a stub). The "sketch" goal is the
SHAPE of the file, not full converter coverage.

---

## Overall verification

After all three items complete:

```bash
# Rocq full rebuild
eval $(opam env --switch=coq-4.14)
cd src/formal-semantics/rocq
coq_makefile -f _CoqProject -o Makefile
make -j4

# Lean rebuild
cd ../lean && lake build

# Trust check — Rocq should remain zero-axiom
cat > /tmp/check.v <<'EOF'
Require Import PyCSL.Phase6m_VcgSemBridge.
Require Import PyCSL.Phase6i_Soundness.
Require Import PyCSL.Phase1b_IrToStmt.
Print Assumptions why3_implements_wp_w_derived.   (* expect: zero *)
Compute (ir_to_stmt sample_assign_ir).             (* expect: Some (SAssign ...) *)
EOF
coqc -R . PyCSL /tmp/check.v

# Lean trust check — expect why3ValidatesEmitted gone or
# replaced by single construction-site axiom
echo "#print axioms why3ImplementsWpW_derived" | lean PyCSL.lean

# Self-annotation suite stays green
bash bin/run-self-annotation-suite.sh

# Reference corpus must not regress
bash bin/run-reference-tests.sh
```

End-state metrics expected:
- Item A: Lean `why3ValidatesEmitted` eliminated or replaced
  by single construction-site axiom; cert-as-witness pattern
  in place. Lean parity with Rocq's design.
- Item B: 3 of 4 self-annotate mirrors carry formal-semantics
  citations (Module 4 may defer).
- Item C: `Phase1b_IrToStmt.v` compiles; the simple-subset
  conversion works on a hand-built test value.

---

## Sequencing rationale

Order is A → B → C:

- **A first** (Lean port): builds on the Rocq Sub-β work just
  landed. Doing it now is high-leverage parity; deferring risks
  Lean drift from Rocq.
- **B next** (citations): trivial once A is done — citations
  point at axiom-free theorems. Doing it after A means the
  Lean citation paths can also point at axiom-free results.
- **C last** (U.2 sketch): independent; can slip if A took
  longer than expected without blocking other work. Q4 is
  multi-week anyway.

<!-- LEGACY OLD PLAN (Items 4, 1, 2, 3) — superseded; removed. -->

## LEGACY: Items 4/1/2/3 (superseded)

_The detailed text of the old plan has been removed. Those four
items were executed 2026-05-29; see `friday-01.md` at the repo
root for the snapshot._

---

_See `closer-to-code.md` at repo root for the full multi-quarter
plan that this short-term sequence operates within._
