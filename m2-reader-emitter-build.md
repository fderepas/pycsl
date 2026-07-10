# M2 reader-emitter build — faithful string-map readers (multi-session)

*Self-contained build plan, 2026-07-10. Converts the flat-`Dict[str,str]` reader cluster
(`_call_return_whyml_type` first) from `\trusted` to verified bodies, by generating — from the emitter —
the WhyML shape the probe (`getting-better/composition-wall/rpartition-probe.mlw`, Alt-Ergo Valid) already
proved sound. This is the M2-emitter-build the census identified: target-provable is DONE; emitter-generable
is the work. Discipline: **byte-diff 0 at EVERY phase** (the prior sprawl-attempt failed exactly here —
corpus `0887` `ref s`→`ref ""`), whole-file proofs (not just `--fun`), ledger stays 3, no gate loosening,
no un-trusted-not-gated masking. VALUE-not-count: a phase lands only if it is byte-inert AND proof-clean.*

## The failure this plan fixes (root cause)
The delegated one-shot build reached `--fun` SUCCESS (count 1228) but FAILED because supporting plumbing
was not byte-inert and was over-scoped (374 lines / 9 files):
1. a **too-broad string-local pre-decl collector** re-typed a *corpus* string-local (`0887`) → byte-diff ≠ 0;
2. **2 unprompted `@mutable_state` gate loosenings** in expressions.py (independent corpus risk);
3. **un-trusted-but-not-independently-gated** mirror methods added to reach 1228 (masking, not proof).
The fix: build each recognizer with a TIGHT mirror-only / new-shape-only gate, verify byte-diff 0 per phase,
and never loosen an existing gate.

## The pieces (from the probe + the emitter-generation analysis)
- **A1 — self-field string-dict typing** (mirror-only; VALIDATED in the spike). `@dataclass` (NOT
  `@mutable_state` — pulls emit_ir ADT, `size` two-theory collision) + `Dict[str,str]` field decls on the
  mirror `TypeInferenceMixin` → field types as `map string (option string)`. Zero live-emitter change.
- **A4 — option-`.get` → union-return mapping**. `return <mapfield>.get(k)` (single-arg) from an
  `Optional[ν]` function where the field is `map _ (option ν)` must emit
  `match Map.get recv k with Some v -> <Arm_Some> v | None -> <Arm_None> end`, NOT the lossy `| None -> 0`.
- **U — union return exception**. A union-returning function with EARLY returns needs a typed
  `Return_<union>` exception + catch — a NATURAL EXTENSION of the existing typed-return family
  (`Return_void`/`Return_str`/`Return_seq`/`Return_<arity>` in stmt_control_flow.py), NOT new machinery.
- **A3 — `str.rpartition` recognizer**. `x.rpartition(sep)` → `val str_rpartition_op (s sep: string) :
  (string, string, string)` (type-correct, NO semantics/axiom — like the existing `str_split_op`); the
  `obj,_,method = …` 3-unpack lowers with `obj`/`method` typed `string`. Corpus has **0** `.rpartition` →
  inert by construction. The unpacked string locals must pre-declare `ref ""` — gated to
  **rpartition-unpack targets ONLY** (the collector that broke `0887` was un-gated).

## Measured byte-diff risk (read-only scan, 2026-07-10 — BEFORE any code)
- **P1/U (union return exception): corpus-INERT by construction.** `grep '-> Optional[' corpus` = **0**
  files. `Return_<union>` fires only for union-returning functions; the corpus has none. And the
  typed-return-exception family ALREADY exists (`preamble.py`: `Return_seq`/`Return_seq_str`/`Return_str`/
  `Return_void`/`Return_<arity>`) — `Return_<union>` is a drop-in sibling.
- **A4 (option-return mapping): corpus-INERT by the same fact.** Gated on *returning from an `Optional[ν]`
  function* → 0 corpus sites (the 14 `return x.get(...)` corpus sites are record `.get()` (0446/0653),
  two-arg module-const (0872/0873), subscript-proj (0749), or **int**-returning `node.get(...)`
  (0878/0880) — none returns Optional).
- **A3 string-local pre-decl: THE ONLY real byte-diff risk.** The sprawl-attempt's `0887` perturbation
  (`ref s`→`ref ""`) came from an UN-GATED collector re-typing every string-assign local. MUST be gated to
  **rpartition-unpack targets ONLY** (`obj`/`method` from `x.rpartition(sep)`), never a general
  string-assign. This single narrow gate is the make-or-break for byte-diff 0.

