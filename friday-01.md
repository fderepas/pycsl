# Implementation Plan — Post Q3 Sub-β Follow-On (Items 4, 1, 2, 3)

> Sequenced near-term work after Q3 Sub-β closure. Four items in
> order: (4) tighten `enrich_main_cert`, (1) Q1 close-out audit,
> (2) CC.1+CC.3 housekeeping, (3) Q4 U.1 inductive sketch.
> Working directory: `/home/fabrice.derepas@canonical.com/git/pycsl/`
> Switch: `coq-4.14` (OCaml 4.14.2).

## Context

Q3 Sub-β ports completed in the prior session. The Why3-validation
chain now has exactly one residual axiom (`enrich_main_cert` in
`Phase6m_VcgSemBridge.v`), down from two broad axioms
(`module6_encodes_mlw`, `why3_validates_emitted`).

Top-level state:
- `wp_gen_correct`, `vcg_sound`, `pycsl_soundness_verified`: zero
  axioms (modulo standard `propositional_extensionality` +
  `functional_extensionality_dep`).
- `why3_implements_wp_w_derived` (the Why3 → wp_w bridge):
  depends only on `enrich_main_cert`.
- Q1 cleanup C.1/C.2/C.3 already done (exploration confirmed —
  no Admitted in `Phase3b_Desugar.v`; no sorry in `WhileInv.lean`).
- L.1 done (`spec_no_exception` + Lean mirror).
- L.2, L.3 not started. L.4 took a different shape than the plan
  (`spec_reviewer : option string` added as a SEPARATE field;
  `spec_trusted : bool` left unchanged).

The four items below are tackled in user-specified order
(4 → 1 → 2 → 3) because Item 2's audit-plan edits depend on
Item 4's outcome.

---

## Item 4 — Tighten `enrich_main_cert`

### Problem

`enrich_main_cert` (Phase6m_VcgSemBridge.v:547) is the sole
residual axiom in the Why3-validation chain. It bridges from
the opaque sealed-`unit` `why3_certificate` (Phase6j_Why3Trust.v:45,
via `Module Type WHY3_CERT_SIG` with `Definition cert _ _ := unit`)
to the witness-carrying `enriched_why3_cert` Record (same file,
Phase6m:517).

The axiom is irreducible *in pure Rocq* because the opaque cert
carries no introspectable evidence — there is nothing to project
into the witness. The trust line is currently at this projection,
where it should be at the construction site.

### Approach — Witness-as-Cert refactor

