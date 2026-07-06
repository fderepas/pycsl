# triage-ranked-tcb.md — the TCB-reduction plan (empirically calibrated)

Go-forward plan for driving the PyCSL self-annotation mirror's `\trusted` count toward its
irreducible floor. Ranked by a one-time full-frontier triage, then **re-calibrated by what actually
executed** (tiers 1 and 2a were run; their `--no-proof`-based fan-out estimates proved optimistic).

- **Raw per-stub data:** `getting-better/self-tcb-triage/` (aggregate `FRONTIER-TRIAGE.md` + 8 per-group reports).
- **Loop procedure & the streamlined gate:** `config/skills/self-tcb-reduction/SKILL.md` (esp. §5.1).
- **Live ledger:** `self-tcb-reduction.md` §8.

## Current state
- Branch `ghost-assign-bc6`, green: fidelity 77/77 verbatim, mirror-check 51/51, doc-coherency in sync, tree clean.
- `\trusted` count **1252** (grep-count; ≈1215 real stubs after removing docstring mentions).
- Session banked: streamlined gate, frontier map, 2 faithful-semantics features (module-const-dict `.get`, string `or`/`and`), 10 verified conversions (1262→1252).

## The frontier (one-time triage, ~1215 real stubs)
| bucket | count | meaning |
|---|--:|---|
| trivial-leaf | ~39 *(real: 8)* | free under `--no-proof`; **only 8 survived FULL proof** |
| needs-recognizer | ~84 | one bounded feature each — **but the conversion is usually tier-3-gated (see Tier 2)** |
| hard-architectural | ~1087 | the value-ADT mass (AST-node / emit_ir / Term) |
| floor | 4 | irreducible I/O + hashlib (`_resolve_module_path`, `_get_module_exports`, `_process_dependency`, `stable_hash`) |

**Shape:** ~90% is one class of feature (recursive typed variant/record ADT + isinstance/type dispatch
+ heterogeneous tree recursion) = the deferred **formal-semantics Phase 7**. The frontier is
**feature-gated, not floor-limited.**