**Consequence:** the M2 build is far safer than the sprawl suggested — the union machinery + option-return
mapping cannot touch the corpus; only the A3 string-local pre-decl needs a tight gate.

## Commit discipline (REFINED — no standalone facades)
P1/U, P2/A4, A1, A3 convert NOTHING individually (each is corpus-inert → a facade). Per the no-unused-facade
rule, they are **NOT committed as standalone commits**. Build all of {U, A4, A1, A3} in ONE working tree,
gate the WHOLE thing at the conversion, and commit ONCE as the `_call_return_whyml_type` −1. The phases
below are a **build+verify ORDER within one tree**, not a commit sequence — nothing lands until the −1 lands.

## Phases (build+verify order in ONE tree; commit once at P3; each step byte-diff-0-checked or REVERT)

- **P1 — U (union return exception).** Add `exception Return_<union> <uniontype>` to the family
  (`preamble.py` next to `Return_str`) + the `raise (Return_<union> val)` branch in
  `stmt_control_flow.py::_handle_return_stmt` (the `use_raise` path, line ~1115, reusing
  `_maybe_inject_union_return` for arm injection) + the `with Return_<union> r -> r` catch. Gated to
  union-return-type functions. NOT committed alone (corpus-inert facade).
- **P2 — A4 (option-return mapping).** The `.get`→union map at the return site, gated to the
  single-arg-`.get`-on-`map _ (option ν)`-returned-from-`Optional` shape. Corpus-inert (0 Optional fns).
  NOT committed alone.
- **P3 — A1 + A3 + convert + COMMIT.** Apply the mirror scaffold (A1, `@dataclass`-only), the rpartition
  recognizer (A3) with the **tightly-gated** string-local pre-decl (rpartition-unpack targets ONLY — the
  single byte-diff-critical gate), port the body, drop `\trusted`. Collapses the facade to a real −1.
  FULL gate battery THEN one commit: fidelity (52/52 + sync no-new-divergence), `--fun` SUCCESS, byte-diff 0
  (authoritative worktree sweep — the `0887` regressor), whole-body proof; count 1229→1228; ledger 3;
  non-vacuity (real `Map.get`/`str_rpartition_op`); mirror-side changes carry NO un-trusted-not-gated method
  (every touched mirror method is `\trusted` OR proven).
- **P4 — cluster roll (honest scope).** Re-census which cluster members convert with the now-built
  {A1,A4,U,A3}. Expected: only rpartition-using flat-`Dict[str,str]` members. `_field_type_for` /
  `_callable_tag_to_whyml` also need **nested-dict** projection; `_rhs_yields_*` also need **A2**
  (param TypedDict-view). Those are separate builds — P4 lands ONLY the members {A1,A4,U,A3} fully cover,
  one −1 per commit, each byte-diff-0 gated. No projection; measure each.

## Proof strategy (env-realistic, per SKILL §5.1 / §10.10)
Whole-file proofs of `stmt_control_flow.py`/`statements.py` can exceed the desktop timeout. Per changed
method: `--fun` (whole-body). Per file at P3 close: ONE whole-file proof (background, long timeout) as the
§10.10 sibling-interaction check — REQUIRED before commit (the sprawl-attempt skipped this). A `--fun`
SUCCESS with a whole-file FAIL means REVERT.

## Order & first action
Build order in ONE tree: **U → A4 → A1 → A3 → convert**, single commit at the end. The one dangerous gate
is A3's string-local pre-decl (rpartition-targets only); everything else is corpus-inert by measurement.
First action: **U** — add `Return_<union>` to the typed-return family (drop-in sibling of `Return_str`),
`--fun`-check the target reaches past the early-return, no commit yet.

## Non-goals / limits
- No `@mutable_state` on TypeInferenceMixin (size collision) — `@dataclass` only.
- No existing-gate loosening; no un-trusted-not-gated methods (every mirror method is `\trusted` OR proven).
- A2 (param `Dict[str,Any]`→TypedDict-view) and nested-dict readers are separate builds, not here.
- Ledger stays 3; the `val`s are uninterpreted (type-safety only), no axiom.
