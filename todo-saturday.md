# Saturday TODO — and the multi-week trail beyond

Plan for the four open items left over from the
`closer-to-code.md` close-out (item 64). Ordered **smallest
effort first** so saturday actually makes a dent.

| # | Item | Effort | Day-1 deliverable |
|---|------|--------|--------------------|
| 4 | Status-doc consolidation + index | 0.5 day | `closer-to-code-execution-status-index.md` |
| 2 | Manual `Expr.decEq` in Lean | 1 day | Real DecidableEq instance + updated Module 4 citation |
| 3 | `proof2why3 emit` — registry auto-gen | 2-3 days | `bin/proof2why3-emit.py` + Makefile target |
| 1 | Q4 corpus residue (8 categories) | 4-6 weeks | One sub-item per day; smallest first |

The first three items together fit a long saturday + 2-3
follow-on days. Item 1 is the multi-week tail.

---

## Item 4 — Status-doc consolidation + index (0.5 day, do first)

### Context

`closer-to-code-execution-status.md` is 64 items, ~2600 lines.
Future maintainers reading it need a jump-table. A consolidated
index gives that without rewriting the ledger.

### Approach

**New file** `closer-to-code-execution-status-index.md` —
one-line entry per item:

```markdown
# Execution-status index

A reading guide for the 64-item ledger at
`closer-to-code-execution-status.md`. Items grouped by
program area. Click an item to jump to its full entry in
the main ledger.

## Q1 — Lateral + Cleanup
- [Item 1](closer-to-code-execution-status.md#1) — L.1 Add spec_no_exception
- [Item 2](closer-to-code-execution-status.md#2) — L.2 Add allow_iter_mut
- …

## Q2 — Sub-α per-construct emit_stmt
- [Item 15](#) — α.1 wSkip pilot
- [Item 16](#) — α.2 wAssign full state coverage
- …

## Q3 — Sub-β Why3 formula semantics
- [Item 21](#) — Phase 4 c_let_ghost / formula_rep import
- …

## Q4 — Upward chain (Module 5 IR ↔ formal stmt)
- …

## CC (cross-cutting) + Sticky-01/02 + post-status
- …
```

The full URLs are not strictly necessary — a section list with
item numbers + one-line summaries is enough.

### Critical files

- **New**: `closer-to-code-execution-status-index.md` —
  ~150 lines markdown.
- **Modified**: `closer-to-code-execution-status.md` —
  add an "Index" pointer paragraph near the top.

### Verification

```bash
# Index lists exactly 64 items.
grep -cE "^- \[Item" closer-to-code-execution-status-index.md
# Expect: 64.

# Every item number in the ledger appears in the index.
grep -oE "^[0-9]+\." closer-to-code-execution-status.md | sort -u | wc -l
# Expect: 64; cross-check with the index count.
```

### Risk + fallback

- Pure documentation deliverable; zero code change. No risk.
- The full URLs to specific anchors don't render unless the
  hosting platform supports them. Inline item numbers are
  robust against this.

---

## Item 2 — Manual `Expr.decEq` in Lean (1 day)

### Context

When `Expr.call (func : Ident) (args : List Expr)` was added to
`src/formal-semantics/lean/PyCSL/AST.lean:25` (Q4 U.4), Lean's
`deriving DecidableEq` failed: the synthesis handler doesn't
descend into nested `List Expr` to lift a recursive
`DecidableEq Expr` instance through `List`.

`PyCSL.AST.Expr.decEq` therefore doesn't exist. Module 4's Lean
citation (`src/self-annotate/src/Module4_SemanticAnalyzer.py:3`)
points at `PyCSL.AST.Expr` — the inductive type itself, as a
namespace-presence anchor — not at a real DecidableEq instance.

This is **cosmetic**: the Rocq side has the real
`expr_eq_dec` (via `list_eq_dec expr_eq_dec`); the Lean side
has the type but not the decidability. Upgrading gives Lean
parity with Rocq.

### Approach

Write the recursion manually. The standard Lean 4 pattern uses
*mutual recursion* between `Expr.decEq` and the helper
`decEqList : DecidableEq (List Expr)`, OR a unified `decEq`
that pattern-matches on both via `Expr` and lists embedded.

