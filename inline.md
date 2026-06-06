# inline.md — inlining method calls on module-level global instances

## Status — IMPLEMENTED (Phases 0–3)

Phase 0 spike confirmed Why3 1.8.2 accepts a module-level mutable-record global
(`let g : account = {…}` with `writes { g.balance }`); no ref-threading fallback needed.
Phases 1–3 are implemented:
- **Module 4** `collect_module_globals`; **Module 5** emits the `module_globals` IR;
  **Module 6** (`preamble.py::_emit_module_globals`) emits `let g : c = <ctor>` and
  resolves `g.field` (`_handle_attribute_expr` / `_handle_var_expr`, `_module_global_classes`).
- **`src/pycsl/ir_inline.py`** (`apply_inline_globals`, wired in `pycsl.py` after
  `_apply_composition`) inlines `g.m(args)` (statement + expression position; self→g,
  formals→actuals with temp-binding for non-trivial actuals; freshened locals), demotes
  global-touching functions out of `pure` (so they emit as program `let`), refuses
  recursive methods + bounds inlining depth, and bans aliasing a global.
- Drivers **0576/0577** (Phase 1 read), **0578/0579** (Phase 2 — the A2c payoff: a
  field-referencing post that the contract path can't prove), **0580** (Phase 3 recursion
  refusal). Whole corpus byte-identical (the pass is a no-op without object globals).

The rest of this file is the original design.

## Motivation

PyCSL verifies method calls **modularly** today: a call `c.m(args)` on a record-typed local/param
resolves the callee's *contract* (`expressions.py::_resolve_dotted_signature`, via
`_current_record_var_classes`). That has a known, documented gap — the **method-call contract gap**
(a.k.a. A2c): a method's *field-referencing* `ensures` (`\result == self.balance`, or a postcondition
relating `self.x` before/after) does **not** propagate to a caller that constructs and calls the
instance. Result-only / param-referencing ensures propagate (A2a); field-referencing ones do not. This
blocks class-based stub demos (StringIO/NodeVisitor) and any "construct an object, call methods, assert
on its fields" pattern.

**Inlining is the whole-program alternative** that closes the gap directly: instead of summarizing a
method by its contract, splice the method's *body* at the call site (with `self`→the receiver and
formals→actuals). The caller's verification condition then contains the real field reads and writes, so
`\result == self.balance` and cross-call field state are *exact* — no contract propagation needed. The
cost is the usual one for inlining: it is whole-program (no modular separation), it cannot handle
unbounded recursion, and it can grow VCs; we bound it with explicit guards (Phase 3).

This plan scopes inlining to method calls on **module-level global instances** — the case where the
receiver is a single, named, statically-known object (`acc = Account()` at module scope), which is the
simplest aliasing story (one object, one name, no aliasing) and the most common "stateful global"
pattern PyCSL cannot currently express.

## Scope & non-goals

In scope:
- A module-level global instance `g = C(<args>)` (a class with `#@ class invariant` and methods).
- Inlining `g.m(args)` used as a **statement** (mutating call) and as an **expression** (a call whose
  `\result` feeds an enclosing expression).
