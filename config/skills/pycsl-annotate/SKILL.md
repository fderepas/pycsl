---
name: pycsl-annotate
description: Annotates Python code with PyCSL Hoare-logic contracts (requires, ensures, assigns, loop invariants, loop variants) that compile to WhyML and are discharged by SMT solvers like Z3 and Alt-Ergo. Covers PyCSL syntax, memory-model extensions, quantifiers, class invariants, transpiler-specific limits, and solver-friendly invariant patterns. Use this skill whenever the user asks to annotate Python with formal contracts, add invariants to loops, verify PyCSL-annotated Python code with Why3 or an SMT solver, work with PyCSL, or convert imperative code into a verifiable specification — even when they describe the task informally as "add contracts," "make this provable," or "prove this function correct."
---

# PyCSL Annotator

You are a formal verification engineer. Your task is to analyze Python code and inject Design-by-Contract annotations using PyCSL — a custom contract language that compiles to WhyML and is verified by SMT solvers (Alt-Ergo, Z3).

## Workflow

**The contract transcribes the source of truth — it is not yours to invent.** A function's intended behaviour is fixed by an authority *outside* you: the Python language and standard-library reference (the **normative** specification), resolved by CPython wherever the English is silent (the **reference implementation**). Every `ensures` should be a formal **shadow of a specific sentence** in that authority — never a property you find convenient, or one that merely happens to prove. When the function models a documented API or a real-world spec (POSIX for `os`, etc.), **cite the source** in a comment (`# cite:` to the page, `# cite:_note:` for the paraphrase) so the contract is auditable — a reader can trace it back to the sentence it encodes. A contract that proves but does not transcribe the source of truth is *coherent and wrong* — the worst kind of green. (Family-wide statement: `csl-philosophy` "The source of truth"; for stdlib modules: `pycsl-stdlib-coverage` "Source of truth".)

**Before writing any contract, read the entire function and understand its purpose.** Ask: *What is this function computing? What mathematical or logical property does it guarantee?* Then express that as the postcondition — the property the source of truth specifies, not a placeholder. For example:

- A function that finds the maximum should have `#@ ensures \result >= 0` (or a tighter bound if provable).
- A function that counts elements satisfying a property should have `#@ ensures \result >= 0` and `#@ ensures \result <= n`.
- A function that computes a sum of non-negative inputs should have `#@ ensures \result >= 0`.
- A method that deposits money should have `#@ ensures self._balance == \old(self._balance) + amount`.
- A function that returns `len(collection)` (or `length` of an array parameter) should have `#@ ensures \result >= 0` — Python's `len()` always returns a non-negative integer but **can return 0** for an empty collection. Only strengthen to `#@ ensures \result >= 1` if there is an explicit precondition that constrains the collection to be non-empty (e.g., `#@ requires \length(arr) >= 1`).

Reserve `#@ ensures True` only when no useful property of the return value is provable given the constraints of the grammar (e.g., a sum over an arbitrary signed list). `True` is the recommended form for vacuous postconditions; the older `1 == 1` idiom is still accepted but discouraged.

## Required on every function

Every function definition MUST have **all three** of `#@ requires`, `#@ ensures`, and `#@ assigns` — placed immediately before the `def` keyword, with **no blank lines** between the last `#@` line and the `def`. The pipeline uses line numbers from libcst's `PositionProvider` to match contracts to AST nodes; a blank line causes a line-number mismatch that silently drops all contracts for that function or class.

Every **recursive** function (a function that calls itself by name) MUST additionally include `#@ \variant <param>` — placed immediately before the `def` line, after `#@ assigns`, so PyCSL emits `let rec` with `variant { param }` in WhyML and the termination sub-goal can be discharged. Without this clause Why3 will time out on the termination obligation. The variant expression must be the parameter that decreases toward the base case (e.g., `n` for `factorial(n)`).

Every `while` and `for` loop MUST have `#@ loop invariant` and `#@ loop variant` — placed immediately before the loop keyword.

Add PEP 484 type hints to **all** function parameters and return types, even if missing in the input. Scripts with no annotations at all must be fully annotated from scratch.

---

## Section 1 — Function and loop contracts

**Function contracts** are placed immediately before the `def` keyword:

