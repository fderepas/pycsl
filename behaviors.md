# Plan: ACSL-style `behaviors` in PyCSL

## 1. Goal

Add ACSL's **named behaviors** to PyCSL's `#@` contract language: a way to split a
function contract into named, guarded cases, plus the `complete behaviors` and
`disjoint behaviors` meta-clauses.

ACSL reference (see also the conceptual explanation given earlier in this session):

```c
/*@ behavior positive:
      assumes *p > 0;
      ensures \result == *p + 1;
    behavior nonpositive:
      assumes *p <= 0;
      ensures \result == 0;
    complete behaviors;
    disjoint behaviors;
*/
```

Semantics: a behavior's `ensures E` is **not** an unconditional promise — it means
`assumes A` (evaluated in the **pre-state**) ⟹ `E`. `complete` asserts the guards cover
every input; `disjoint` asserts at most one guard is true at a time.

## 2. Key design decision — **desugar, don't add a first-class IR node**

The two exploration passes over the pipeline surfaced one decisive fact the initial
analysis missed: **PyCSL already has an implication operator.**

- `Module2_Parser.py:762` — `IMPL_OP: "==>" | "<==>"`
- `module6_whyml/identifiers.py:11` — `"==>": "->"` (WhyML implication), `"<==>": "<->"`
- `\old(...)` / `@PRE` already lower to WhyML `(old e)`
  (`module6_whyml/expressions.py:950–978`).

Therefore a behavior needs **no new IR container, no new Module5/6 emission**. It lowers
entirely into the `Requires`/`Ensures` nodes that already exist — the per-behavior clauses
*and* the `complete`/`disjoint` meta-clauses (the latter as pre-state `ensures`, see ⚠):

| Behavior `b` clause (guard `A`) | Desugars to |
|---|---|
| `assumes A` + `requires R` | `Requires( A ==> R )` |
| `assumes A` + `ensures E`  | `Ensures( \old(A) ==> E )`  ← guard read in pre-state |
| `assumes A` + `assigns …`  | guarded frame (see §6 — no-op in `hoare` model) |
| `complete behaviors b1,b2` | `Ensures( \old(A1) \|\| \old(A2) )` (proof goal, see ⚠ below) |
| `disjoint behaviors b1,b2` | `Ensures( not (\old(Ai) && \old(Aj)) )` per pair |