The cleanest form:

```lean
namespace PyCSL.AST

mutual

protected def Expr.decEq : DecidableEq Expr
  | .int n,        .int m        => decEq n m |>.map (· ▸ rfl) (· ∘ Expr.int.inj)
  | .var x,        .var y        => decEq x y |>.map (· ▸ rfl) (· ∘ Expr.var.inj)
  | .subscript a i, .subscript b j => …
  | .len a,        .len b        => …
  | .binop op e1 e2, .binop op' e1' e2' => …
  | .neg e,        .neg e'       => …
  | .cmp op e1 e2, .cmp op' e1' e2' => …
  | .fieldGet o f, .fieldGet o' f' => …
  | .call f args,  .call f' args' =>
      match decEq f f', Expr.decEqList args args' with
      | .isTrue hf, .isTrue ha => .isTrue (hf ▸ ha ▸ rfl)
      | _,           _         => .isFalse (by …)
  | _, _ => .isFalse (by intro h; cases h)

protected def Expr.decEqList : DecidableEq (List Expr)
  | [],       []      => .isTrue rfl
  | a :: as,  b :: bs =>
      match Expr.decEq a b, Expr.decEqList as bs with
      | .isTrue h1, .isTrue h2 => .isTrue (h1 ▸ h2 ▸ rfl)
      | _,           _          => .isFalse (by intro h; injection h …)
  | _, _ => .isFalse (by intro h; cases h)

end

instance : DecidableEq Expr := Expr.decEq

end PyCSL.AST
```

Then update the citation:

```python
# src/self-annotate/src/Module4_SemanticAnalyzer.py:3
#@ proof lean PyCSL.AST.Expr.decEq    ← was: PyCSL.AST.Expr
```

And update the audit-anchor stub at
`src/self-annotate/src/Module4_SemanticAnalyzer.proofs/lean/AST.lean`
to wrap a `decEq` declaration inside `namespace PyCSL.AST` so
the namespace-aware audit parser finds it.

### Critical files

- **Modified**: `src/formal-semantics/lean/PyCSL/AST.lean` —
  add the mutual recursion block + instance.
- **Modified**: `src/self-annotate/src/Module4_SemanticAnalyzer.py`
  line 3 — update citation qualname.
- **Modified**:
  `src/self-annotate/src/Module4_SemanticAnalyzer.proofs/lean/AST.lean`
  — audit-anchor stub now wraps a `decEq` symbol.

### Verification

```bash
# Lean rebuild — no sorry on Expr.decEq.
cd src/formal-semantics/lean && lake build

# #print axioms verifies the assumption set is allow-listed.
echo '#print axioms PyCSL.AST.Expr.decEq' | \
    lake env lean --stdin
# Expect: propext / Classical.choice / Quot.sound only.

# Audit accepts the new citation.
source ../../../.venv/bin/activate
python ../../../src/pycsl/pycsl.py --audit-proof \
    ../../../src/self-annotate/src/Module4_SemanticAnalyzer.py
# Expect: Module 4 citation passes.

# Cross-check via the IR pipeline (sanity — no regression).
PROOF2WHY3_USE_LEAN_META=1 python -m pycsl.proof2why3.crosscheck_ir \
    src/self-annotate/src/Module4_SemanticAnalyzer.py
# Expect: 1 SKIP (registry-not-cited; audit-anchor stub),
# rocq==lean PASS via the new decEq.

# Self-annotation suite stays green.
bash bin/run-self-annotation-suite.sh
# Expect: 26/26 PROVED.
```

### Risk + fallback

- **Mutual recursion termination check**: Lean's
  decreasing-measure inference might trip on the nested
  `decEqList`. Mitigation: add explicit `termination_by` hints
  on the structural measure (e.g., `e.size + args.size`).
- **Mathlib dependency**: the manual `decEq` is pure Lean
  core; no Mathlib needed. Confirm the existing
  `lakefile.lean` doesn't require Mathlib for this.

### CC.4 audit-anchor stub update

The Module 4 lean stub currently declares
`namespace PyCSL.AST` with `inductive Expr` as the anchor. After
this work it should declare `decEq` as a `def` symbol so the
audit's namespace-aware parser finds the new qualname.
The wrap is ~5 additional lines in the stub file.