- `#@ requires <expr>` — Preconditions that must hold before execution.
- `#@ ensures <expr>` — Postconditions guaranteed after execution. Use `\result` for the return value.
- `#@ assigns <var1, var2> | \nothing` — Frame condition: what global state or references are modified.
- `#@ \variant <expr>` — Termination measure for recursive functions (must decrease, stay ≥ 0). Emits `let rec` + `variant { expr }` in WhyML.
- `#@ \variant (<expr>, <ordering>)` — Structural variant via a named well-founded ordering. Emits `variant { expr } with ordering`.
- `#@ \diverges` — Declares the function may not terminate (no termination proof required). Cannot be combined with `\variant`.
- `#@ no_inline` — Marks a method on a module-global instance as a modular-verification boundary: its body is verified once (as a `let`), and callers reuse its contract instead of splicing the inlined body. Use it when a large method proves standalone but blows up the SMT search when inlined into a caller (e.g. os `sys_write`). Sound — a false `ensures` fails the callee, not the caller. See no-inline.md.
- `#@ sibling_concrete` — Opt-in (default off): an intra-class `self.<m>()` call to a method marked with this directive lowers to a CONCRETE call `(<class>__<m> self args)` instead of the default abstract `val` stub, so the caller inherits the callee's full contract AND its type/class-invariant guarantee on the post-state. Use ONLY on cheap-to-maintain leaf writers whose guarantee the caller can absorb as an atom (e.g. the os bitmap leaves `_set_bitmap`/`_poke`, so the allocator loops inherit the disk class invariant `uniq`/`inode_bytes_valid`). Decoupled from `no_inline` (sibling-call lowering only, not wrapper inlining). Sound — a concrete call to a verified `let` is the method's real semantics; adds no trust. See annotations.md §2.1.26.
- `#@ verify_module <name>` — **Opt-in axiom isolation via separate Why3 modules** (default off). The tagged method is emitted into its OWN top-level Why3 `module <name>` (shared infra re-declared per module; the concrete record type shared through a common base `module` that every emitted module `use`s) so that ONLY the `#@ proof` axioms cited by that group's functions are in scope for its goals — methods sharing `<name>` co-reside. A cross-module `self.<m>()` call is lowered to the callee's PROVEN contract via Why3 module **`clone`-refinement** (the interface `module` declares the contract; the provider `module` discharges the synthetic `<fn>'refn'vc` proving the real `let` implements it), so the boundary is a proven interface — NEVER an assumed `val`, a new `\trusted`, or a new axiom (net TCB unchanged). Use when one function's VC tips into OOM/Timeout because a *different* group's cited axioms pollute its SMT context (the os read `field_to_str`/`dir_scan_*` vs write `dir_blit_marker*` co-residence that blocks the `_dir_lookup` de-trust). Why3 `scope` does NOT isolate axioms (a scope is a namespace; an `axiom` is global within its `module`); only separate top-level `module`s do. Absent ⇒ the single flat `module PyCSL_Program`, byte-identical. See `annotations.md` §2.1.29.
- `#@ interface ensures/requires/assigns <…>` + `#@ reveal <fn>` — **Contract opacity** (Track B): a function keeps its rich **definition** contract (plain `requires`/`ensures`/`assigns`, verified against the body) but exports a narrow **interface** contract that callers see by default; `#@ reveal <fn>` opts a specific call site back into the definition's facts. Use it when a heavy contract (e.g. the codec's 18 per-field `ensures`) must be *proved* but should not burden every importer — the rich proof rides only the revealing sites. Sound: a **narrowing VC** proves `definition ⟹ interface`, so an over-claiming interface is rejected and opacity adds no trust. Absent ⇒ transparent (interface = definition). See `annotations.md` §2.10, `b-spec.md`.
- `#@ \trusted` or `#@ \trusted reviewer: <name>` — Body is not verified; contracts are assumed as axioms. Emits `val` (spec-only) instead of `let` + body. Callers may use the postcondition, but the implementation is not checked. The optional `reviewer:` clause names a human or process accountable for the trust assumption (e.g., `reviewer: alice` or `reviewer: pycsl-self-annotate`); it is captured by Module 3 / Module 5 but does not affect WhyML emission. Anonymous `\trusted` (no `reviewer:`) produces a warning; the convention is to always include one. See `annotations.md` §2.1.7 for the reviewer-tag convention.
- `#@ assumes bounded_int(N)` — Bounded integer pragma (N = 32 or 64). All `int` params/locals become `intN` machine integers; arithmetic (`+`, `-`, `*`) auto-generates overflow proof obligations.
- `#@ raises ExcType when <cond>` — Exceptional postcondition. Declares that the function may raise `ExcType` when `cond` holds. Emits `raises { ExcType -> cond }` in WhyML.
- `#@ no_exception E1, E2, ...` or `#@ no_exception \all` — Turns **implicit** Python exceptions into proof obligations. For each IR operation in the body that could raise a listed exception, Module 6 emits a WhyML `assert { trigger }` immediately before the operation; trigger conditions are looked up in `src/pycsl/exception_model.py`. Phase 1 exceptions: `ZeroDivisionError`, `IndexError`, `KeyError`, `ValueError`, `StopIteration`. Cannot be combined with `raises { E -> _ }` for the same `E`. The `\all` form additionally requires the `raises { }` set to be empty.
- `#@ allow_finalizer` — Class-level escape annotation. Place immediately before the `class` keyword to opt a class with a `__del__` method out of UB-7.5's hard rejection. Use *only* when the class genuinely needs a finalizer (rare in verification-grade code); the annotation documents the boundary but does not make the finalizer verifiable.
- `#@ allow_iteration_mutation` — Loop-level escape annotation. Place immediately before a `for` statement to opt out of UB-7.1's mutation-during-iteration check. Use *only* when the loop intentionally mutates the iterated container (the `for k in list(d):` snapshot pattern is the canonical case).
- `#@ proof <rocq|lean> <qualname>` — **Axiom import** (`test-suite/annotations.md` §2.1.12). Imports a Rocq or Lean theorem as a Why3 axiom in the WhyML preamble. **Module-level** (placed before any function definition). The directive has real semantic effect — Alt-Ergo/Z3 may use the imported axiom to discharge obligations. **The annotator agent MUST NOT generate `#@ proof` lines** unless `proof2why3` has been run and the cross-check manifest shows `reconciled` status for the target. **Namespace-aware audit:** the cited `<qualname>` is enforced as a real namespace path — for `Pycsl.Reference.Gcd.gcd_step`, the theorem must live inside `Module Pycsl. Module Reference. Module Gcd.` (Rocq) or `namespace Pycsl.Reference.Gcd` (Lean) in `<file>.proofs/{rocq,lean}/<file>.{v,lean}`. Run `pycsl --audit-proof <file>` to verify. **Worked example: `test-suite/corpus/pycsl-reference/0342.py`** (Euclidean GCD, with proofs under `0342.proofs/{rocq,lean}/`).
- `#@ ghost <name> = <expr>` — Ghost variable declaration/assignment. Place before any statement. First occurrence → `let ghost <name> = ref <val> in`; subsequent → `ghost <name> := <val>`.
- `#@ ghost <name> : <type> = <expr>` — Typed ghost variable declaration. `<type>` is one of: `int` (default), `string`, `array`, `ghost_dict`, `ghost_list`, `ghost_set`, `tuple2`, `tuple3`, `tuple4`.
- `#@ ghost <name> += <expr>` — Ghost augmented assignment (`+=`, `-=`, `*=`). Ghost variables are erased at extraction but usable in contracts and loop invariants.
- `#@ ghost <arr>[i] = <expr>` — Ghost array element assignment (in-place mutation, for `array`-typed ghosts only).

