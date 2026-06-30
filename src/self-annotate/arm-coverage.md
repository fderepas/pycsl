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
| SArraySet | ✓ | ✓ | `array_set_semantics` | `array_set_code_state_coherent` | **AXIOM (audited)** — no-rest disjunct has genuinely different semantics (`eval = st`, not `eval rest st`); needs a rest-conditioned spec |
| SSkip | ✓ | ✓ | `skip_semantics`/`skip_semantics_norest` | `skip_code_state_coherent` | **AXIOM (audited)** — same: no-rest disjunct differs; not promotable without a rest-conditioned spec |

**Tally:** 8 coherence **lemmas** (machine-checked), 2 audited-trusted coherence **axioms**
(`array_set`, `skip`). The two remaining axioms are NOT a Z3 case-split limit (that was `seq`,
now promoted) — their no-rest emission disjunct has a genuinely different state semantics, so a
clean lemma needs the code spec to condition the disjunction on whether `rest` is empty (a change
that touches the byte-diff correspondence to the Python emitter). Each remains a legitimate
stratified-trust point per the path's D1 ("explicitly audited-trusted" is an allowed decision).

## 2. Python emitter `_handle_*` methods (`module6_whyml/statements.py`) → arm decision

The 12 `_handle_*` methods. The base WP model covers the *control-flow + core assignment* arms
(if/while/for/return/continue/skip/seq/assign/augassign/arrayset). Handlers with no correspondent
in that subset are audited-trusted at this layer (their soundness rides on LINK 2 + the per-run
certificate, not on a WP coherence lemma).

| `_handle_*` method | WP-arm decision |
|---|---|
| `_handle_assign_stmt` | **matched** → `assign_code_state_coherent` (lemma) |
| `_handle_augassign_stmt` | **matched** → `aug_assign_code_state_coherent` (lemma) |
| `_handle_array_set_stmt` | **matched** → `array_set_code_state_coherent` (audited axiom) |
| `_handle_seq_assign` | desugars to SSeq∘SAssign → `seq` (axiom) + `assign` (lemma); audited at this layer |
| `_handle_tuple_unpack_stmt` | desugars to SSeq of SAssign → as above; audited at this layer |
| `_handle_expr_stmt` | no base-WP arm (expression-statement / SCall) → **audited-trusted** |
| `_handle_fieldassign_stmt` | no base-WP arm (record field mutation) → **audited-trusted** |
| `_handle_fieldaugassign_stmt` | no base-WP arm → **audited-trusted** |
| `_handle_critical_section_stmt` | no base-WP arm (concurrency, out of the modeled subset) → **audited-trusted** |
| `_handle_ghost_assign_stmt` | ghost (erased at extraction) → **audited-trusted** |
| `_handle_ghost_array_set_stmt` | ghost (erased) → **audited-trusted** |
| `_handle_array_slice_set_stmt` | no base-WP arm (slice assignment) → **audited-trusted** |

**Decision summary:** 3 handlers map directly to a WP coherence statement (2 lemmas + 1 audited
axiom); 9 are audited-trusted at this layer — either because they desugar into already-covered arms
(`seq_assign`, `tuple_unpack`) or because they fall outside the WP-modeled subset (field/ghost/slice/
critical/expr). Extending the WP model to the latter is the remaining D1 scope; until then they are
named, audited-trusted obligations, not silent holes.
