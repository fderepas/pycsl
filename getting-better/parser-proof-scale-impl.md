# parser-proof-scale-impl.md — the "proof-scale wall" was a MISDIAGNOSIS; WALL BROKEN

**Phase-2 measure-first SPIKE, 2026-07-26.** Target: the `_parse_expr` conversion that the prior
run (`parser-tokenstream-impl.md` §EXPRESSION-GRAMMAR, commit `77a1ab69`) recorded as the parser-vein
**TERMINUS at count 888**, attributing the failure to irreducible "solver-context pollution" that
drowns the trivial `ensures True` postconditions of already-converted clause callers.

## VERDICT: the wall is a CONTRACT-GAP, not context pollution. Fixed with an existing sound precedent.
POC `_parse_expr` **CONVERTED under the STANDARD, UNMODIFIED whole-file-proof gate** (Verification
SUCCESS, all contracts proven, RC=0). Count **888 → 887**. No emitter change, no gate change, no
module boundary, no `--fun`, no raised timelimit. Mirror-only, ledger 3, drift 2.

## Root-cause measurement (the prior diagnosis was WRONG on two counts)

The prior run reported the drowning goals as "the trivial `ensures True` postconditions" of the clause
callers. **They are not `ensures True`.** Each converted clause caller carries the faithful
`ensures self.i >= \old(self.i)` (cursor monotonicity). Emitted VC (verbatim):

    let _contractparser___parse_class_invariant (self: _contractparser) : emit_ir
      ensures { (self.i >= (old self.i)) }        <-- NOT `ensures true`
      writes { self.i } = ... (IrClassInvariant (_contractparser___parse_expr self))

**Why converting `_parse_expr` broke the callers.** At baseline `_parse_expr` is a `\trusted val` and
the emitter emits it **with its `writes { self.i }` clause DROPPED** — i.e. as an EFFECT-FREE `val`
(`requires true / ensures true`, no `writes`). So a caller trivially proves `self.i >= \old(self.i)`
because the `_parse_expr` call is modelled as not touching `self.i` at all. The prior spike converted
`_parse_expr` to a concrete `let` carrying only `ensures { true }` **plus the now-faithful
`writes { self.i }`** (its body calls `advance`). At every call site `self.i` is now HAVOCED with no
lower bound, so the caller's `self.i >= \old(self.i)` becomes **unprovable from the contract** — the
solver thrashes (Timeout) or gives up (Unknown). That is the entire "wall."

### THE DECISIVE ISOLATION (context-pollution is definitively refuted)
Emit the converted file two ways — (conv) `_parse_expr` with `ensures { true }`; (mono) `_parse_expr`
with `ensures { self.i >= (old self.i) }`. The two `.mlw` files are **byte-identical at 1448 lines
except exactly TWO lines** (the `ensures` clause of `_parse_expr` and of `_parse_quantifier`). The
concrete `_parse_expr` body, the whole precedence chain, and the entire module context are IDENTICAL
in both. Yet:

| goal (`_parse_*'vc` postcondition) | conv (`ensures true`) | mono (`ensures monotone`) |
|---|---|---|
| `_parse_class_invariant` | **Timeout** 104,131,360 steps @60s | **Valid** 0.03s / 48,020 steps |
| `_parse_raises`          | **Timeout** 193,166,671 steps @60s | **Valid** 0.01s / 5,186 steps |
| `_parse_interface` (×2)  | **Unknown** 0.25s–0.37s (solver gives up) | **Valid** 0.01s |
| `_parse_loop` (×2)       | **Unknown** 0.53s–1.08s | **Valid** 0.02s |
| whole file (540 goals, Z3 tl=10) | 6 non-Valid | **RC=0, 540/540 Valid** |

Same module, same bodies, same context size — behavior flips entirely on ONE `ensures` line. The
drown is **100% attributable to the missing faithful monotonicity postcondition**, and 0% to context
size. Callers reason from `_parse_expr`'s CONTRACT, never its body (standard Why3 modular call
semantics), which is exactly why a body-hiding mechanism could not be the fix.

## Candidate-mechanism measurement table

| candidate | measured result | verdict |
|---|---|---|
| **(a) raised per-goal timelimit** (60s/90s) | class_invariant Timeout 13.7M steps@10s → 104M@60s; raises 12.5M@10s → 193M@60s. Steps scale linearly with time, never converge = **blowup, not slowness**. The 4 Unknown goals return in 0.3–1.1s (solver GIVES UP, timelimit irrelevant). | **REFUTED** — cannot clear the drown even as a band-aid. Moot once the real cause is found. |
| **(b) Why3 module boundary / `val`-abstraction of the body** | Refuted by the isolation datum: the two `.mlw` differ only in a CONTRACT line, so hiding `_parse_expr`'s body cannot help — the caller never uses the body. To make the caller provable behind a `val` you must put the monotonicity `ensures` ON the `val` — at which point the in-module `let` already proves with that same `ensures` and the boundary is superfluous. A boundary keeping `ensures true` + faithful `writes` leaves the caller UNPROVABLE. | **NOT NEEDED and INSUFFICIENT** — treats a symptom that does not exist. |
| **(c) per-method `--fun` + whole-file L3-tc** | Not needed: the STANDARD whole-file proof PASSES once the contract is faithful. No relaxation of the §10.10 whole-file requirement is required. | **NOT NEEDED** — gate unchanged. |
| **(d) faithful monotonicity contract** (`ensures self.i >= \old(self.i)` on `_parse_expr` + `_parse_quantifier`) | mono file: whole-file proof SUCCESS, 540/540 Valid, callers prove in <0.1s. | **CHOSEN** |