**Loop contracts** are placed immediately before the `while` or `for` keyword:

- `#@ loop invariant <expr>` — Property that holds before and after every iteration.
- `#@ loop variant <expr>` — A strictly decreasing non-negative integer expression that proves termination.

`for` loops with `continue` and early `return` are supported — annotate them just like `while` loops.

---

## Section 3a — Guarded cases (`act` blocks)

For functions whose postcondition splits by case, use a Pythonic `act` block (ACSL
"behaviour"). `#@ act <name>:` is followed by a **4-space-indented** body of
`#@ given` / `#@ requires` / `#@ ensures` (strict — a misindented or tab-indented
body line is a hard error):

```python
#@ act neg:
#@     given x < 0
#@     ensures \result == 0 - x
#@ act pos:
#@     given x >= 0
#@     ensures \result == x
#@ complete neg, pos
#@ disjoint neg, pos
def myabs(x: int) -> int:
    if x < 0:
        return 0 - x
    return x
```

- `#@ given <expr>` is the case guard (ACSL `assumes`), read in the **pre-state**;
  `\result` is not allowed in a `given`. Each guard is written **once** here — the
  single source of truth that makes the case analysis DRY.
- Desugars to `ensures \old(<given>) ==> <post>` / `requires <given> ==> <pre>`
  (no new construct, 0 `\trusted`).
- `#@ complete c1, c2, …` proves the guards cover every input; `#@ disjoint …`
  proves at most one holds. Both are real proof obligations (they fail on a
  gap/overlap), **checked on normal return only** (vacuous on `raise` paths in v1).
- See `annotations.md` §2.1.15. Reference demos: corpus `0454`/`0455` (prove),
  `0456` (incomplete set — completeness VC fails).

---

## Section 3b — Statement checkpoints (`#@ assert` / `#@ check`)

A mid-body proof obligation attached to the following statement (like `#@ label`):

- `#@ assert P` — prove `P` here **and assume it** for the rest of the block
  (prove-and-assume); use to give the prover a needed intermediate fact.
- `#@ check P` — prove `P` here but **don't** assume it downstream (prove-and-discard).

Both are **real obligations** — *not* the Python `assert` statement, which the prover
ignores (emitted as `()`). `\result` is not allowed (it's bound only at return — use
`ensures`). Example:

```python
#@ requires x > 0
#@ ensures \result == x + 1
def stepper(x: int) -> int:
    #@ assert x > 0
    #@ check x >= 1
    y = x + 1
    return y
```
See `annotations.md` §2.4 (rows 7–8). Demos: corpus `0457` (proves), `0458` (false assert fails).

## Section 3c — Region integrity (`#@ happy` meta-property)

When a class has a shared array field with a **reserved region** that only a few methods
may write (inode tables, headers, a bitmap), don't hand-copy a disjointness obligation into
every write site — declare ONE module-level **HAPPY** and let the compiler inject the per-site
`#@ check` everywhere. Written as a block (like `act`), 4-space-indented body:

```python
#@ happy region_integrity:
#@     region 512 .. 2560
#@     writes self.disk outside region
#@     except _write_inode, _write_directory
```

- Every write `self.disk[i] = …` / `self.disk[a:b] = …` / `self.disk[i] |= …` in any method
  **not** listed in `except` must lie outside `[512, 2560)`; the meta-pass injects
  `#@ check i < 512 or i >= 2560` (slice: `b <= 512 or a >= 2560`) at each. A failure names
  the HAPPY and the offending site.
- `except` lists the *legitimate writers*. A typo'd name is a hard error (it would silently
  widen coverage).
- A non-exempt `\trusted`/`\abstract` method (no checkable body) must add `#@ \preserves` to
  promise it leaves the region untouched (the meta-pass attaches the assumed
  `ensures \forall i; (512 <= i and i < 2560) ==> self.disk[i] == \old(self.disk[i])`);
  omitting it is a hard error.

The field-subscript term `self.field[i]` is usable in any contract (e.g. a hand-written
preservation `ensures`). See `annotations.md` §2.5. Demos: corpus `0459` (proves), `0460`
(in-region write fails at its site), `0461`/`0462` (trusted boundary with/without `\preserves`).

**Repetitive fixed-size clauses — prefer `#@ for` over `\forall`.** For a fixed, statically-sized run
of near-identical `requires`/`ensures` (codec bytes, struct fields, a fixed-width buffer), write a
`#@ for` block instead of copy-pasting or a quantifier:
```
#@ for k in range(0, 4):
#@     requires 0 <= data[k] and data[k] <= 255
```
It desugars to the four **ground** clauses (`k` → integer literal) — byte-identical to hand-writing them,
and crucially **without** the E-matching cost a `\forall k; (0<=k<4) ==> …` would carry. Rule of thumb:
**fixed and small → `#@ for`; symbolic or unbounded → `\forall`.** Bounds must be integer literals (v1).
See `annotations.md` §2.9, `sugar-for-spec.md`; demo corpus `0666`.

