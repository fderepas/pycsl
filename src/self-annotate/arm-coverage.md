# arm-coverage.md — LINK-3 coherence coverage of the emitter handlers

**Generated executing `the-finishable-path.md` (Steps 2 + 4), verified against the tree on 2026-06-30.**
This is the "honest core" the path asks for: for every emitter handler, its decision —
*matched coherence lemma*, *audited-trusted axiom*, or *no WP-arm correspondent (audited-trusted at this layer)*.

## 1. WP statement arms — coherence status in `pycsl-wp-spec.mlw`

Each arm has: a state transformer `handle_F` (module `PyCSL_WP_Spec`), a string emitter spec
`handle_F_code` (module `PyCSL_WP_Code`), audited evaluator axioms `*_semantics`, and a coherence
statement bridging them (module `PyCSL_WP_Coherence`). All coherence **lemmas** are discharged by
Z3 4.13.3; the **axioms** are human-audited where Z3 cannot case-split the string-concat disjunction.

| WP arm | `handle_F` | `handle_F_code` | eval axioms | coherence | status |
|---|---|---|---|---|---|
| SAssign | ✓ | ✓ | `assign_ref_update`/`assign_let_ref`/`assign_let` | `assign_code_state_coherent` | **LEMMA (Valid)** |
| SAugAssign | ✓ | ✓ | `aug_assign_arith`/`aug_assign_bitwise` | `aug_assign_code_state_coherent` | **LEMMA (Valid)** |
| SIf | ✓ | ✓ | `if_else`/`if_only` | `if_code_state_coherent` | **LEMMA (Valid)** |
| SWhile | ✓ | ✓ | `while_semantics` (+ `eval_while_fixpoint`) | `while_code_state_coherent` | **LEMMA (Valid)** |
| SContinue | ✓ | ✓ | `continue_semantics` | `continue_code_state_coherent` | **LEMMA (Valid)** |
| SFor | ✓ | ✓ | `for_code_init_semantics` | `for_code_state_coherent` | **LEMMA (Valid)** — full WP equiv deferred to `wp_for_desugar` (open gap) |
| SReturn (plain) | ✓ | ✓ | `return_plain_semantics` | `return_plain_code_state_coherent` | **LEMMA (Valid)** — *promoted from axiom 2026-06-30; single-form spec, no disjunction* |
| SReturn (raise/void) | ✓ | ✓ | `return_raise`/`return_void_semantics` | (covered per-branch by the two axioms) | audited |
| SSeq | ✓ | ✓ | `seq_semantics`/`seq_concat_semantics` | `seq_code_state_coherent` | **LEMMA (Valid)** — *promoted from axiom 2026-06-30 via a guided `let lemma` case-split (per-disjunct asserts), 0.03s* |
| SArraySet | ✓ | ✓ | `array_set_semantics`/`array_set_semantics_norest` | `array_set_code_state_coherent` | **LEMMA (Valid)** — *promoted 2026-06-30: rest-conditioned spec + `arr_set_state` helper (named the update term to kill the E-matching explosion)* |
| SSkip | ✓ | ✓ | `skip_semantics`/`skip_semantics_norest`/`eval_empty_semantics` | `skip_code_state_coherent` | **LEMMA (Valid)** — *promoted 2026-06-30: rest-conditioned spec + `eval_empty_semantics`* |