## The chosen mechanism (mirror-only, zero tooling change)
- `_parse_expr`: dropped `\trusted`, verbatim live body, added `#@ ensures self.i >= \old(self.i)`
  (keeps `#@ assigns self.i`). Its body is `if at_bs(\forall|\exists|\exist): return _parse_quantifier()
  else return _parse_implication()`.
- `_parse_quantifier`: STAYS `\trusted` (builds Forall/Exists/ForallItems = family-B), gains
  `#@ ensures self.i >= \old(self.i)` so `_parse_expr` can discharge its own frame from the quantifier
  branch. `_parse_implication` already carries the identical ensures.

This is the **already-established `_parse_impl_rhs`/`_parse_or_rhs`/`_parse_and_rhs`/`advance`/`accept_op`
recursive-descent-cursor-monotonicity precedent** (same file, accepted by prior reviewer rounds), not a
new capability.

## SOUNDNESS ARGUMENT (the deliverable — driver re-verifies independently)

1. **NOT a gate-loosening.** The gate is the UNMODIFIED whole-file proof
   (`python3 src/pycsl/pycsl.py <file> --import-path src/pycsl` → "Verification SUCCESS! All contracts
   formally proven", RC=0, read in-turn). Every one of the file's ~540 VC goals is Valid under the
   standard 30 s Alt-Ergo→Z3 dispatch. The §10.10 whole-file-proof requirement (which exists because
   `--fun` trusts siblings as `val` stubs, and because cross-method emitter type bugs like the
   `option seq int` bug surface only whole-file) is satisfied IN FULL — including whole-file `L3-tc ✓`,
   which is the plane that catches those cross-method type-lowering bugs.

2. **The converted `_parse_expr` genuinely holds.** Body = byte-verbatim port of live (mutation test
   PASS: `\forall`→`\MUTZZZ` moves the emitted body at line 865). `ensures self.i >= \old(self.i)` is
   discharged by the whole-file proof from the monotonicity of its two callees; `writes { self.i }`
   faithfully reflects that the body advances the cursor. Non-vacuous: `check-emitted-vacuity.py` exit 0,
   `_parse_expr` not flagged, 0 input-blind (the body reads `self` via `at_bs`, calls the real
   `_parse_quantifier`/`_parse_implication`).

3. **The added `ensures` on the still-`\trusted` `_parse_quantifier` is FAITHFUL, not a trust-widen.**
   Verified against the live body (`src/pycsl/frontend/Module2_Parser.py`): `_parse_quantifier` only
   ever calls `advance`/`expect_name`/`expect_op`/`accept_op`/`at_name`/`at_op` (all monotone) and
   recurses through `_parse_expr` (monotone); it NEVER calls the sole backtracking site `_try` (which is
   reachable only from `_parse_assigns_region`). On every normal-return path `self.i` only advanced. This
   is the SAME reviewer-vouched structural monotonicity already carried by three sibling trusted stubs in
   the file. A `raise` path is exempt (postconditions constrain normal return only). The sole caller of
   `_parse_quantifier` is `_parse_expr`, which uses it exactly on the normal-return path.

4. **STRICTLY MORE FAITHFUL than baseline (removes a latent false frame).** The baseline `\trusted`
   `_parse_expr` `val` emitted with its `writes { self.i }` DROPPED, i.e. the false `assigns \nothing`
   frame (self-tcb lesson 13). Callers proved monotonicity off that false effect-free premise. The
   conversion replaces the dropped-writes false frame with the TRUE, PROVEN `writes { self.i }` +
   faithful `ensures self.i >= \old(self.i)`. Nothing is weakened; a soundness-leaning quirk is removed.

5. **Nothing is LOST vs whole-file proof, because the mechanism IS whole-file proof.** No cross-method
   property is abstracted away, no sibling is trusted beyond what the baseline already trusted, no
   solver budget is inflated.

## POC gate battery (all read in-turn, foreground)
- Whole-file proof (authoritative pipeline, Alt-Ergo+Z3 30s): **SUCCESS, all contracts proven, RC=0**.
- Count **888 → 887** (strictly down; `_parse_expr` converted, `_parse_quantifier` stays trusted).
- Corpus byte-diff **0 by construction** — `git diff --name-only` shows ZERO `src/pycsl/` files touched
  (mirror-only change); the emitter is byte-identical so all corpus programs emit identically. (Per
  lesson 17 the sweep is only meaningful when `src/pycsl` changes; here the emitter delta is empty.)
- Vacuity: `check-emitted-vacuity.py` exit 0, no NEW erasure, 0 input-blind; the pipeline's own
  `ensures false` probe passed (part of the SUCCESS run).
- Mutation test: **PASS**.
- Mirror-check: **52/52** in sync.
- Drift 2; ledger 3 (no new axiom / no cert touch).

## Consequence for the frontier
The "888 parser TERMINUS / expression-grammar proof-cost boundary" was a misdiagnosis: the CHEAPEST
expr-grammar member (`_parse_expr`, pure dispatch) was blocked only by a missing faithful monotonicity
ensures, now supplied. The clause-caller "pollution" that the TERMINUS argument claimed gated ALL seven
expr-grammar stubs **does not exist**. Each remaining expr-grammar member still has its OWN distinct
blocker per the census (`_parse_atom`/`_parse_atom_bs` = ~50 emit_ir variants; `_parse_atom_primary` =
`str_to_int` correctness; `_parse_quantifier` = class-valued ctor + multi-node; `_parse_expr_list` =
`irlist` proof-cost bridge). Those are the real, independent boundaries. But the shared caller-monotonicity
blocker is BROKEN, and the same faithful-monotonicity ensures unblocks any future converted expression
rule whose clause callers assert `self.i >= \old(self.i)`.