Eliminate the indirection by making the witness type BE the cert
type. After this refactor, `why3_certificate ws Q` directly
demands a proof that every emitted VC's `eval_vc_formula` holds.
Constructing one requires the witness — which is exactly what
Why3's "Valid" verdict certifies. The `enrich_main_cert` axiom
disappears; the trust moves to wherever the cert is constructed
(in Lean's `Why3Trust.check`, when invoking Why3 externally).

The blocker is layering: the witness type references
`vc_formula_of` (Phase6m:95), `eval_vc_formula` (Phase6m:68), and
`vc_formula` (Phase6m:~30) — all currently defined *downstream*
of `Phase6j_Why3Trust.v`.

**Concrete steps:**

1. **Create `Phase6c_VcFormula.v`** (new file, slotted between
   `Phase6b_WPW.v` and `Phase6j_Why3Trust.v` in `_CoqProject`).
   Move from `Phase6m_VcgSemBridge.v`:
   - `Inductive vc_formula` and its constructors.
   - `Definition eval_vc_formula`.
   - `Definition vc_formula_of`.
   - Helper functions used by the above (`c_conj`, `c_first` —
     check Phase6m for the actual minimal set; both may already
     live in Phase6_WhyML or Phase4_WP).

   Do NOT move `vc_prop`, `emit_vc_list`, `vc_formula_of_sound`,
   `vcf_mem_emit_vc_list`, `vcf_emit_to_some`,
   `enriched_why3_cert`, `enriched_cert_validates`, etc. — these
   stay in Phase6m because they depend on `vc_prop` (which lives
   in Phase6k).

2. **Modify `Phase6j_Why3Trust.v`** (lines 36-45):
   - Replace the `Module Type WHY3_CERT_SIG` / `Module Why3Trust`
     pattern with a direct definition:
     ```rocq
     Definition why3_certificate (ws : whyml_stmt) (Q : wp_conts) : Type :=
       forall (pre_es es : exec_state) (i : nat) (f : vc_formula),
         vc_formula_of ws Q pre_es es i = Some f ->
         eval_vc_formula f es pre_es.
     ```
   - Add `Require Import Phase6c_VcFormula.`
   - The `why3_trust_check` stub (line 53) needs updating — it
     returns `None` opaquely now; with the new type, it can
     trivially return `None` of `option (why3_certificate ws Q)`
     (function type makes the option fine).

3. **Modify `Phase6m_VcgSemBridge.v`**:
   - Delete `Record enriched_why3_cert` (was lines ~517-525) and
     `Lemma enriched_cert_validates` (~531-540): no longer
     needed — `why3_certificate` IS the witness now.
   - Delete `Axiom enrich_main_cert`: GONE.
   - Replace usage in `why3_validates_emitted`,
     `why3_validates_vc_formula_b3`, `vcg_bridge_sem_b3`,
     `module6_encodes_mlw`, `vcg_bridge`: instead of
     `(enrich_main_cert ws Q Hcert)`, just apply `Hcert`
     directly (it now IS the witness — `Hcert pre_es es i f Hf`
     gives the eval_vc_formula proof).
   - Remove the `vc_formula`/`eval_vc_formula`/`vc_formula_of`
     definitions that were moved to Phase6c.

4. **Update Lean mirror**
   (`src/formal-semantics/lean/PyCSL/Why3Trust.lean` line 45+):
   - Replace the opaque `Why3Certificate` `CertImpl` structure
     with a function type matching the new Rocq definition.
   - `Why3Trust.check` (line 68) still returns
     `Option Why3Certificate`; the implementation already
     produces evidence by invoking Why3 — the type just tightens
     to demand the witness explicitly. For the immediate refactor,
     this can be left as a TODO axiom on the Lean side (the
     soundness path doesn't run through Lean in Rocq's tree).

5. **Update `_CoqProject`** to insert `Phase6c_VcFormula.v` between
   `Phase6b_WPW.v` and `Phase6j_Why3Trust.v`.

6. **Print Assumptions verification:**
   ```
   Print Assumptions why3_implements_wp_w_derived.
   ```
   Expected: `Closed under the global context` (zero axioms in
   the Why3 chain, modulo standard propext+funext for parent
   theorems).

### Critical files

- `src/formal-semantics/rocq/Phase6c_VcFormula.v` (NEW)
- `src/formal-semantics/rocq/Phase6j_Why3Trust.v` (modify cert def)
- `src/formal-semantics/rocq/Phase6m_VcgSemBridge.v` (delete enriched cert + axiom; route via cert directly)
- `src/formal-semantics/rocq/_CoqProject` (add Phase6c line)
- `src/formal-semantics/lean/PyCSL/Why3Trust.lean` (mirror)

### Risk + fallback

The Phase6c extraction may surface unexpected dependencies — if
`vc_formula_of` transitively needs symbols from Phase6k or later,
the move becomes infeasible without a larger restructure. In
that case, fall back to: **document `enrich_main_cert` as the
structurally-irreducible boundary**, write a one-page note in
`docs/glossary/` explaining why it cannot be eliminated in pure
Rocq (the Cohen & JF POPL'24 argument), and call Item 4 done at
the documentation level.

---

## Item 1 — Q1 close-out (L.2, L.3, L.4 only)

C.1/C.2/C.3 + L.1 verified done in exploration. Remaining work:

### L.2 — `allow_iteration_mutation : bool` on SFor

Add a flag field to `SFor` (currently
`Phase1_AST.v:161-162`, fields `(x : ident) (arr : ident)
(inv : contract_expr) (var : contract_expr) (body : stmt)`).

**Steps:**
- Add `(allow_iter_mut : bool)` field to `SFor` constructor.
- Mirror in `lean/PyCSL/AST.lean` `SFor` definition.
- Touch all `SFor _ _ _ _ _` pattern matches — `find . -name "*.v" -exec grep -l "SFor " {} \;` from rocq/. Add a wildcard for the new field. The WP rule for SFor doesn't use the flag (it's a transpiler-gating field per the plan), so semantic lemmas are unchanged.
- Lemma stating the field is consumed only by Module 6 emission, not by the WP calculus — single-line `Lemma SFor_allow_iter_mut_wp_irrelevant` showing wp_s for SFor doesn't depend on the flag.

### L.3 — `allow_finalizer : bool` on class records

Exploration found: NO class records exist in `Phase1_AST.v` yet.
PyCSL's formal AST doesn't model classes; the `closer-to-code.md`
plan's "Q4-class support" is its own large piece.

**Decision required:** either
- (a) Add `allow_finalizer` as a function-spec field instead
  (since `\trusted finalizer` annotations live on functions in
  the source-level AST), OR
- (b) Mark L.3 as blocked-on-class-modeling and downgrade scope.

Default plan: **(a)** — add `spec_allow_finalizer : bool` to the
function spec record in Phase1_AST.v + Lean mirror. Single-field
addition, no WP rule changes (transpiler-gating only).

### L.4 — `spec_trusted` semantics audit

Current state: `spec_trusted : bool` + `spec_reviewer : option string`
as two independent fields (Phase1_AST.v:132-133). Plan wanted
unified `spec_trusted : option REVIEWER_ID`.

**Decision required:** the current two-field design is arguably
cleaner (separates concerns: "is this trusted?" vs "who reviewed
it?"). Recommend **declaring L.4 done with a different shape**
and updating `closer-to-code.md` retroactively to match. No code
change needed — just a one-line audit-plan amendment in Item 2.

### Critical files

- `src/formal-semantics/rocq/Phase1_AST.v` (SFor + spec record)
- `src/formal-semantics/lean/PyCSL/AST.lean` (mirror)
- Any file pattern-matching SFor (find via grep)

---

## Item 2 — CC.1 + CC.3 housekeeping

### CC.1 — `audit-plan.md` amendment

Exploration found that `src/formal-semantics/audit-plan.md`
already covers Sub-α (lines 70-88, feature matrix rows 15-33,
including the α.14 composition lemma at line 77-78). Sub-β is
not named explicitly. Axioms `module6_encodes_mlw` /
`why3_validates_emitted` are referenced at lines 29, 37, 77-78
and in `docs/glossary/trusted-computing-base.md:69-72`.

**Edits:**
- In `audit-plan.md`: add a "Q3 Sub-β closure" subsection
  noting that `module6_encodes_mlw` and `why3_validates_emitted`
  have been replaced by `enrich_main_cert` (or eliminated, if
  Item 4 succeeded). Update the axiom references at lines 29,
  37, 77-78 to point to the current axiom.
- In `docs/glossary/trusted-computing-base.md`: lines 27-31
  (TCB inventory) and 69-72 (module6EncodesMlw section).
  Replace with the current state per Item 4's outcome.
- Add a one-line L.4 amendment noting the realized design
  (`spec_trusted : bool` + `spec_reviewer : option string`)
  differs from the plan's `option REVIEWER_ID`.

### CC.3 — `formula_rep` glossary entry

Add `docs/glossary/formula-rep.md` following the existing
convention (sample from `docs/glossary/loop-invariant.md:1-3`
and `trusted-computing-base.md:1-7`):

```markdown
**formula_rep** is Why3's bool-valued evaluation predicate for
closed monomorphic formulas, formalized by Cohen & Jourdan-
Fonseca (POPL '24).

---

## Why formula_rep matters in PyCSL

[1-2 paragraphs on how Q3 Sub-β uses formula_rep to bridge
from `why3_certificate` to `eval_vc_formula`, and why the
evaluational embedding (Phase6m_VcgSemBridge_Rocq9.v:98) is
sound modulo `excluded_middle_informative`.]
```

Cross-link from `theorem-prover.md` and `smt-solver.md`.

### Critical files

- `src/formal-semantics/audit-plan.md`
- `docs/glossary/trusted-computing-base.md`
- `docs/glossary/formula-rep.md` (NEW)

---

## Item 3 — Q4 U.1 (`pycsl_ir_json` Rocq inductive sketch)

Per `closer-to-code.md` Q4 U.1 — define the Rocq inductive
matching `src/pycsl/ir_schema.py:25-68`'s TypedDicts (`ContractsIR`,
`FunctionIR`, `ProgramIR`). The plan calls for 2 weeks for the
full U.1+U.2+U.3; this item is **just the inductive shape**
(1-2 days), without `ir_to_stmt` or the validate-IR
correspondence theorem.

### Approach

Create `src/formal-semantics/rocq/Phase0_IrJson.v` (slotted at
the very top of `_CoqProject`, before `Phase1_AST.v`):

```rocq
Require Import ZArith String List.

(* Generic JSON-value-shaped placeholder for unmodelled nested
   dicts. The TypedDicts use `Dict[str, Any]` for statements
   and expressions — model those as an opaque `json_value`
   for now. U.2 (later) will refine into a structured AST. *)
Inductive json_value : Type :=
  | JsonNull
  | JsonBool (b : bool)
  | JsonInt (n : Z)
  | JsonString (s : string)
  | JsonList (vs : list json_value)
  | JsonObject (kvs : list (string * json_value)).

Record contracts_ir : Type := mkContractsIR {
  ci_requires : list json_value;
  ci_ensures  : list json_value;
  ci_assigns  : list json_value;
  ci_raises   : list json_value;
  ci_no_exception : list string;
  ci_no_exception_all : bool;
}.

Record function_ir : Type := mkFunctionIR {
  fi_name : string;
  fi_symbol_table : list (string * string);
  fi_return_annotation : string;
  fi_contracts : contracts_ir;
  fi_body : list json_value;
  fi_function_variants : list json_value;
  fi_diverges : bool;
  fi_trusted : bool;
  fi_bounded_int : option Z;
  fi_pure : bool;
  fi_array2d_params : list string;
  fi_array1d_params : list string;
  fi_kind : string;
  fi_self_type : string;
}.

Record program_ir : Type := mkProgramIR {
  pi_type_decls : list json_value;
  pi_functions : list function_ir;
  pi_shared_vars : list json_value;
  pi_mutex_invariants : list (string * json_value);
  pi_thread_entries : list string;
  pi_lock_order : list string;
}.
```

This is **exactly the U.1 sketch**: structural shape only,
no semantics, no `ir_to_stmt`. The `json_value` placeholder
defers Module 5's statement/expression schema (recursively
nested dicts) to U.2.