> ⚠ **Two corrections, both forced by cross-checking the ACSL skill + the PyCSL source.**
>
> *(1) Not `requires`.* In ACSL, `complete`/`disjoint behaviors` are **proof obligations** —
> the tool proves *"under the precondition, the guards cover every case / never overlap"*
> (skill `acsl-reference.md` §3: *"asserts the guards cover every case reachable under the
> precondition"*). A `requires` is the opposite — a **caller obligation** that is *assumed*
> inside the body, never proved — so it would silently strengthen the contract **and** let
> an incomplete set **pass** (contradicting the §7 negative test).
>
> *(2) Not `assert` either.* A natural fix would be a function-entry `assert`, but **PyCSL's
> `assert` is not a proof obligation** — the Python `assert` statement is emitted as `()`
> (a no-op) and skipped by the prover (`module6_whyml/statements.py:1199–1200`: *"Python
> assert statements are runtime checks, not proof obligations"*); there is no `#@ assert`
> contract clause. An assert here would be **silently discarded** — no teeth.
>
> *The correct primitive is `ensures` over `\old` guards.* `complete`/`disjoint` are pure
> **pre-state** predicates, so `ensures \old(A1) || \old(A2)` generates exactly the VC
> `Pre ⟹ (A1 ∨ A2)` (the body cannot change `\old` values), is **proved by the function**
> (so it *fails* on a gap — teeth), and imposes **no** caller obligation. This also keeps the
> pure-desugar thesis intact: everything lowers to `Requires`/`Ensures`, no body injection,
> no new emission. (Per-behavior `requires`/`ensures` — rows 1–2 — were verified *correct*
> against the skill, including the `\old`-guard for `ensures`, which the `clamp` example
> confirms is pre-state.)

This keeps the `#@ \abstract` philosophy: introduce the surface construct, lower it to
primitives the verifier already trusts, keep **0 `\trusted`**. Modules 4/5/6 are touched
only minimally (validation + already-supported emission). It is the lowest-risk design.

**Rejected alternative:** a first-class `Behavior` node threaded through IR → WhyML
(emit `requires`/`ensures` per behavior directly). More faithful to ACSL's structure, but
multiplies surface area across Module5 (IR schema), Module6 (emission), the Rocq/Lean
formal-semantics mirrors, and the differential corpus — for zero added proving power over
the desugaring. Defer unless behaviors must round-trip back to source verbatim.

## 3. Surface syntax — **line-oriented**, to fit the one-`#@`-line-per-contract model

`Module2_Parser.parse_node_contracts` parses **each `#@` line independently**
(`Module2_Parser.py:963–981`); Module1 harvests them as an ordered `List[str]`
(`Module1_Ingestor.py:23–29`, `PyCSLContract.contracts`). A multi-line `behavior { … }`
block would require new stateful line-grouping in Module1. To stay architecturally
aligned, each clause is its own line, tagged with its behavior name:

```python
#@ requires \valid(p)                 # global precondition (all behaviors)
#@ behavior positive: assumes p > 0
#@ behavior positive: ensures \result == p + 1
#@ behavior nonpositive: assumes p <= 0
#@ behavior nonpositive: ensures \result == 0
#@ complete behaviors positive, nonpositive
#@ disjoint behaviors positive, nonpositive
def f(p: int) -> int: ...
```

Each line is independently parseable; a grouping step (§4, step 3) collects clauses by
name. This is the recommended surface. (A future ergonomic pass could add the braced
multi-line ACSL block by teaching Module1 to fold `behavior NAME:` continuation lines —
out of scope here.)

## 4. Implementation phases

### Phase 1 — Grammar + AST nodes (`Module2_Parser.py`)

1. **AST nodes** (insert near the other clause dataclasses, ~lines 21–51):
   ```python
   @dataclass
   class BehaviorClause(CSLNode):
       name: str
       clause: CSLNode          # an Assumes | Requires | Ensures | Assigns

   @dataclass
   class Assumes(CSLNode):
       expr: CSLNode

   @dataclass
   class CompleteBehaviors(CSLNode):
       names: List[str]

   @dataclass
   class DisjointBehaviors(CSLNode):
       names: List[str]
   ```

2. **Grammar** — add to the `?contract` alternation (`Module2_Parser.py:568–595`):
   ```
   | behavior_clause | complete_behaviors | disjoint_behaviors
   ```
   and the rules (after the core clause rules, ~line 638):
   ```
   behavior_clause: "behavior" CNAME ":" behavior_body
   behavior_body: assumes_clause | precondition | postcondition | assigns
   assumes_clause: "assumes" expr
   complete_behaviors: "complete" "behaviors" name_list
   disjoint_behaviors: "disjoint" "behaviors" name_list
   name_list: CNAME ("," CNAME)*
   ```
   `precondition`/`postcondition`/`assigns` are reused verbatim — `behavior_body` wraps
   the existing rules, so `assumes`/`ensures` parsing is shared.

3. **Transformer methods** (alongside the others, ~lines 796–959):
   ```python
   def behavior_clause(self, name, body):      return BehaviorClause(str(name), body)
   def assumes_clause(self, expr):             return Assumes(expr)
   def complete_behaviors(self, names):        return CompleteBehaviors([str(n) for n in names])
   def disjoint_behaviors(self, names):        return DisjointBehaviors([str(n) for n in names])
   def name_list(self, *names):                return list(names)
   ```

   ⚠️ `assumes`, `complete`, `disjoint`, `behavior` become **reserved words** in contract
   position. Confirm none currently parse as bare `CNAME` identifiers in existing corpus
   contracts (grep the 410-file reference corpus; almost certainly clean, but verify).

### Phase 2 — Group + desugar (new pass in `Module3_Weaver.py`)

The weaver already dispatches parsed clauses onto `csl_*` fields by `isinstance`
(`Module3_Weaver.py:57–97`). Add, **before** that dispatch, a desugaring step:

1. Collect all `BehaviorClause` for the node, bucket by `name` (ordered dict, source
   order — preserve determinism; cf. the hash-seed lesson in
   `module6_whyml/functions.py`).
2. For each behavior `b` with guard set `assumes_b` (conjoin if multiple `assumes`) and
   clauses:
   - each behavior `requires R` → append `Requires( BinOp(assumes_b, "==>", R) )`
   - each behavior `ensures E`  → append `Ensures( BinOp(Old(assumes_b), "==>", E) )`
   - behavior `assigns` → §6.
3. For `CompleteBehaviors(names)` → append `Ensures( Old(A1) || Old(A2) || … )` (or one
   `Ensures( Old(A1 || A2 || …) )`). For `DisjointBehaviors(names)` → for every pair
   `(i,j)`, append `Ensures( UnaryNot( And(Old(Ai), Old(Aj)) ) )`. **Not a `Requires`, not
   an `assert`** — see the ⚠ in §2. These are pre-state predicates, so wrapping the guards
   in `\old` and asserting them as postconditions makes them *proof goals* (`Pre ⟹ ⋁Aᵢ`)
   that fail on a gap, without strengthening the caller contract.
4. Drop the `BehaviorClause`/`Complete`/`Disjoint` nodes after desugaring; feed **all** the
   synthesized `Requires`/`Ensures` into the **existing** dispatch
   (`node.csl_requires` / `node.csl_ensures`).

Build the synthesized nodes from the **existing** `BinOp`, `Old`/`CSLOld`, and unary-not
classes — no new expression types, no body injection. After this pass the rest of the
pipeline sees only ordinary requires/ensures and needs **no further change**.

> Placement note: do this in the weaver (where contracts first land on AST nodes) rather
> than the parser, because `complete`/`disjoint` need *all* of a node's behaviors
> collected first — a per-line parser can't see across lines.

### Phase 3 — Semantic validation (`Module4_SemanticAnalyzer.py`)

Module4 validates (does not transform) contracts (`Module4_SemanticAnalyzer.py:512–525`).
Because desugaring already happened in Module3, the synthesized requires/ensures get
validated for free. Add only **behavior-specific** checks (run on the pre-desugar
behavior list, so stash it on the node, e.g. `node.csl_behaviors`):

- every name in `complete`/`disjoint` refers to a defined behavior;
- `\result` does not appear in any `assumes` (guards are pre-state — reuse the existing
  `\result`-only-in-postcondition check at `Module4_SemanticAnalyzer.py:204–208`);
- duplicate behavior names → error;
- a behavior with `ensures` but no `assumes` ⟹ guard defaults to `True` (ACSL semantics);
  document and allow.

### Phase 4 — Modules 5 & 6: **no change expected**

By Phase 2 the IR (`Module5_IREmitter.py:1260–1272`) and WhyML emission
(`module6_whyml/functions.py:156–202`) only ever see desugared requires/ensures containing
`==>` and `\old`, all already supported. (This is why `complete`/`disjoint` must lower to
`ensures \old(…)` and **not** to a PyCSL `assert`, which the emitter drops as a no-op —
see §2 ⚠.) **Verify** with a differential: the desugared behavior contract must emit the
same WhyML as the hand-written `ensures { (old A) -> E }` / `ensures { (old A1) || (old A2) }`
equivalents. If anything in Module5/6 needs touching, the desugaring in Phase 2 was
incomplete — fix it there, not here.

## 5. Worked lowering example

Surface:
```python
#@ behavior pos: assumes n >= 0
#@ behavior pos: ensures \result == n
#@ behavior neg: assumes n < 0
#@ behavior neg: ensures \result == -n
#@ complete behaviors pos, neg
#@ disjoint behaviors pos, neg
def my_abs(n: int) -> int: ...
```
Desugars (Phase 2) to **four `ensures`** (no requires, no assert):
```python
#@ ensures (\old(n >= 0)) ==> (\result == n)
#@ ensures (\old(n < 0))  ==> (\result == -n)
#@ ensures \old(n >= 0) || \old(n < 0)        # complete
#@ ensures !(\old(n >= 0) && \old(n < 0))     # disjoint
```
Emits (Module6, `hoare`) the WhyML:
```whyml
  ensures  { (old (n >= 0)) -> (result = n) }
  ensures  { (old (n < 0))  -> (result = (- n)) }
  ensures  { (old (n >= 0)) || (old (n < 0)) }            (* complete *)
  ensures  { not ((old (n >= 0)) && (old (n < 0))) }      (* disjoint *)
```
The last two ensures reference only pre-state, so their VC reduces to `Pre ⟹ …`: they are
**proved by the function** (and *fail* when a case is missing or overlaps — the whole point
of the meta-clauses), yet impose no obligation on callers. A `requires` would be assumed,
not proved; a PyCSL `assert` would be dropped entirely (§2 ⚠).

## 6. Per-behavior `assigns` (the one wrinkle)

ACSL's frame is global; a per-behavior `assigns` means "this behavior writes at most this
set." In PyCSL's default **`hoare`** memory model, `_emit_frame_condition` emits **nothing**
(`module6_whyml/statements.py:1238–1272`) — arrays are value-semantic, no aliasing — so
per-behavior `assigns` is a **no-op** there and can be accepted-and-ignored in v1.
For the typed/store models, a guarded frame (`assumes ==> region-exclusion`) is the
faithful lowering but adds complexity; **defer** to a follow-up and emit a clear
"behavior assigns unsupported in <model> model" diagnostic if used. Document this scope
limit in the SKILL.

## 7. Test plan

1. **Unit (parser)** — new cases in the Module2 test suite: each behavior clause parses;
   `complete`/`disjoint` parse; reserved-word collisions rejected cleanly.
2. **Desugaring (weaver)** — assert the synthesized `Requires`/`Ensures` AST equals the
   hand-written `==>`/`\old` equivalent (structural equality).
3. **WhyML differential** — for each demo, assert the behavior version emits byte-identical
   WhyML to its hand-desugared twin, under `PYTHONHASHSEED=0` (determinism; cf. the
   param-order fix in `functions.py`).
4. **End-to-end proof** — `pycsl --proof` on the demos must close (Why3). Include a
   **negative** case: a `complete behaviors` that does *not* cover all inputs must make the
   completeness VC **fail** (proving the check has teeth).

### Reference-corpus additions (required for any new feature)

Per project convention, add demos to `test-suite/corpus/pycsl-reference/` (410 files
today, e.g. `0001.py`/`0001.mlw`). Add at least:
- `NNNN.py` — `my_abs` from §5 (complete + disjoint, both provable) + its golden `.mlw`;
- `NNNN.py` — a behavior with a global `requires` plus two cases;
- `NNNN.py` — a deliberately **incomplete** behavior set, marked to show the completeness
  VC failing (xfail/expected-fail per corpus conventions).
Regenerate goldens with the standard corpus tooling; re-baseline the SY3 (`src/pycsl`)
cmmi mod-index if def counts shift.

## 8. Documentation

- `config/skills/pycsl-annotate/SKILL.md` — add the behavior surface syntax, the
  desugaring semantics (guard is pre-state for `ensures`), and the `hoare`-model
  `assigns` limitation.
- Note in the skill that `behavior`/`assumes`/`complete`/`disjoint` are reserved in
  contract position.

## 9. Risks / open questions

1. **Reserved-word collisions** — `assumes`/`behavior`/`complete`/`disjoint` could shadow
   identifiers used in existing contracts. Mitigation: grep the corpus before landing;
   the LALR grammar will surface ambiguities at build time.
2. **`\old` of a compound guard** — confirm `Old(BinOp(...))` lowers correctly (not just
   `Old(Var)`); `expressions.py:950–959` wraps the inner expr generically, so a compound
   `(old (n >= 0))` should be fine, but add a test.
3. **Empty / default guard** — `behavior b: ensures E` with no `assumes` ⟹ guard `True`
   ⟹ `ensures { (old True) -> E }` ⟹ `ensures { E }`. Harmless; verify Why3 simplifies.
4. **Formal-semantics mirrors** — because we desugar to existing nodes, the Rocq/Lean
   AST mirrors (`src/formal-semantics/…`) need **no** new constructors. Confirm the
   self-annotate / cross-check gate stays green (it compares non-`#@` bodies only).
5. **Determinism** — bucket behaviors with an **ordered** dict and emit synthesized
   clauses in source order; an unordered `set` would reintroduce the hash-seed proof
   flakiness fixed in `module6_whyml/functions.py`.

## 10. Estimated scope

Front half (grammar + nodes + transformer + weaver desugar + Module4 checks): the bulk of
the work, all in `Module2_Parser.py`, `Module3_Weaver.py`, `Module4_SemanticAnalyzer.py`.
Back half (Module5/6): ideally **zero** code, only differential tests. Plus corpus demos
and SKILL docs. No new dependency, no new IR schema, **0 `\trusted`** preserved.