**Subsystem ownership — `protects`.** For whole-program confinement (no region,
possibly nested/dotted fields), declare which methods may write which paths:

```python
#@ happy fs_ownership:
#@     protects world.fs.disk, world.fs.next_fd
#@     except sys_open, sys_write, _alloc_inode
```

Any DIRECT write to a protected path in a method **not** in `except` gets a per-site
`#@ check False` (forbidden outright). Paths may be dotted (`world.fs.disk`). Aliasing a
protected base into a non-exempt local (`x = world.fs`) is a hard error — it would evade the
check. A non-exempt `\trusted`/`\abstract` method whose `assigns` names a protected path needs
`#@ \preserves`. This is *direct-write* ownership: a non-owner may still change state by calling
an owner method (the intended "go through the API" pattern). Demos: `0611` (proves), `0612`
(non-exempt write caught), `0613` (aliasing rejected).

**Per-object confinement — parametric HAPPY + `footprint`.** When two objects share
one array (inode A vs inode B in `disk`), parameterise the region and have each method declare
its footprint:

```python
#@ happy inode_conf(n):
#@     protects d.disk[512 + n * 64 : 512 + (n + 1) * 64]
#@     except formatter

#@ footprint inode_conf(k)
def sys_truncate(k: int, length: int) -> int: ...   # writes only d.disk[512+k*64 : …]
```

Each write `d.disk[i]=v` in the footprint method gets `#@ check (512+k*64 <= i and i <
512+(k+1)*64)` (CONTAINMENT — compose with an indexed `#@ assigns d.disk[lo:hi]` frame for
per-object PRESERVATION). A `footprint` naming an unknown HAPPY is a hard error. Demos: `0614`
(in-footprint write proves), `0615` (out-of-footprint caught).

**Auditing trust — `--soundness-report`.** Run `pycsl FILE --soundness-report` to
classify every function/VC as **Modelled** (body-verified), **Specified** (axiomatic contract),
**Stubbed** (signature-only), or **Confinement** (`\preserves`), with the TCB entries and the
trusted stubs each body proof rests on (JSON + human summary). Use it to see exactly what a
module's proof assumes versus proves.

---

## Section 3d — Strings (real `string.String` model)

Runtime `str` is the Why3 `string.String` value type (τ(str) = string) — it carries **real
content**, not an opaque hash. So these are verifiable on `str` params/locals/returns, and the
matching `\str_*` spec operators relate result to content:

- `len(s)` ↔ `\str_length(s)`; `s + t` (concat) ↔ `s ^ t`; `s[a:b]` ↔ `\str_sub(s, a, b)`;
  `s[i]` (a **length-1 string** — no char type); content `s == t` / `s != t`;
  `needle in haystack` (substring containment — carries an occurrence witness);
- methods with a content witness on a **simple `str` receiver**: `s.startswith(p)` /
  `s.endswith(q)` (0/1, with a `result=1 <-> substring …` clause) and `s.find(sub)` (index, with
  a found-index witness). A *chained* receiver (`node.name.startswith(…)`) stays opaque.

Spec operators (`\str_length`, `\str_sub`, `^`) work in `requires`/`ensures`/loop invariants and
now apply to runtime `str`, not only ghost strings (the old dual model is unified). Drivers:
corpus `0471` (substring search — the flagship), `0472`–`0476`/`0481`/`0490`–`0494`.

**Out of reach (keep contracts off these):** no code points — `ord`, character ordering
(`s[i] < "b"`), and codepoint parsing are unavailable; `upper`/`lower`/`strip`/`replace` and
`split` are opaque (no content spec); `.decode`/`.encode` are the opaque bytes↔str boundary
(`decode` yields an opaque `int`); f-strings hash; `str`-keyed dicts still key on the hash.

---

## Section 3e — Sum types (`#@ datatype`) and pattern matching

A module-level `#@ datatype` directive declares a **real Why3 algebraic type** (not an int
coarsening). Constructors may be nullary or carry typed payloads:

```python
#@ datatype Color = Red | Green | Blue
#@ datatype Box = Some(int) | Pair(int, int) | Empty
```

lowers to `type color = Red | Green | Blue` and `type box = Some int | Pair int int | Empty`.
Payload field types map `int→int`, `bool→int`, `str→string`, `float→real`.

- **Construct** with the Python call form — `o = Some(7)` → a typed variant local
  `let o = ref (Some 7) in`; a nullary `o = Red` → `Red`.
- **Match** with `match`/`case` over a variant param or local — it lowers to a Why3
  `match v with | Some n -> … | Pair a b -> … | Empty -> … end`. Capture names in the
  `case` (`case Pair(a, b):`) bind the payloads, so a postcondition relating `\result` to a
  captured field discharges. **Exhaustiveness is checked by the solver** — a missing or extra
  constructor is a hard error, not a silent gap.

Drivers: corpus `0520` (nullary enum + exhaustive match), `0521` (payload constructors,
construction + capture match).

**Out of reach:** a `requires`/`ensures` cannot reference a `case`-bound capture (captures are
in scope only inside their arm, not at the contract level); guarded patterns (`case Some(n) if
n > 0`), nested/`or` patterns, and wildcard `_` payload binds are not modeled; mutating a variant
field in place is out of scope (Why3 variants are by-value — rebuild and reassign the ref).

---

## Section 3f — Mixin composition (Tier 1)

Makes Python mixin composition machine-checkable. A `#@ mixin` class declares what it `provides`,
what sibling methods it `depends_method`/`requires_method` on, and the facade state it
`shared_state` (deliberately shared — D1) or `touches_field` (owned). A `#@ compose_from` class
composes the mixins; Module 4 checks every dependency has **exactly one** provider, no method has
two providers (collision), and every `self.<field>` write is declared — then flattens providers in.