---

## Item 3 — `proof2why3 emit` — auto-generate `_AXIOM_REGISTRY` (2-3 days)

### Context

`_AXIOM_REGISTRY` in `src/pycsl/module6_whyml/preamble.py:18` is
the hand-curated dict mapping qualnames → WhyML axiom bodies
that Module 6 splices into the preamble. The cross-check
(`proof2why3.crosscheck_ir`) verifies registry-vs-prover
agreement on every `make` run — but the registry itself is
still human-authored.

`proof2why3 emit` closes the loop: given a cited qualname,
extract the elaborated theorem from Rocq+Lean, canonicalize
both, project the canonical IR to a WhyML axiom-body string,
and emit it. The registry becomes a *cache* (generated from
proofs) rather than a *source* (hand-edited).

### Approach

**New file** `src/pycsl/proof2why3/emit_why3.py`:

```python
def ir_to_whyml_axiom_body(term: Term) -> str:
    """Project a canonicalized first-order IR Term back into the
    WhyML axiom-body subset that the Module 6 preamble expects.

    Inverse of the registry-side parser in proof2why3/parser.py
    on the round-trip-supported subset (Forall over int, BinOp
    arithmetic + comparison, App for gcd/mod/…). For shapes
    that don't round-trip (predicate Foralls, higher-order
    quantification, …) emits a structured `<<UNSUPPORTED:…>>`
    string so the caller knows to fall back to hand-curation.
    """
    …
```

**New CLI** `bin/proof2why3-emit.py`:

```bash
# Per-qualname: emit a registry body from cross-checked IR.
python bin/proof2why3-emit.py <py_file>
# Output: a dict literal suitable for pasting into
# `_AXIOM_REGISTRY`, with each qualname's body derived
# mechanically from the Rocq+Lean theorems.
```

**Makefile integration**:

```makefile
.PHONY: sync-axiom-registry
sync-axiom-registry: .venv
    @echo "=== Regenerating _AXIOM_REGISTRY from cross-checked IR ==="
    @for f in test-suite/corpus/pycsl-reference/*.py; do
        grep -q "^#@ proof " "$f" || continue
        python bin/proof2why3-emit.py "$f" \
            >> /tmp/proof2why3-registry-fragments.txt
    done
    @python bin/proof2why3-merge-registry.py \
        src/pycsl/module6_whyml/preamble.py \
        /tmp/proof2why3-registry-fragments.txt
    @echo "=== Done. Re-run make self-annotate-verify. ==="
```

**Registry header marker**:

```python
# src/pycsl/module6_whyml/preamble.py
_AXIOM_REGISTRY: Dict[str, str] = {
    # ============================================================
    # AUTO-GENERATED via `make sync-axiom-registry`.
    # Do NOT edit entries by hand. The cross-check at
    # `make self-annotate-verify` enforces registry-vs-prover
    # agreement; manual edits will be reverted on the next
    # regeneration.
    # ============================================================
    "Pycsl.Reference.Gcd.gcd_step": "forall a b : int. …",
    …
```

### Critical files

- **New**: `src/pycsl/proof2why3/emit_why3.py` — IR → WhyML
  serializer.
- **New**: `bin/proof2why3-emit.py` — per-file CLI.
- **New**: `bin/proof2why3-merge-registry.py` — splices the
  auto-generated dict back into `preamble.py`.
- **Modified**: `src/pycsl/module6_whyml/preamble.py` — add
  the AUTO-GENERATED header marker.
- **Modified**: `Makefile` — add `sync-axiom-registry` target.

### Verification

```bash
# Regenerate registry; should produce byte-identical content
# to what's already there (the cross-check has already
# verified agreement).
make sync-axiom-registry
git diff src/pycsl/module6_whyml/preamble.py
# Expect: no diff. Idempotency confirmed.

# Cross-check still 14 PASS / 8 SKIP / 0 FAIL.
make check-proof-crosscheck

# Negative test: corrupt the registry, regenerate, expect the
# corruption to be overwritten.
sed -i 's|gcd a 0 = a|gcd a 0 = a + 1|' \
    src/pycsl/module6_whyml/preamble.py
make sync-axiom-registry
grep "gcd a 0 = a" src/pycsl/module6_whyml/preamble.py
# Expect: gcd_0 = "forall a : int. a >= 0 -> gcd a 0 = a" (restored).
```

