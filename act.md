# Plan: `act` blocks — guarded contract cases in PyCSL

> **Canonical plan.** Supersedes `behaviors.md` (v1, line-oriented surface) and
> `behaviors-2.md` (v2, block surface). Self-contained — read only this.

## 1. Goal & surface

Add ACSL-style named, guarded contract cases to PyCSL's `#@` language, with a **Pythonic
block syntax**: an `act NAME:` header whose **4-space-indented** body holds the case's
clauses, plus bare `complete` / `disjoint` meta-clauses.

```python
#@ act neg:
#@     given x < 0
#@     ensures \result == -1
#@ act zero:
#@     given x == 0
#@     ensures \result == 0
#@ act pos:
#@     given x > 0
#@     ensures \result == 1
#@ complete neg, zero, pos      # the guards cover every input
#@ disjoint neg, zero, pos      # at most one guard holds at a time
def sign(x: int) -> int: ...
```

- Keywords **`act`, `given`, `complete`, `disjoint`** — all confirmed free in the grammar
  (no collisions; `given` is chosen over ACSL's `assumes` precisely to avoid the existing
  `assumes bounded_int(N)` clause, `Module2_Parser.py:638`).
- `given` = the case guard; `ensures`/`requires`/`assigns` inside an act are conditional on
  it. `complete`/`disjoint` reference acts by name.

## 2. Why (and why this shape)

A guarded case is **pure sugar** over `==>` + `\old`, which PyCSL already has — so this adds
**zero proving power** and the bar is "does it earn its surface under PyCSL's reduce-the-TCB
philosophy?" It does, for one reason: **DRY-on-guards**. Writing cases as raw
`ensures \old(g) ==> …` repeats each guard `g` across its conditional ensures, the
completeness disjunction, and every disjointness pair (`n+1` copies, growing quadratically),
with drift risk — edit one copy and the completeness check silently certifies a *different*
proposition. The `act` block writes each guard **once** (its `given`), a single source of
truth; `complete`/`disjoint` reference by name, so the checks are guaranteed to be about the
same guards. The `def`-like block also reads better than the alternatives. That DRY +
readability win is the whole justification.

## 3. Design — desugar to existing primitives

**No new IR node, no new Module5/6 *semantics*.** Each parsed `act` lowers into the
`Requires`/`Ensures` nodes that already exist, via the existing `==>` (`IMPL_OP`,
`Module2_Parser.py:762`) and `\old`:

| `act b` clause (guard `A` = conjunction of its `given`s) | Desugars to |
|---|---|
| `requires R` | `Requires( A ==> R )` |
| `ensures E`  | `Ensures( \old(A) ==> E )` — guard read in pre-state |
| `assigns …`  | guarded frame; **no-op in `hoare`** (§6) |
| `complete b1,b2,…` | `Ensures( \old(A1) \|\| \old(A2) \|\| … )` |
| `disjoint b1,b2,…` | `Ensures( not (\old(Ai) && \old(Aj)) )` for each pair |

**`complete`/`disjoint` are `ensures \old(…)` — NOT `requires`, NOT `assert`.** A `requires`
is *assumed* (an incomplete set would silently pass); PyCSL's `assert` is emitted as `()` and
never proved (`module6_whyml/statements.py:1199`). A pre-state `ensures` makes `Pre ⟹ ⋁Aᵢ`
a real VC that **fails on a gap**, with no caller obligation. **0 `\trusted` preserved.**

## 4. Implementation

### Phase 0 — Module1 folding, **contained and fail-loud** (the load-bearing phase)

Module1 is soundness-critical (it decides which contract attaches to which node) and was just
rewritten libcst-free with a byte-for-byte differential. The block surface needs comment-body
indentation, which `_clean` (`Module1_Ingestor.py:57`, `comment_text[2:].strip()`) discards.
The change is therefore **strictly contained**:

1. **Guarded path — non-`act` contracts stay byte-identical.** In `_Harvester`, after
   collecting a node's `#@` bodies, branch on a cheap presence check: does any raw body match
   `^\s*act\s+\w+:\s*$`? **If not, run the existing path unchanged** (`_clean` + flat
   `List[str]`). Only nodes that actually use `act` enter the new folder. This guarantees the
   410-file corpus and the libcst differential see *zero* behavioural change.
