# self-tcb-reduction — full frontier triage (one-time classification)

One-time parallel classification of the entire `\trusted` frontier (8 read-only triage-probes,
each covering a subsystem). Per-stub detail: the `triage-A{1..8}.md` reports in this directory.
Purpose: replace serial pick→discover-blocked→stop churn with a global, fan-out-ranked build order.

Date: 2026-07-05. Live grep count 1260; **agent-corrected real-stub count ≈ 1215** (grep counts
include each mirror's header-docstring `\trusted` line + some dataclass-docstring mentions).

## Totals

| group (subsystem) | stubs | trivial-leaf | needs-recognizer | hard-architectural | floor |
|---|--:|--:|--:|--:|--:|
| A1 `frontend/pure_ast.py` | 261 | 0 | 3 | 258 | 0 |
| A2 `frontend/Module5_IREmitter.py` | 180 | 0 | 2 | 178 | 0 |
| A3 front-end pipeline (Parser/Weaver/Ingestor/…) | 153 | 2 | 3 | 148 | 0 |
| A4 `core_ir_semantic` + IR-resolution passes | 126 | 1 | 4 | 118 | 3 |
| A5 Module6 core (`_handle_*`, expressions/statements/functions) | 132 | 1 | 27 | 104 | 0 |
| A6 Module6 helpers (scanner/preamble/types/…) | 182 | 31 | 33 | 117 | 1 |
| A7 `proof2why3/*` + proof-audit | 132 | 4 | 8 | 119 | 0 |
| A8 `pycsl.py` driver + top-level misc | 49 | 0 | 4 | 45 | 0 |
| **TOTAL** | **≈1215** | **≈39** | **≈84** | **≈1087** | **4** |

**Shape:** ~3% free, ~7% bounded-recognizer, ~90% hard-architectural, ~0.3% floor. The hard mass
collapses onto a *few* value-modeling features, NOT per-leaf axioms — so the frontier is
feature-gated, not floor-limited.

## Ranked build order (fan-out first)

### TIER 1 — free wins (no feature; convert NOW): ~39
Biggest source **`ir_scanner.py`: 19** (bool/set IR-tree scanners — empirically `--no-proof`-clean).
Others: `stmt_control_flow` 6, `expr_ghost_collections` 3 (`_handle_map_empty/set_empty/nil_expr`
const-string), `types.py` 2, `Transpiler` 1, `proof2why3` 4 (`crosscheck._module_namespace_of` +
3 `@dataclass .pp`), front-end 2 (`Module2_Parser.__init__`, `Module1_Ingestor._clean`), core_ir 1
(`ir_inline._method_key`), Module6 core 1 (`functions._symtype_to_whyml`). Several are flagged
"uncertain" in the reports → the batch converter re-verifies each with `--no-proof` before porting.

### TIER 2 — bounded recognizer features (build + convert freed cluster), by aggregate fan-out
| # | feature | aggregate fan-out | notes |
|---|---|--:|---|
| 2a | **set/frozenset value modeling** (§5 OPEN gap #2) | ~40–50 | cross-cutting: A5 ~11, A6 ~25, A7 ~5, A8 ~4, A3 ~4; a known gap; highest leverage. **PARTIALLY LANDED:** module-const string-set membership (`x in CONST_SET`) now faithful (`collect_module_const_sets` + `_emit_membership` expansion; locks 0876/0877) — unblocks the A8 pair `is_rocq_assumption_allowed`/`is_lean_axiom_allowed`. Still open: set-VALUED returns, set-comprehension, mixed-type sets, set-local fixpoint scanners. |
| 2b | **mixed-literal f-string** (literal segments hash to int today) | ~9 primary + ~40 secondary | concentrated in Module 6 (the soundness-relevant emitter); single highest-leverage recognizer there |
| 2c | **str-list `.append` builder** | ~18 | dominates `preamble.py` |
| 2c | **record-ify plain mixin classes** (`types.py TypeInferenceMixin` → `@mutable_state @dataclass`) | 7 (one-file) | structural; also helps Preamble/AbstractOps mixins |
| — | regex modeling (`re.match/sub/compile`) | ~20 | cross-cutting but HARDER (regex engine) — defer within tier 2 |
| — | singletons (`str.startswith` ~7, module-const set membership, `\|=` set-union→`.update`) | scattered | opportunistic |

### TIER 3 — value ADT (DEFERRED; decide jointly with formal-semantics Phase 7): ~800–900
The 90% hard mass, one class of feature (recursive typed variant/record ADT + `isinstance`/`type`
dispatch + mutual recursion over heterogeneous trees):
- AST-node value ADT — `pure_ast` ~258, front-end ~148 (partial)
- `emit_ir`/`CSLNode`/IR-dict node model — Module5 ~178, core_ir ~106, Module6 ~45–55
- `Term` variant ADT + s-expr/JSON tree recursion — `proof2why3` ~77
- subprocess/filesystem/external-tool opacity (near-floor) — pycsl CLI ~24, proof2why3 ~15, ir_resolve ~3
**This is the deferred Phase-7 record/ADT model in `src/formal-semantics/` terms.** Building the
emitter recognizer WITHOUT Phase 7 would let the self-annotation verify against a construct the
meta-theory doesn't yet cover — capability outrunning its certificate. Hence: co-decide, don't
casually start. For `pure_ast`/`proof2why3` specifically, "prioritize by value" (leave trusted) is
the likely-correct call — they are peripheral to the WP-soundness LINK 1/2/3 story.

## The 4 genuine floor stubs
`core_ir`/`ir_resolve`: `_resolve_module_path`, `_get_module_exports`, `_process_dependency`
(open files + re-invoke Modules 1→5 — irreducible I/O `val`); `identifiers.stable_hash`
(hashlib.sha256 opaque). These stay `\trusted` by construction (external-dependence / D2-adjacent).