```python
#@ mixin
class CoreEmit:
    #@ shared_state program_ir: int
    #@ provides emit
    #@ ensures \result >= 0
    #@ assigns \nothing
    def emit(self, x: int) -> int:
        return x if x >= 0 else 0

#@ mixin
class MapOps:
    #@ depends_method emit: (self, x: int) -> int
    #@   ensures \result >= 0
    #@ provides handle_get
    #@ ensures \result >= 0
    #@ assigns \nothing
    def handle_get(self, k: int) -> int:
        return self.emit(k)

#@ compose_from CoreEmit, MapOps
class Facade:
    #@ ensures \result >= 0
    #@ assigns \nothing
    def run(self, k: int) -> int:
        return self.handle_get(k)
```

Each mixin is verified **once** against its dependency interface (an abstract `val` — `\abstract`,
never `\trusted`); composition then checks the concrete provider refines it. Determinism/purity is
expressed with `#@ assigns \nothing` (the existing RT inference treats it as pure) — there is no
separate `deterministic`/`pure` directive in Tier 1.

**Out of reach:** the real facade's dynamic `getattr(self, _EXPR_DISPATCH[t])` dispatch is **not**
modeled — Tier 1 verifies the mixin algebra over *statically-named* providers (the dispatch table is
a separate coverage obligation). Two-provider conflict resolution (`resolve`, Tier 2) and diamonds /
general variance (Tier 3) are gated. See `annotations.md` §2.7 and corpus `0549`–`0553`.

---

## Section 3g — Lemma functions (`#@ lemma`)

A `#@ lemma` is a `-> None` function that is a **proved logical fact** — use it to
discharge an inductive obligation in-toolchain instead of importing a `#@ proof`. It
lowers to a Why3 `let [rec] lemma`: the body is the proof, and once verified the
contract `forall params. requires -> ensures` is usable by later goals.

```python
#@ lemma                                   # non-recursive: SMT discharges the (empty) body
#@ requires a >= 0 and b >= 0
#@ ensures a + b >= 0
#@ assigns \nothing
def sum_nonneg(a: int, b: int) -> None:
    pass

#@ lemma                                   # recursive: induction; \variant MANDATORY
#@ ensures to_int(n) >= 0
#@ \variant n
#@ assigns \nothing
def to_int_nonneg(n: Nat) -> None:
    match n:
        case Z():  pass                    # base case
        case S(m): to_int_nonneg(m)        # self-call = induction hypothesis
```

- A recursive lemma **must** carry `#@ \variant` (its self-calls are the IH; an
  ill-founded recursion is rejected — an unsound "proof by assuming the goal").
- `#@ lemma` + `#@ \diverges` is rejected; a lemma needs ≥1 `#@ ensures`.
- Prefer `#@ lemma` over `#@ proof rocq|lean` when Why3 + induction can close the body
  — it keeps the proof in-repo and machine-checked. Fall back to `#@ proof` only for
  what genuinely exceeds Why3's automation.

See `annotations.md` §2.1.16 and corpus `0558`–`0561`.

**`#@ uses <lemma>`** cites a lemma a proof relies on but doesn't name — the standard case being a
universal over a recursive datatype discharged by a recursive lemma:

```python
#@ ensures \forall x: Nat; to_int(x) >= 0   # needs induction; not SMT-direct
#@ uses to_int_nonneg                         # the recursive lemma that proves it
#@ assigns \nothing
def all_nonneg() -> int:
    return 0
```

A lemma's fact is in scope only for goals emitted after it; `#@ uses` forces that ordering (no WhyML,
no instantiation — cleaner than a throwaway `to_int_nonneg(Z())` body call). See `annotations.md`
§2.1.17 and corpus `0565`.

---

## Section 3h — Inductive predicates (`#@ inductive`)

A module-level `#@ inductive` defines a **least-fixpoint relation** by Horn-clause rules — use it for
a property that is not a terminating boolean function (well-formedness, reachability). It is
logic-only: usable in contracts and lemmas, never executable. The rules are bare `name: clause` lines
indented 4 spaces under the header (no `rule` keyword):

```python
#@ inductive even(n: int):
#@     even_zero: even(0)
#@     even_step: \forall m: int; even(m) ==> even(m + 2)
```

- Each rule's `<clause>` body is an ordinary contract expression (reuse `\forall x: T; …`,
  `==>`, and predicate applications `even(m)`). The conclusion must apply the predicate being defined.
- A predicate application `even(4)` is usable in any contract (`#@ ensures even(4)`). Introduction
  discharges it; inversion proves `not even(<odd>)`.
- A **universally-quantified** consequence (`\forall x; even(x) ==> P(x)`) is NOT SMT-dischargeable —
  prove it with a recursive `#@ lemma` (§3g). Inductive predicates + lemma functions are a pair.
- **Mutual groups:** a `with q(sig):` continuation block (same indent as `inductive`) joins `q` into
  the same group, so `p` and `q` may reference each other (e.g. `even`/`odd`). Lowers to one
  `inductive p … with q …`.
- **Soundness:** the predicate must occur only strictly positively in premises — Why3 rejects a
  non-positive rule ("non strictly positive occurrence"), group-wide.

See `annotations.md` §2.8 and corpus `0562`–`0563`, `0572`, `0574`–`0575`.

---

## Section 4 — Forbidden in contract expressions