## THE GATE (streamlined — SKILL §5.1)
Per stub (all fast): fidelity (`check-self-annotate-sync.sh` ∧ `self-annotate-mirror-check.sh`) +
prove **ONLY the changed mirror file** (files are independent verification units) + a `git diff`
mirror-only assertion (mirror isn't in the reference corpus ⇒ byte-diff 0 by construction) +
allowlist unchanged + count strictly shrank. Full suite + corpus sweep run **once per batch**, not
per stub. (~10 min/stub → ~30 s/stub, no soundness loss.)

## Ranked build order — with execution calibrations

### TIER 1 — free wins (no feature) — ✅ DONE, yield 8 (not 39)
Converted 8 (`crosscheck._module_namespace_of`, `Module2_Parser.__init__`, `Module1_Ingestor._clean`,
`ir_inline._method_key`, `Module6_WhyMLTranspiler._wrap_unannotated_call_with_strict_assert`,
`ir.py Var.pp`+`Unsupported.pp`, `stmt_control_flow._union_arm_whyml_type`). 1260→1252.
**CALIBRATION:** the triage classified trivial-leaves on `--no-proof` TYPE-CHECK; the gate is FULL
proof, and type-check-clean ≠ proof-clean. The 19-stub `ir_scanner.py` "motherlode" ALL reclassified:
13 prove per-function via `--fun` but time out in the combined file proof (recursion VCs). **Rule:
classify tier-1 on full `--fun` proof, not `--no-proof`.** Residual tier-1: the 13 `ir_scanner`
walkers are convertible via **per-function commits + a per-goal SMT-timeout bump** (a tooling tweak,
not a feature) — the one remaining genuinely-cheap batch, if desired.

### TIER 2 — bounded recognizer features — ⚠ MARKER YIELD IS TIER-3-GATED
2a (set/frozenset modeling) was built, fully gated, then **REVERTED** (`768f5392`→`5c4b87e0`). Root
cause & the decisive lesson: to convert its target cluster (the A8 `-> bool` module-const-set
membership *tail returns* `is_rocq/is_lean_axiom_allowed`), the feature had to add a bool→int bridge
to the VERIFIED emitter method `_handle_return_stmt` — and that block does **IR-node dict reflection**
(`_rr.get("name")` on a nested IR node), which hits the **emit_ir/IR-dict ADT gap** and cannot
self-verify (fails Why3 type-check in BOTH the `in` and `.get()...is not None` forms). Re-trusting = +1
regression. **Net 2a yield: 0.**

> **The generalization (why 2b/2c were not attempted):** a feature that *unblocks a `\trusted`
> conversion* must almost always touch a verified emitter method, and those methods do IR-node
> reflection = the tier-3 ADT. So the `--no-proof` fan-out numbers below overstate the *convertible*
> yield the same way tier-1's did. Tier-2 features have real value **as tool improvements for user
> programs** (faithful semantics, byte-diff 0), but their **marker-reduction value is tier-3-gated.**

| # | feature | `--no-proof` fan-out | tool value | marker value |
|---|---|--:|---|---|
| 2a | set/frozenset modeling | ~40–50 | real (condition-position membership) | **0 (tail-return conversion is ADT-gated)** |
| 2b | mixed-literal f-string | ~9 + ~40 | real | expected ADT-gated (same wall) |
| 2c | str-list `.append` builder | ~18 | real | expected ADT-gated |
| 2c | record-ify mixin classes | 7 | real | possibly convertible (structural, less IR-reflection) — the one tier-2 item worth probing |
| — | regex modeling | ~20 | real | harder; defer |

**Decision for tier 2:** build these features **on demand, when a user program needs the faithful
semantics** — NOT as a marker campaign. The single exception worth a probe is **record-ify the plain
mixin classes** (`types.py TypeInferenceMixin` → `@mutable_state @dataclass`): it's structural, not
IR-reflection-heavy, so its 7 stubs *might* convert without the full ADT — verify with a full-proof
spike before committing effort.

### TIER 3 — the value ADT (the real lever) — DECISION REQUIRED, joint with Phase 7
The ~1087 hard mass AND the tier-2 conversion enabler are the SAME feature: a recursive typed
variant/record ADT with isinstance/type dispatch and mutual recursion, covering
- AST-node value ADT — `pure_ast` ~258, front-end ~148
- `emit_ir`/`CSLNode`/IR-dict node model — Module5 ~178, core_ir ~106, Module6 ~45–55
- `Term` variant ADT + s-expr/JSON tree — `proof2why3` ~77

**This is the deferred Phase-7 record/ADT model in `src/formal-semantics/`.** By the LINK-1/2/3
architecture (see `src/formal-semantics/README.md §8.1a`): building the emitter-side ADT recognizer
WITHOUT Phase 7 would let the self-annotation verify against a construct the mechanized meta-theory
doesn't yet cover soundly — capability outrunning its certificate. **So the ADT must advance jointly:
emitter recognizer + formal-semantics Phase-7 (record-valued `val`, nested aliasing) together.**

**Prioritize by value, not count:** `pure_ast` (~258) and `proof2why3` (~130) are *peripheral* to the
WP-soundness story (LINK 1/2/3 certifies the Module-6 emitter core, not the AST reader or the Rocq/Lean
s-expr parser). Leaving those trusted is the likely-correct call. The high-value ADT target is the
**Module-6 emitter core** (~150–200 stubs: `emit_ir`/IR-dict node model), which is exactly what the
formal semantics already reasons about and what unblocks the tier-2 conversions too.

> **Tier-3 Phase-4 DECISION — both LEAVE TRUSTED (rigorous analysis: `getting-better/tier3/phase4-peripheral-decision.md`).**
> `proof2why3`: **fail-stop only, cannot false-verify** — it is *not on the runtime trust path*
> (`pycsl.py` never imports it; the verifier trusts the hand-curated `_AXIOM_REGISTRY`, anchored by
> `--audit-proof --reverify`). Strong leave-trusted. `pure_ast`: honest correction — it **can**
> false-verify *in principle* (a silent misparse ⇒ verifying the wrong program), a **distinct
> source→IR-faithfulness boundary NOT covered by the 3-axiom ledger**. Still leave-trusted, but for
> the sharper reason that **conversion would not close that gap** (self-contracts can't express
> grammar faithfulness); the load-bearing control is the CPython differential oracle (512/517
> byte-identical `ast.dump`, 0 mismatch) + fail-closed `PyCSLSyntaxError` — maintain/CI-wire that
> rather than convert the reader.

### FLOOR — 4 irreducible stubs (leave trusted, by construction)
`ir_resolve._resolve_module_path` / `_get_module_exports` / `_process_dependency` (open files +
re-invoke Modules 1→5) and `identifiers.stable_hash` (hashlib.sha256). These are D2-adjacent.

## Hard-won process rules (add to the SL discipline)
1. **Classify trivial-leaves on full `--fun` proof, never `--no-proof`** (tier-1 over-counted 5×).
2. **Any feature that edits a verified emitter method MUST re-port + re-prove that mirror method in its
   own commit** (the missing step that caused the 2a fidelity drift). If the re-port can't prove
   (IR-reflection gap), the feature is tier-3-gated — do not re-trust, do not merge a red gate.
3. **Single-writer on the working tree** — never run two mirror-editing agents concurrently
   (near-miss stash/detach race this session).
4. **Prove per file, batch the suite/sweep** (SKILL §5.1) — the mechanical slowness is solved; the
   *structural* limit is the ADT.

## Recommended path forward (in order)
1. **(optional, cheap)** Convert the 13 `ir_scanner` walkers via per-function commits + an SMT
   per-goal-timeout bump. The last genuinely-free batch. ~+13 markers.
2. **(probe)** Full-proof spike the **mixin record-ify** (2c) — if the 7 `types.py` stubs convert
   without the ADT, land it. If they too need IR-reflection, stop.
3. **(the real move)** Open the **tier-3 ADT + formal-semantics Phase-7** effort, scoped to the
   **Module-6 emitter core** first (highest soundness value, unblocks tier-2). Leave
   `pure_ast`/`proof2why3` trusted (prioritize by value).
4. Otherwise: **bank the session** — the durable wins stand and the branch is green at 1252.

## What NOT to do
- Do not chase leaf markers with `--no-proof` fan-out estimates (they overstate 3–5×).
- Do not build tier-2 features as a marker campaign (their conversions are ADT-gated).
- Do not start the emitter ADT recognizer without co-advancing formal-semantics Phase 7.
- Do not pour ADT effort into `pure_ast`/`proof2why3` (peripheral to the soundness story).
