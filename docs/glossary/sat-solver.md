A **satisfiability (SAT) solver** decides whether a propositional Boolean
formula has a satisfying assignment, typically with a CDCL/DPLL search.

It is narrower than an [SMT solver](smt-solver.md): a SAT solver works with
Boolean variables and connectives, but it does not natively know about integer
arithmetic, arrays, maps, uninterpreted functions, or quantifiers.

---

## Why SAT solvers matter in PyCSL

PyCSL users usually do **not** invoke a bare SAT solver directly.

Why3 sends its [verification conditions](verification-condition.md) to Alt-Ergo
or Z3 because those goals talk about program theories such as integer bounds,
arrays, and maps. That is SMT territory, not plain SAT.

The SAT idea still matters as background because an SMT solver contains a
CDCL/DPLL Boolean (SAT) core; it is that core, wrapped by theory decision
procedures and quantifier instantiation, that an SMT solver builds on.

---

## Concrete examples

### Boolean skeleton versus theory facts

A Why3 VC often contains both:

- Boolean structure such as `A /\ (B -> C)`
- theory facts such as `0 <= i < Array.length a`

The Boolean skeleton looks SAT-like, but the arithmetic and array parts require
SMT reasoning.

### Why PyCSL says "SMT"

If a VC mentions facts like:

- `i < Array.length a`
- `Map.get m k = v`
- `x + 1 <= y`

then a plain SAT solver is not enough in the normal workflow. Why3 instead
calls Alt-Ergo or Z3 as SMT solvers.

---

## When the distinction is useful

If a discussion says “SAT” when it really means automatic proving over Why3
goals, the more accurate repo-facing term is usually
[SMT solver](smt-solver.md).

Use **SAT solver** when you specifically mean propositional search only.

---

## Related terms

- [smt solver](smt-solver.md)
- [theorem prover](theorem-prover.md)
- [verification condition](verification-condition.md)

> **In short:** SAT solves Boolean formulas; PyCSL usually needs SMT because
> its Why3 goals include arithmetic and program theories.