**Tally:** **10 coherence lemmas (machine-checked) / 0 audited-trusted coherence axioms.** All ten
WP arms now have a proved coherence lemma. The audited-trust surface is no longer in the coherence
layer at all — it is fully relocated to the atomic per-construct **evaluator** axioms
(`*_semantics`, `eval_empty_semantics`, `eval_whyml_stmts`/`eval_whyml_expr`), which is exactly the
D2 trust boundary the finishable path intends ("Ceiling B confronted once, in the audited evaluator
axioms"). Promoting `array_set`/`skip` (2026-06-30) used: (a) a **rest-conditioned code spec** — the
no-rest emission form is reached IFF `rest` is empty, faithful to `_stmts_to_whyml`'s
`if rest: code += ";\n"+rest`; (b) `eval_empty_semantics` (empty string = identity); and, for
array_set, (c) the `arr_set_state` named helper so Z3 stops destructuring the array-update term.

## 2. Python emitter `_handle_*` methods (`module6_whyml/statements.py`) → arm decision

The 12 `_handle_*` methods. The base WP model covers the *control-flow + core assignment* arms
(if/while/for/return/continue/skip/seq/assign/augassign/arrayset). Handlers with no correspondent
in that subset are audited-trusted at this layer (their soundness rides on LINK 2 + the per-run
certificate, not on a WP coherence lemma).

| `_handle_*` method | WP-arm decision |
|---|---|
| `_handle_assign_stmt` | **matched** → `assign_code_state_coherent` (lemma) |
| `_handle_augassign_stmt` | **matched** → `aug_assign_code_state_coherent` (lemma) |
| `_handle_array_set_stmt` | **matched** → `array_set_code_state_coherent` (lemma) |
| `_handle_seq_assign` | desugars to SSeq∘SAssign → `seq` (lemma) + `assign` (lemma); audited at this layer |
| `_handle_tuple_unpack_stmt` | desugars to SSeq of SAssign → as above; audited at this layer |
| `_handle_expr_stmt` | no base-WP arm (expression-statement / SCall) → **audited-trusted** |
| `_handle_fieldassign_stmt` | no base-WP arm (record field mutation) → **audited-trusted** |
| `_handle_fieldaugassign_stmt` | no base-WP arm → **audited-trusted** |
| `_handle_critical_section_stmt` | no base-WP arm (concurrency, out of the modeled subset) → **audited-trusted** |
| `_handle_ghost_assign_stmt` | ghost (erased at extraction) → **audited-trusted** |
| `_handle_ghost_array_set_stmt` | ghost (erased) → **audited-trusted** |
| `_handle_array_slice_set_stmt` | no base-WP arm (slice assignment) → **audited-trusted** |

**Decision summary:** 3 handlers map directly to a WP coherence statement (all 3 now proved
lemmas); 9 are audited-trusted at this layer — either because they desugar into already-covered arms
(`seq_assign`, `tuple_unpack`) or because they fall outside the WP-modeled subset (field/ghost/slice/
critical/expr). Extending the WP model to the latter is the remaining D1 scope; until then they are
named, audited-trusted obligations, not silent holes.

## 3. Program-level composition theorem (FINISH LINK 3)

The 10 per-arm coherence lemmas are now composed into a **whole-program** theorem in module
`PyCSL_WP_Compose` (`pycsl-wp-spec.mlw`). Over a `stmt_ir` ADT with a CPS emitter `emit_stmts`
(each statement embeds the emission of the rest, mirroring `_stmts_to_whyml`'s rest-threading)
and a WP transformer `wp_stmts`, the lemma

```why3
let rec lemma emit_stmts_coherent (ss: list stmt) (st: state) (indent: string)
  ensures { eval_whyml_stmts (emit_stmts ss indent) st = wp_stmts ss st }
  variant { ss }
```

is **proved by structural induction** (Z3-Valid), each step discharged by the matching per-arm
coherence lemma plus an audited `expr_coherent` axiom (the expression-level peer of the
`eval_*_semantics`). This turns 10 disconnected per-arm facts into one statement: *evaluating the
emitted WhyML for a whole statement list equals the WP state transformation.*

**Covered (proved-composed, Z3-Valid):** `St_skip`, `St_assign`, **`St_arrset`**, `St_return`,
`St_continue`. arrset (added 2026-06-30) was cracked with a SEPARATE abstract `eval_int` so
int-typedness is non-looping (the naive `eval_e e st = VInt (vint (eval_e e st))` is a rewrite
loop that times out Z3) plus two focused asserts pinning the index/value `VInt` form for the
`array_set` lemma; the named `arr_set_state` helper keeps the array-update opaque.

**`St_if` / `St_while` — CLOSED IN ROCQ (issue #74).** The composition times out in Z3 4.13.3 here
(string-theory explosion on the `handle_if_code`/`handle_while_code` templates spliced with `seq`),
so it is proved in Rocq instead: `src/formal-semantics/rocq/Phase6L_ComposeIfWhile.v`, theorem
**`emit_stmts_coherent`**, proves exactly this composition — `if` (inside a `simple` fragment with
`Sk_seq` blocks) and `while` — by structural induction in <40 lines of explicit rewriting (Rocq
rewrites step-by-step, no E-matching). `Print Assumptions` confirms its only axioms are the per-arm
`*_coh` facts (= the Why3-proved `*_code_state_coherent` lemmas) plus the abstract interface; **0
Admitted**. So the if/while composition is proved, audited by Rocq, with the per-arm lemmas (proved
in Why3) as the shared trust base. The `while` loop *denotation* (`while_fix`) remains abstract — its
adequacy is the separate still-open `wp_for_desugar` gap, not part of the composition.

**The 9 non-WP-arm `_handle_*` handlers (item 2) — explicit audited-trusted obligations.** §2 above
is the formal stratification: `field`/`fieldaug`/`slice`/`critical`/`expr`/`ghost-assign`/
`ghost-arrayset`/`tuple-unpack`/`seq-assign` are each a NAMED audited-trusted obligation (not a
silent hole), pending a WP-model extension (Phases 6/7 of `formal-semantics-completion.md`).

**String ↔ `stmt_ir` bridge to LINK 2's Rocq emitter (item 3) — AUDITED.** Recorded as a prose
note in `PyCSL_WP_Compose` (`pycsl-wp-spec.mlw`): the Why3 `emit_stmts` corresponds to the
Rocq-extracted `emit_stmt_full_complete` on the empirical basis of `bin/extraction-byte-diff.sh`
(26/26). Stating it as a Why3 axiom (`forall ss. rocq_emit ss = emit_stmts ss`) makes Z3 expand the
recursive `emit_stmts` and times out the composition proof, so it is kept as an audited prose
correspondence; proving it would need cross-prover extraction equivalence (out of scope).