### Risk + fallback

- **IR → WhyML serializer asymmetry**: `parser.py` (WhyML →
  IR) is well-tested; `emit_why3.py` (IR → WhyML) is new and
  may produce a string that round-trips through the parser to
  a DIFFERENT Term than the input. Mitigation: round-trip test
  every regenerated entry (`ir_to_whyml_axiom_body(t)` →
  `parse(…)` → check structural equality with `t`).
- **Lossy canonicalization**: alpha-renamed vars in canonical
  IR become `v0`/`v1`/… — readable but not the original `a`/`b`
  names. Acceptable since the registry is auto-generated; users
  read the upstream Rocq/Lean theorems, not the registry.
- **What to do with non-round-trippable shapes**: predicate
  quantification (`wp_gen_correct` style) can't be expressed
  as a WhyML axiom directly. The emit step should
  detect+report and leave the existing entry intact (don't
  overwrite with garbage).

---

## Item 1 — Q4 corpus residue (4-6 weeks; smallest sub-items first)

### Context

`bin/extraction-byte-diff-upward.sh` on
`test-suite/corpus/pycsl-reference/*.py` (386 files) reports:

- **PASS**: 346/386 (89.6%)
- **SKIP**: 24/386 — outside the formal `ir_to_stmt` subset
- **FAIL_M5**: 16/386 — Module 5 itself can't produce IR

The 24 SKIP cases break down per `blocker:` tag in the driver
output. Eight categories surfaced in the analysis (item 52 in
the status doc):

| # | Category | Effort | Plan ref |
|---|----------|--------|----------|
| 1.1 | 3-arg `range(start, stop, step)` desugar | ~1 day | Phase1b_IrToStmt's For case (already handles 1-arg + 2-arg) |
| 1.2 | `CGStrSub` contract atom | ~1 day | Phase1_AST.v + Phase1b_IrToStmt + Lean mirror |
| 1.3 | `EChainedSubscript` at expr level | ~2 days | parallel to existing CChainedSubscript |
| 1.4 | `ESlice` at expr level | ~2 days | parallel to CSlice |
| 1.5 | `SGhostArraySet` stmt | ~2 days | Phase1_AST constructor + WP rule + soundness arm |
| 1.6 | `MkTuple` / tuple literal at expr level | ~2 days | needs list-of-expr handling in eval_expr |
| 1.7 | `match-case` (SMatch + pattern inductive) | ~5-10 days | new `pattern` inductive + SOS + WP rule |
| 1.8 | Lambda (closure model) | multi-week | no closure model in formal expr; needs heap discipline rethink |

**Strategy**: smallest first. 1.1 and 1.2 are 1-day each and
unblock specific test files. 1.3-1.6 are 2-day each. 1.7
(match-case) is 1-2 weeks. 1.8 (lambda) is multi-week — defer.

### Approach per sub-item

Each sub-item follows the same shape:

1. **Pick a corpus test** that triggers the blocker (e.g.
   `bin/extraction-byte-diff-upward.sh 2>&1 | grep blocker:<Type>`).
2. **Extend the formal AST** in `Phase1_AST.v` + Lean mirror.
3. **Extend `ir_to_stmt`** in `Phase1b_IrToStmt.v` to recognize
   the IR shape Module 5 emits.
4. **Extend `stmt_to_ir_simple`** in `Phase1d_StmtToIr.v` and
   add a round-trip Example (proved by `reflexivity`).
5. **Update Lean mirror** (`AST.lean`, plus per-case projector
   in `from_lean_json.py` if Phase A/B extractors need to
   handle the new shape).
6. **Update the audit-plan.md feature row** with the new
   theorem reference.
7. **Run the byte-diff** to confirm the test file's blocker
   resolves; corpus PASS count increases by ~3-6 (related tests
   share the shape).

### Suggested sequencing