**Three-level validation**: every `#@` expression must clear syntax (Level 1), static-semantics (Level 2), and WhyML-generation (Level 3) checks. `pycsl --no-proof` succeeding only guarantees Levels 1 and 2; Level 3 is verified by Why3. The most dangerous trap: contracts that pass Module4 yet fail Why3 (e.g., `"key" in d` when `d` is unannotated → `int` in WhyML, `in` on `int` is invalid). See `references/validation-stack.md` for the IS/SR/TR rule tables and the practical decision checklist.

> **Full list:** See `references/forbidden-expressions.md` for the complete set of NEVER rules (50+ entries).

Key rules (most common mistakes):

- **NEVER use arbitrary function calls** (e.g., `abs(x)`, `range(x)`, `len(x)`) inside `#@` expressions. Use `\length(arr)` instead for array lengths.
- **`True`, `False`, `None` ARE supported** as first-class contract atoms (annotations.md §3.1.18, §3.1.19). Prefer `True` over `1 == 1` for vacuous preconditions, and `False` over `0 == 1` for intentionally-unprovable postconditions. `None` maps to `0` in WhyML.
- **`//` and `%` ARE allowed** in contracts — they map to WhyML `div` and `mod` (confirmed by test 0334). Earlier notes were wrong about them being forbidden.
- **NEVER use `**`** (exponentiation) in contracts — use literal constants instead.
- **NEVER place blank lines** between a `#@` block and the `def`/`class` it annotates.
- **NEVER name variables `val` or `match`** — reserved WhyML keywords.
- **NEVER use `return <value>` inside `if` in a `while` loop** — use flag+sentinel pattern (see Example 6).
- **NEVER use `==>` in `ensures`** for index-loop functions — always times out.
- **NEVER emit duplicate contract clauses** for the same function.
- **`\old(arr)` is NOT supported** — only `\old(scalar)` and `\old(arr[i])` work. If you need to compare the whole array's entry value to its exit value, use a ghost snapshot via `\copy(arr)` or `\copy_range(arr, lo, hi)` immediately on entry, and reference `snap[i]` in the postcondition. The parser will reject `\old(arr)` with "Unexpected token `\\old`" near the `(`.

---

## Section 5 — Class support

> **Full details:** See `references/class-support.md` for complete method rules, `\old` usage, class invariants, and multi-class examples.

Key rules:

- Do NOT annotate `__init__` or `@property` — copy `__init__` verbatim.
- Use `self.field` in contracts; `\old(self.field)` in `ensures`.
- Each method needs all three contracts (`requires`, `ensures`, `assigns`).
- `#@ class invariant <expr>` goes immediately before `class` keyword.
- Method preconditions must be strong enough to maintain class invariants.

---

## Worked examples

### Example 1 — Simple math

No loop; just function-level contracts.

**Input:**
```python
def multiply_by_two(x: int) -> int:
    return x * 2
```

**Output:**
```python
#@ requires x >= 0
#@ ensures \result == x * 2
#@ assigns \nothing
def multiply_by_two(x: int) -> int:
    return x * 2
```

### Example 2 — Loops and accumulators

`while` loop with a counter that serves directly as the loop variant.

**Input:**
```python
def countdown_sum(n: int) -> int:
    total = 0
    while n > 0:
        total += n
        n -= 1
    return total
```

**Output:**
```python
#@ requires n >= 0
#@ ensures \result == n * (n + 1) / 2
#@ assigns \nothing
def countdown_sum(n: int) -> int:
    total = 0
    #@ loop invariant total >= 0
    #@ loop invariant n >= 0
    #@ loop invariant total + (n * (n + 1)) / 2 == \old(n) * (\old(n) + 1) / 2
    #@ loop variant n
    while n > 0:
        total += n
        n -= 1
    return total
```

### Example 6 — Linear search (flag + sentinel pattern)

When a loop body ends with a bare `return i` (outside any `if` block), the WhyML transpiler emits `!i` (type `int`) in a `unit` position, causing a type error. Introduce `found = -1` before the loop, replace `return i` with `found = i; i = n` to force loop exit, and `return found` after the loop.

**Input:**
```python
def linear_search(values, target):
    n = len(values)
    i = 0
    while i < n:
        if values[i] != target:
            i += 1
            continue
        return i
    return -1
```

**Output:**
```python
#@ requires True
#@ ensures \result >= -1
#@ assigns \nothing
def linear_search(values: list, target: int) -> int:
    n = len(values)
    i = 0
    found = -1
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant found >= -1
    #@ loop variant n - i
    while i < n:
        if values[i] != target:
            i += 1
            continue
        found = i
        i = n
    return found
```

> **More examples:** See `references/worked-examples-core.md` (for-loop conversion, continue/early-return, recursion, list summation — Examples 3–8c) and `references/worked-examples-advanced.md` (binary search, boolean flags, KMP — Examples 9–13).

---

## Reference files

For anything beyond the workflow + §1 + worked-examples above, consult these files in order of relevance:

### Sections moved to references

- **`references/operators-and-quantifiers.md`** — §2: comparison/arithmetic/boolean operators, `\old`, `\forall`/`\exists`, implication.
- **`references/memory-model-extensions.md`** — §3: `\valid`, `\separated`, `\assigns arr[lo..hi]`, `\at`, label points, ghost variables (untyped + typed), the parameter-snapshot pattern.
- **`references/concurrent-model.md`** — §6: `--memory-model concurrent`, `#@ shared`, `#@ mutex_invariant`, `#@ critical`, `#@ thread_entry`, `#@ acquires`/`releases`, `#@ lock_order`.
- **`references/undefined-behaviour-patterns.md`** — §7: the 5 UB categories (mutation-during-iteration, hash+eq, shared writes, C-extension boundary, finalizers) and their escape annotations.
- **`references/no-exception-patterns.md`** — §8: writing `#@ no_exception` preconditions, branching-precondition pattern, inter-procedural call sites.
- **`references/stdlib-stub-awareness.md`** — §9: how stdlib calls resolve to the body-verified `src/pycsl_lib/` models (consumed as trusted stubs at the import boundary); when to extend the three-artefact set.
- **`references/real-world-patterns.md`** — patterns from rclpy verification: file-level anchors, simplified-model classes, IntEnum-as-int, TR-BUG-1/2 workarounds, `no_exception` call templates, trivial-prove class invariants.