### Critical files

- `src/formal-semantics/rocq/Phase0_IrJson.v` (NEW)
- `src/formal-semantics/rocq/_CoqProject` (insert at top)

### Verification

- `make` compiles `Phase0_IrJson.v` cleanly.
- Open the file in `coqtop` and `Check program_ir.` — confirms
  type-checks.
- Per the plan: **no semantic tests** at this stage; U.1 is
  pure-shape.

---

## Overall verification

After all four items complete:

```bash
# Rocq full rebuild
eval $(opam env --switch=coq-4.14)
cd src/formal-semantics/rocq
coq_makefile -f _CoqProject -o Makefile
make -j4

# Top-level trust check
cat > /tmp/check.v <<'EOF'
Require Import PyCSL.Phase6i_Soundness.
Require Import PyCSL.Phase6m_VcgSemBridge.
Print Assumptions why3_implements_wp_w_derived.   (* expect: zero, or only propext+funext *)
Print Assumptions wp_gen_correct.                  (* expect: zero *)
Print Assumptions pycsl_soundness_verified.        (* expect: propext + funext *)
EOF
coqc -R . PyCSL /tmp/check.v

# Lean rebuild
cd ../lean && lake build

# Self-annotation + reference corpus stay green
bash bin/run-self-annotation-suite.sh
bash bin/run-reference-tests.sh
```

End-state metrics expected:
- Item 4: zero axioms in the Why3 chain (or fallback: same
  state + docs noting irreducibility).
- Item 1: L.2 + L.3 fields land; L.4 declared done-with-
  different-shape.
- Item 2: audit-plan.md + glossary entry reflect current state.
- Item 3: `Phase0_IrJson.v` compiles; foundation for U.2 ready.

---

## Sequencing rationale

User-specified order is 4 → 1 → 2 → 3, which is sensible:

- **4 first** because Item 2's audit-plan edits depend on the
  outcome (single axiom remains? zero axioms? fallback to
  docs?). Doing 2 before 4 risks a re-edit.
- **1 next** (L.2 / L.3 / L.4) — pure AST extensions,
  zero risk of conflict with Item 4's structural changes.
- **2 third** — documentation rolls up the outcomes of 4 + 1.
- **3 last** — independent inductive definition; can slip if
  4 took longer than expected without blocking other work.

<!-- Legacy multi-quarter plan content removed below; this plan supersedes it. The full multi-quarter plan lives in closer-to-code.md at the repo root. -->

_See `closer-to-code.md` at repo root for the full multi-quarter
plan that this short-term sequence operates within._