- Bodies that read/write `self.<field>`, call other methods on `self`/`g`, and return a value.
- Inlining method calls on *locals*/*params* (keep the existing contract path; revisit only if the
  contract gap blocks a real driver there).
- Recursive methods (Phase 3 refuses to inline; require a contract + `#@ \variant` instead).
- Aliased / collection-held instances, dynamic dispatch, inheritance overrides.
- Globals that are reassigned (`g = C(); …; g = C()`) — a global instance is bound once.

## Grounding (current tree)

- **Module-level globals barely exist.** Only module-level *int constants* are modeled:
  `Module6_WhyMLTranspiler` reads `self._module_constants = self.ir.get("module_constants", {})`
  (`module-constants-plan`), resolved to literals in `_handle_var_expr`. There is **no** model for a
  module-level *object* instance.
- **Records / class instances** are modeled as Why3 records: `type c = { mutable x: int } invariant
  { … }` (`preamble.py::_emit_type_decls`; the `mutable` + type-invariant machinery is the same one
  quantification P4 used). A local `acc = Account()` becomes a record-valued local.
- **Method calls resolve a contract, not a body.** `_resolve_dotted_signature` keys off
  `_current_record_var_classes` (locals, `IRScanner.find_record_var_classes`) ∪ `_record_param_classes`
  (params) to find `<class>__<method>` and apply its contract. **No inlining exists anywhere today.**
- **Method bodies are present in the IR.** Each method is a function-IR dict with `kind == "method"`,
  `self_type`, `formal_params`, `contracts`, and `body` — so the body needed for inlining is available;
  it is just never spliced into a caller.
- **`self.field` lowering** already qualifies fields via `_field_label(self_type, field)` and treats
  `self` specially; inlining must remap that `self` to the global's binding name.

## Phase 0 — Why3 spike (do FIRST; gates the whole approach)

The open question is **how Why3 models a mutable global**. Spike, before any PyCSL code, that all of
the following typecheck and discharge in Why3 1.8.2:

```
module Test
  use int.Int
  type account = { mutable balance : int } invariant { balance >= 0 }
  let g : account = { balance = 0 }
  let deposit (amount: int) : unit
    requires { amount >= 0 }
    writes { g.balance }
    ensures { g.balance = old g.balance + amount }
  = g.balance <- g.balance + amount
  let main () : unit = deposit 10; assert { g.balance >= 10 }
end
```

Key unknowns to resolve in the spike:
1. Does Why3 accept a **module-level mutable-record binding** (`let g = { … }`) that functions mutate
   via `g.field <- …` with a `writes { g.field }` effect? (If not, fall back: model the global as a
   single `ref`, or thread it as an explicit ghost parameter — decide here.)
2. Does the **type invariant** on `account` hold for `g` at the module level (so the global always
   satisfies `#@ class invariant`)? Where is it re-established after a write?
3. Does `old g.balance` work inside an inlined frame, and how does `\old` in the *caller* interact with
   writes from an inlined callee?

The result of Phase 0 fixes the global-state model used by Phases 1–2. **If module-level mutable
globals are not viable in Why3, the fallback is ref-threading** (pass the global record as an extra
`ref` parameter to every function that transitively inlines a call touching it) — heavier but standard.

## Phase 1 — module-level global instances

Recognize and model `g = C(<args>)` at module scope.

- **Module 1 / 3 / 5:** detect a module-level assignment whose RHS is a constructor call `C(...)` for a
  known class `C` (mirror the `module_constants` collection path, but for object instances). Emit a new
  IR section `module_globals: [{ "name": "g", "class": "C", "init_args": [...] }]`.
- **Module 6 (`preamble.py`):** after the type declarations, emit the global binding per the Phase-0
  model — e.g. `let g : c = { <field> = <init>; … }` (initial field values from `C.__init__`, which
  PyCSL already evaluates for local instances). Register `g → class C` in a new
  `_module_global_classes` map (analogous to `_current_record_var_classes`, but module-scoped and
  available in *every* function), and add `g`'s fields to the writes/effect tracking.
- **Reads in contracts/bodies:** `g.field` lowers to the record field on the global binding (reuse
  `_handle_attribute_expr` / the `_field_label` path — the same mechanism quantification P4 added for
  quantifier-bound record vars; `g` is just another known record-typed name).

**Gate-A drivers:** (1) a global instance whose field is read in a function contract
(`#@ ensures \result == g.balance`) — no method call yet, just the global-state model; (2) a FAIL twin
asserting a false fact about the global.

## Phase 2 — inline the method call

A new **IR-level inlining pass** (cleanest before Module 6; it can reuse the existing IR shapes).
For each call `g.m(args)` where `g ∈ module_globals` and `C.m` is a non-recursive method:

1. **Resolve** the callee `<class>__<m>` function IR (reuse the `_resolve_dotted_signature` name
   mangling; it already maps receiver-class + method → function name).
2. **Substitute** in a *copy* of the callee body IR: `self` → `g`, each formal → its actual argument
   expression (or a fresh let-bound temp if the actual is non-trivial / used more than once — avoid
   double-evaluation and capture), and **freshen the callee's local variable names** (`m`'s locals get
   unique suffixes to avoid colliding with the caller's).
3. **Splice**:
   - *Statement position* (`g.m(args)` as an `ExprStmt`): replace with the substituted body's
     statements.
   - *Expression position* (`x = g.m(args)` / `… g.m(args) …`): lower the body to a let-bound block
     whose value is the method's returned expression — i.e. hoist the body into a preceding statement
     sequence binding a fresh `_inl_result`, and replace the call expression with `_inl_result`.
4. **Invariant:** after the inlined writes, the global's `#@ class invariant` must still hold; with the
   Phase-0 type-invariant model Why3 re-checks it at the write site automatically (no explicit
   re-assertion needed) — confirm in the spike.

Because the body is spliced, the caller's VC sees the exact field mutations: a method
`def deposit(self, a): self.balance += a` inlined into `deposit_driver` makes `g.balance` provably
`old + a` **without** relying on `deposit`'s `ensures` propagating — closing the A2c gap.

**Gate-A drivers (the payoff):** (1) `g.deposit(10)` then `#@ assert g.balance == \old(g.balance) + 10`
— **fails today** via the contract path (field-referencing ensures don't propagate), **passes** once
inlined; (2) a method used as an expression (`x = g.peek()`); (3) a method calling another method on
the same global (nested inline); (4) a FAIL twin asserting the wrong post-state.

## Phase 3 — soundness guards & limits

- **Recursion:** refuse to inline a (directly or mutually) recursive method — detect via the call
  graph (`module6_whyml/scc.py` already computes SCCs) and emit a hard, actionable Module-4 error
  ("method `m` is recursive; verify it by contract + `#@ \variant`, not by inlining"). Never silently
  loop.
- **Inlining depth:** bound transitive inlining (a global method that calls another global method …)
  with an explicit depth cap; `log`/error past it rather than blow up.
- **Aliasing:** a module global is a single named binding — no aliasing to reason about. Forbid taking
  a reference/alias of `g` into a local that is then called (would reintroduce aliasing); a Module-4
  check.
- **Effects on multiple globals:** if a method touches several globals, the `writes` set is their
  union; ensure the Phase-0 effect model composes.
- **Termination of the *pass*:** the inliner itself must terminate (guaranteed by the recursion refusal
  + depth cap).

## Gates (every phase)
- **Byte-diff (additivity):** whole-corpus emission byte-identical except files that actually use a
  module-level global instance — Phases 1–2 only fire when `module_globals` is non-empty, so all
  existing files (no object globals today) must be untouched. All four memory models, `PYTHONHASHSEED=0`.
- **Gate-A driver first** per phase; FAIL twins stay failing.
- **Why3 type-checks** every emitted global binding and inlined frame (the spec §11 false-green gate).
- **5-surface doc-coherency** if a new `#@` directive is introduced (likely none — a module-level
  `g = C()` is plain Python, not a `#@` directive; only the *model* is new).

## Risks & open questions
- **R1 (gating): the Why3 global-state model (Phase 0).** Everything depends on it. If module-level
  mutable globals don't work, ref-threading changes function signatures and is a much larger change —
  resolve before committing to Phases 1–2.
- **R2: `\old` semantics across an inlined frame** — the caller's `\old(g.field)` must mean
  function-entry, while the inlined body may also reference its own pre-state. Define the pre-state
  mapping precisely (the callee's `self` pre-state = the value of `g.field` at the call site, not the
  caller's entry).
- **R3: double-evaluation / capture** during substitution — bind non-trivial actuals to fresh temps;
  freshen callee locals. Standard inliner hygiene, but easy to get wrong.
- **R4: interaction with the existing contract path** — locals/params still use contracts; only
  *module-global* receivers inline. Keep the two paths cleanly separated (dispatch on whether the
  receiver name is in `module_globals`).
- **R5: initialization** — `C.__init__` must be inlinable/evaluable to constant initial field values
  (PyCSL already does this for local instances); a non-trivial `__init__` may itself need inlining.

## Recommended order
**Phase 0 spike → Phase 1 (model the global) → Phase 2 (inline the call) → Phase 3 (guards).** Do not
start Phase 1 until the Phase-0 spike fixes the global-state model. Phase 2 is the payoff (it closes the
A2c gap); Phase 3 must land *with* Phase 2 (the recursion refusal is a soundness requirement, not a
nicety — an un-guarded inliner can loop or silently drop effects).

## Relationship to existing work
- Reuses the record/`mutable`/type-invariant model from `_emit_type_decls` and the quantification-P4
  binder-type→field-access path (`_handle_attribute_expr` via `_field_label`).
- Complements, does not replace, the modular contract path (`_resolve_dotted_signature`): inlining is
  for module-global receivers; contracts remain for locals/params and recursive methods.
- Closes the **method-call contract gap (A2c)** for the global-receiver case; the local/param case
  (A2c proper) stays open and could later adopt the same inliner if a driver demands it.