2. **Folder (act path only)** operates on the **raw** bodies (`c.text[2:]`, left-whitespace
   preserved), in `lineno` order. Let `c` = the body-column of `act` in the header. Each
   following body line is classified by its body-column relative to `c`:
   - `== c + 4` → a clause of this act;
   - `≤ c` → the act block ends (next top-level contract begins);
   - **anything else (`c < col < c+4`, `> c+4`, or any tab in the indentation) → hard error**
     `PyCSLSyntaxError: misindented act body (expected 4-space indent under 'act <name>')`.
     **Never silently reinterpret.** Spaces only; tabs in act-block indentation are rejected.
   The folder emits the act as **one** logical contract string `act NAME: <clause> <clause> …`
   (clauses joined, per-clause indent stripped). Because each clause starts with a reserved
   keyword (`given`/`requires`/`ensures`/`assigns`), this flat string is unambiguous — the
   grammar needs no indentation awareness.
3. **`_clean` is NOT changed globally.** The folder does its own whitespace-preserving read;
   `_clean` keeps `[2:].strip()` for every non-act line. No ripple into existing contracts.

**Regression gate for Phase 0 (mandatory, before Phase 1 merges):** re-run the libcst
differential and the full 410-corpus goldens and prove the harvest output is byte-identical
for all non-`act` files. The strict-indentation behaviours (exact-4, tabs-rejected,
under/over-indent → error) are **first-class Phase-0 tests**, not edge-case afterthoughts.

### Phase 1 — Grammar + AST nodes (`Module2_Parser.py`)

- **Nodes:** `Act(name: str, clauses: List[CSLNode])`, `Given(expr)`, `Complete(names)`,
  `Disjoint(names)`.
- **Grammar** — add to `?contract` (`:568–595`):
  ```
  act_block:    "act" CNAME ":" act_clause+
  act_clause:   given_clause | precondition | postcondition | assigns
  given_clause: "given" expr
  complete_decl: "complete" name_list
  disjoint_decl: "disjoint" name_list
  name_list:    CNAME ("," CNAME)*
  ```
  `precondition`/`postcondition`/`assigns` reused verbatim. Module1 having folded each act
  into one string ⇒ **one `Act` node per block**; grouping is intrinsic (no regrouping).
- **Transformers:** `act_block`→`Act`; `given_clause`→`Given`; meta rules→`Complete`/`Disjoint`.

### Phase 2 — Desugar + act-name attribution (`Module3_Weaver.py`)

Before the existing `isinstance` dispatch (`:57–97`), lower each `Act` and meta-clause (reuse
existing `BinOp`/`Old`/unary-not — no new expr types):
- conjoin the act's `given`s → `A`; per `requires R` append `Requires(A ==> R)`; per
  `ensures E` append `Ensures(Old(A) ==> E)`; `assigns` → §6.
- `Complete(names)` → `Ensures(Old(A1) || … || Old(An))`; `Disjoint(names)` → per pair
  `Ensures(not(And(Old(Ai), Old(Aj))))`.