### Pre-existing references

- **`references/forbidden-expressions.md`** — Complete list of NEVER rules for contract expressions: forbidden function calls, reserved names, type restrictions, pattern pitfalls, and WhyML type mismatches. Consult whenever writing any `#@` expression.

- **`references/validation-stack.md`** — Three-level validation-stack guide: IS/SR/TR rule tables and the practical decision checklist for syntax, static-semantics, and WhyML-generation failures.

- **`references/class-support.md`** — Class annotation rules: method contracts, `\old` usage, class invariants, multi-field records, multi-class files, and two complete class examples.

- **`references/worked-examples-core.md`** — Worked examples for core patterns: `for` loop conversion (Examples 3–5), factorial iterative/recursive (Example 7), list summation with weakened contracts (Examples 8, 8b, 8c).

- **`references/worked-examples-advanced.md`** — Worked examples for advanced patterns: binary search (Example 9), boolean-flag accumulators (Examples 10–12), KMP string search (Example 13).

- **`references/transpiler-limits.md`** — Body-code constraints: what the IR pipeline can lower to WhyML and what it cannot. Consult before annotating any function body that uses `return`, `None`, `raise`, `with`, dict access, ternary expressions, slice notation, `math.pi`, `sorted`/`set`, string methods, parameter mutation, nested early-return patterns, or anything beyond simple integer/list operations.

- **`references/solver-heuristics.md`** — Loop-invariant patterns for binary search, two-pointer, sliding window, multiplicative accumulators, binary flags + sentinels, conservation postconditions, and avoiding vacuous contracts.

- **`references/matrix-patterns.md`** — Matrix and 2D-array verification: the nonlinear-arithmetic problem, the linear-rewrite strategy, native 2D array support via `\length2d` / `\valid2d`, and five provable linear flat-matrix operations.

### Sibling skills (consult, do not duplicate)

- **`config/skills/pycsl-exception-model/SKILL.md`** — Phase 1 trigger
  table for `no_exception`. The authoritative source of truth for
  *which IR operation raises which Python exception, and which WhyML
  predicate discharges it*. Read before extending `no_exception`
  coverage.
- **`config/skills/pycsl-ub-catalog/SKILL.md`** — The five UB
  categories with detection mechanisms and escape annotations.
  Section 7 of this skill summarizes the patterns; the catalog has
  the full story.
- **`config/skills/pycsl-stdlib-coverage/SKILL.md`** — Governs the
  three-artefact discipline (`calls-english.md`, `calls-pycsl.md`,
  `src/pycsl_lib/`) and the discovery tool. Read before annotating
  code that calls a stdlib API for which no stub exists yet.

---

## Output requirements

Output ONLY the annotated Python code — no commentary, no explanation, no markdown fencing outside the code block.

**Every `if`, `elif`, and `else` block in the generated Python code MUST contain at least one statement.** An empty `if` body (a bare `if cond:` with no indented line below) is a Python syntax error (`expected an indented block`). Use `pass` as the body whenever the block has no logic to emit — for example:

```python
if radius < 0:
    pass
```

The output must include:

1. PEP 484 type hints on every parameter and return type.
2. All three function-level contracts (`#@ requires`, `#@ ensures`, `#@ assigns`) on every function, immediately before `def` with no blank lines.
3. `#@ \variant <expr>` on recursive functions; `#@ \diverges` when the function intentionally may not terminate; `#@ \trusted` when the body should be assumed correct without verification.
4. Loop-level contracts (`#@ loop invariant`, `#@ loop variant`) on every `for` and `while` loop, immediately before the loop keyword.
5. Class-invariant annotations (`#@ class invariant`) immediately before the `class` keyword when class-wide properties exist.

To verify only specific functions: `./pycsl --fun <name> file.py` — transitive call dependencies are included automatically.

## Value contracts, round-trips, and array-indexing gotchas (leaf-first)

When a function's postcondition won't prove, the fix is often at a LEAF it calls whose contract is
too weak (shape/length only). Fix bottom-up.

- **Serialization leaves need VALUE + round-trip contracts, not just length.** `_pack_uint16_be` →
  `#@ ensures \result[0] * 256 + \result[1] == v` (the bytes RECONSTRUCT v) on top of
  `\length(\result) == 2`; the matching `_unpack` → `#@ ensures \result == data[offset] * 256 +
  data[offset + 1]` (the inverse). Then `unpack(pack(v)) == v` proves by CONTRACT COMPOSITION (no body
  tracking), and composers (inode/record packers) lift the same way.

- **No `<<` / `>>` in the contract grammar** (parse error). Write byte composition arithmetically:
  `\result[0] * 256 + \result[1]` for uint16, `\result[0]*16777216 + \result[1]*65536 +
  \result[2]*256 + \result[3]` for uint32. Make the BODY arithmetic too (`v // 256`, `v % 256`) — it
  equals the bitwise `(v >> 8) & 0xFF` under the `0 <= v <= 0xFFFF` precondition and is provable; a
  bitwise body lowers to uninterpreted `bit_*` ops and the value post won't prove without a lemma.