Saturday: 1.1 + 1.2 (each ~1 day; budget overflow OK).
Sunday + Monday: 1.3 + 1.4 (chained subscript + slice; the
contract analogues already exist as templates).
Tuesday + Wednesday: 1.5 + 1.6 (ghost array set + tuple expr).
Following week: 1.7 match-case (multi-day, requires new
inductive).
Defer: 1.8 lambda (its own dedicated work item; multi-week).

After 1.1-1.6 land, expected corpus PASS rate: ~360-370 / 386
(94-96%). After 1.7 lands: ~375-380 / 386 (97-98%). Lambda is
the only path to >98%.

### Critical files (per sub-item)

The pattern is:

- `src/formal-semantics/rocq/Phase1_AST.v` — new constructor.
- `src/formal-semantics/rocq/Phase2_State.v` — eval arm
  (for expressions) or SOS rule (for statements).
- `src/formal-semantics/rocq/Phase1b_IrToStmt.v` —
  `ir_to_stmt` case for the new IR tag.
- `src/formal-semantics/rocq/Phase1d_StmtToIr.v` — encoder
  case + round-trip Example.
- `src/formal-semantics/lean/PyCSL/{AST,State}.lean` — Lean
  mirror.
- `src/formal-semantics/audit-plan.md` — feature row update.
- `bin/ir-to-rocq-ast.py` — Python-side IR translator
  extension.

### Verification (per sub-item)

```bash
# Round-trip lemma passes by reflexivity.
make Phase1d_StmtToIr.vo
# Expect: clean compile, no Admitted.

# Print Assumptions on the new round-trip Example.
echo 'Require Import PyCSL.Phase1d_StmtToIr.
      Print Assumptions roundtrip_<new_case>.' | coqc -R . PyCSL /dev/stdin
# Expect: Closed under the global context.

# Byte-diff: the target test file moves from blocker → PASS.
bash bin/extraction-byte-diff-upward.sh test-suite/corpus/pycsl-reference/
# Expect: PASS count increases by N (N = tests sharing the shape).

# Self-annotation suite + cross-check stay green.
bash bin/run-self-annotation-suite.sh
make self-annotate-verify
```

### Risk + fallback

- **Each sub-item is independent**. A failure on 1.5
  (SGhostArraySet) doesn't block 1.4 (ESlice). Pick the next
  smallest if one stalls.
- **1.7 match-case is genuinely multi-day**. Don't start it
  on saturday afternoon. Treat it as a focused 1-week effort
  in a dedicated session.
- **1.8 lambda is multi-week and may require AST restructuring**.
  Defer until 1.1-1.7 ship and the AST is otherwise stable.

---

## Cross-cutting verification

After saturday's work (Items 4 + 2; possibly 3):

```bash
# Glossary + audit-plan unchanged from the close-out pass.
ls docs/glossary/{extraction-extensional-residue,formula-rep,ir-well-formedness,trust-seam,trusted-computing-base}.md

# Status doc index points back at the ledger.
head -20 closer-to-code-execution-status-index.md

# Self-annotation suite + reference + cross-check.
bash bin/run-self-annotation-suite.sh    # 26/26 PROVED
make self-annotate-verify                # 14 PASS / 8 SKIP / 0 FAIL
bash bin/run-reference-tests.sh --pycsl --start-at 342 --stop-at 342
```

After each Q4 corpus sub-item:

```bash
# Byte-diff PASS rate climbing monotonically.
bash bin/extraction-byte-diff-upward.sh test-suite/corpus/pycsl-reference/ | tail -5
# Track the PASS count; expect monotonic increase.
```

---

## Sequencing rationale

- **Item 4 first** — pure documentation; lowest risk; biggest
  ROI on future readers.
- **Item 2 next** — cosmetic but visible; closes the Lean
  side of CC.4 Module 4 citation; ~1 day.
- **Item 3 next** — closes the registry-as-cache loop; the
  cross-check architecture's final piece.
- **Item 1 last** — multi-week; pick sub-items as time
  permits; smallest first.

Total saturday throughput target: **Items 4 + 2 + start of 3**.
Items 3 finish + first 2-3 sub-items of 1 carry into Sunday +
following week.

---

_See `closer-to-code.md` for the multi-quarter program plan,
`closer-to-code-execution-status.md` items 1-64 for the
execution log, and `self-annot-2.md` "What's left" §8 for
the original framing of these four items._