- **Attribution (blunts the desugaring's diagnosability loss):** tag each synthesized node
  with the originating act, e.g. `Ensures(..., act_name="neg")`. Module6 already appends
  trailing tags to ensures (`(* linear *)`, `functions.py` `_emit_contracts`); reuse that to
  emit `(* act neg *)` on the clause so a proof failure points back to the act. **This is the
  one optional touch of Module5/6 — a comment only, no VC/semantic change.** If skipped, the
  desugar still works; attribution is purely diagnostic.
- Stash pre-desugar acts on `node.csl_acts` (for Phase 3); feed synthesized `Requires`/
  `Ensures` into the existing `csl_requires`/`csl_ensures`. **Order-preserving** (source
  order / ordered dict) — an unordered `set` reintroduces the hash-seed proof flakiness fixed
  in `module6_whyml/functions.py`.

### Phase 3 — Validation (`Module4_SemanticAnalyzer.py`)

On `node.csl_acts`: every `complete`/`disjoint` name resolves to a defined act; **a defined
act not referenced by any `complete`/`disjoint` is flagged** (catches a mistyped act name
that would otherwise become a silent stray case); no `\result` in any `given` (pre-state —
reuse the `:204–208` check); duplicate act names → error; an act with `ensures` but no
`given` ⟹ guard `True` (allow + document).

### Phase 4 — Modules 5 & 6: no semantic change

By Phase 2 the IR/WhyML see only desugared `requires`/`ensures` with `==>` and `\old`, all
supported (the sole optional addition is the `(* act X *)` comment tag, §Phase 2). **Verify
by differential:** an `act` contract must emit WhyML byte-identical to its hand-written
`ensures { (old A) -> E }` / `ensures { (old A1) || (old A2) }` twin (modulo the act-tag
comment), under `PYTHONHASHSEED=0`.

## 5. Worked example

`sign` (§1) desugars to:
```python
#@ ensures \old(x < 0)  ==> \result == -1            # (* act neg *)
#@ ensures \old(x == 0) ==> \result == 0             # (* act zero *)
#@ ensures \old(x > 0)  ==> \result == 1             # (* act pos *)
#@ ensures \old(x < 0) || \old(x == 0) || \old(x > 0)        # complete
#@ ensures !(\old(x < 0) && \old(x == 0))                    # disjoint  (n·(n-1)/2 pairs)
#@ ensures !(\old(x < 0) && \old(x > 0))
#@ ensures !(\old(x == 0) && \old(x > 0))
```
The `complete`/`disjoint` ensures reference only pre-state ⇒ each VC reduces to `Pre ⟹ …`:
proved by the function, failing on gap/overlap, no caller obligation. Each guard appears
**once in source**; the desugared duplication is machine-generated (no drift) — the DRY win.

## 6. Per-act `assigns` (the one wrinkle)

`hoare` model emits no frame condition (`module6_whyml/statements.py:1238–1272`), so per-act
`assigns` is a no-op there — accept and ignore in v1. Typed/store guarded frames
(`given ==> region-exclusion`) are deferred behind a clear "act assigns unsupported in
<model> model" diagnostic.

## 7. Test plan

1. **Phase-0 folding (first-class):** correct grouping; **exact-4 enforced**; tabs rejected;
   under-/over-indent → hard error; `act` with no body; interleaving with plain clauses; CRLF.
2. **Phase-0 regression gate:** libcst differential + 410-corpus goldens byte-identical for
   all non-`act` files (proves containment).
3. **Parser:** `act_block`→one `Act` with its clauses; `complete`/`disjoint` parse.
4. **Desugar:** synthesized `Requires`/`Ensures` AST equals the hand-written `==>`/`\old`
   twin (structural equality); attribution tag present.
5. **WhyML differential:** byte-identical to the hand-desugared twin (modulo `(* act X *)`),
   `PYTHONHASHSEED=0`.
6. **End-to-end:** `pycsl --proof` closes the demos; a **negative** case — an `act` set that
   is *not* exhaustive — must make the completeness VC **fail** (teeth).

### Reference corpus (required for any feature)

Add to `test-suite/corpus/pycsl-reference/` (NNNN.py + golden NNNN.mlw): the `sign` example
(complete+disjoint, provable); an act with a global `requires` + two cases; and a
deliberately **incomplete** act set marked xfail showing the completeness VC failing.
Re-baseline the SY3 (`src/pycsl`) cmmi mod-index if def counts shift.

## 8. Documentation

Update `config/skills/pycsl-annotate/SKILL.md` **and** the five doc-coherency surfaces — the
new `act`/`given`/`complete`/`disjoint` directives must pass `bin/doc-coherency.py --check`
(`test-suite/annotations.md` canonical + README + the three `docs/*reference.md`). Document:
the block syntax + the strict 4-space indentation rule, the desugaring semantics (guard is
pre-state for `ensures`), the `hoare`-model `assigns` limit, and the **normal-return caveat**
below. Note the reserved words.

## 9. Risks (with mitigations now built in)

1. **Module1 containment** — mitigated by the guarded `act`-presence branch + the Phase-0
   regression gate (non-`act` path byte-identical, differential + goldens prove it). *If
   containment can't be kept clean, that's the signal to reconsider a non-whitespace block
   delimiter.*
2. **Significant whitespace** — mitigated by strict, fail-loud indentation (exact-4,
   spaces-only, errors never silent) as first-class tests.
3. **Normal-return-only completeness (documented limitation, not fixed in v1).** A WhyML
   `ensures` is checked only on normal return; PyCSL has first-class `raises … when …`
   (`Module2_Parser.py:623`), so for inputs that always raise, the `complete`/`disjoint`
   `ensures` is **vacuously true** — weaker than ACSL's pre-state obligation. Documented in
   §8; a stronger discharge (on a path exceptions can't skip) is a possible follow-up.
4. **Diagnosability** — blunted by the optional act-name attribution comment (§Phase 2).
5. **Determinism** — order-preserving bucketing (§Phase 2).
6. **Formal-semantics mirrors** — desugaring to existing nodes ⇒ no new Rocq/Lean AST
   constructors; confirm the self-annotate cross-check gate stays green.

## 10. Scope

Front-end is the bulk: **Module1 folding (contained, new)** + Module2 grammar/nodes/
transformers + Module3 desugar (+ optional attribution) + Module4 checks. Back half: zero
semantic change (only the optional `(* act X *)` comment). Plus corpus demos + docs across
five surfaces. No new dependency, no new IR schema, **0 `\trusted`**. The single highest-value
guardrail is the Phase-0 containment + regression gate — do it first.