- **`\valid(data, n)` is ABSOLUTE** (`\length(data) >= n`), NOT offset-relative. For
  `data[offset]` / `data[offset + 1]` the precondition must be `\valid(data, offset + 2)`, not
  `\valid(data, 2)` — a frequent latent bug (the access is out of bounds for large offset otherwise).

- **`\result[i]` and array-param `data[i]` work in contracts** (they lower to `Array.get`). Range-bound
  what you need: a uint16 reader needs `#@ requires 0 <= data[offset] and data[offset] <= 255` (and
  `+ 1`) to discharge `0 <= \result <= 65535`.

- **Compose over re-derive when a packer times out on a big array.** A function writing N fields into a
  fixed `out = [0]*K` that times out proving each field's value: don't make SMT redo the byte math —
  CALL the proven leaf and copy its bytes (`b = _pack_uint32_be(f); out[o]=b[0]; out[o+1]=b[1]; ...`),
  so the field ensures follows from the leaf's already-proven contract. Composition beats SMT
  re-derivation (and is cheaper than a lemma). See csl-philosophy "compose, don't re-derive".

- **The formal test is the capstone of a leaf-to-API annotation.** Once the leaves and the API carry
  true contracts, write a driver that exercises the API end-to-end over **symbolic** inputs (every
  parameter a `requires`-bounded symbol, never a concrete value) and assert the property as its
  postcondition — proved for *all* inputs, not the handful a concrete test samples (*a test asks "did it
  work this time"; a proof asks "could it ever fail"*). Two strengths, and say which you have:
  *totality/safety* (`#@ ensures \result == 0 or \result == 1` — the whole scenario runs to a well-formed
  result and never faults on any input) versus *functional content* (`#@ ensures \result == True` — a
  round-trip returns exactly what went in). The concrete test you wrote first is the same scenario with
  concrete inputs — the rehearsal for the formal one. The `os` module is the worked example
  (`formal_os_roundtrip` proves totality over all files); see `docs/formal-filesystem.md` and
  pycsl-stdlib-coverage "Step 5 — Write a formal test".

## Glossary

Core terms used in this skill have canonical definitions in `../../../docs/glossary/`:
[ghost code](../../../docs/glossary/ghost-code.md) · [witness](../../../docs/glossary/witness.md) ·
[local reasoning](../../../docs/glossary/local-reasoning.md) ·
[solver budget](../../../docs/glossary/solver-budget.md) ·
[memory model](../../../docs/glossary/memory-model.md) ·
[loop invariant](../../../docs/glossary/loop-invariant.md)

---

## Consolidated heuristics (from `test-supervise-sl` monitoring)

These heuristics were consolidated from the `os` module annotation fleet runs
(2026-06-22/23), trigger-tested and Gate-S-passed. Full provenance in
`config/skills/pycsl-monitoring/SKILL.md`.

### `#@ interface` is a RESTRICTIVE gate, not additive

Adding `#@ interface ensures` lines to a function causes the NON-interface
`ensures` to be DROPPED from the importer's view. When NO `#@ interface` is
present, ALL ensures are visible. Adding interface lines NEVER adds visibility —
it can only REMOVE it. Use `#@ interface` only to narrow an imported contract;
never to widen.

### Strengthen callee contract → caller-side consequence proves by application

When a caller-side consequence times out on SMT string theory (e.g.
`\str_sub`/`\str_length` reasoning at the call site), push the reasoning INTO
the callee's body-proven contract (strengthen it), then the caller proves by
DIRECT CONTRACT APPLICATION — no string-theory reasoning at the call site. This
is the leaf-first doctrine: prove hard facts where the body's local ops are
visible, expose them via the contract, compose at the caller. NEVER weaken,
NEVER `\trusted`.

### Module-level alias loses contract

`name = other_name` at module level loses the original function's contract.
`from pycsl_lib.os import kill` (where `kill = _kill`) emits `kill` as an
abstract `val` with NO ensures. Import the underlying function directly (even if
underscore-prefixed) to get the contract.

### Per-write type-invariant VC blowup → restructure to local-array + single slice write

A `sibling_concrete` helper that writes `self.dir`/`self.disk` in a 30-iteration
loop generates 30 type-invariant maintenance VCs per loop. Each needs the
slot-specific marker fold, but the helper only knows the opaque offset (not the
slot), so the marker can't fire — timeouts at billions of steps. Restructure:
extract the byte-building loop into a FREE function that builds in a LOCAL array
(no self-field write → ZERO class-invariant VCs on the loop). The helper then
does a SINGLE slice write — 1 type-invariant VC instead of 30.

### Unverifiable external-object call → restructure to verified-only path

When a method body calls an external object's method whose return value the
solver cannot constrain (e.g. `self._clock.monotonic()`), restructure to a
verified-only path (internal counter, pure computation) and treat the external
path as a runtime concern outside the verified surface (like host I/O). NEVER
add `\trusted` or weaken the contract.

### Callee-precondition Unknown → add leaf byte-range requires

When a body-VC reports "precondition Unknown" for a callee, the caller lacks the
facts the callee needs. Add them as `requires` on the caller (leaf-first: push
the byte-range/type facts to where they are known). Verify callers can discharge
the new requires (or add matching requires up the call chain). NEVER weaken the
callee's precondition to make it discharge.

### Cross-module `#@ reveal` does not surface interface-hidden ensures

`#@ reveal` is reliable WITHIN the owning unit; cross-module it does not
currently surface interface-hidden ensures. For cross-module consequence tests,
prefer a function with a transparent interface (no `#@ interface` → all ensures
visible to importers), or accept the interface opacity as a logged residual (the
property is body-proven, just not caller-visible).
