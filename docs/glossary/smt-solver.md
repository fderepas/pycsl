A **satisfiability modulo theories (SMT) solver** checks logical formulas that
combine Boolean structure with background theories such as integers, arrays,
maps, and algebraic data.

In PyCSL, **Alt-Ergo** and **Z3** are the main SMT solvers. **Why3** generates
the [verification conditions](verification-condition.md) and dispatches them to
those solvers.

---

## Why SMT solvers matter in PyCSL

Most PyCSL proofs are supposed to finish here automatically.

A typical `pycsl file.py` run:

- lowers Python plus contracts to WhyML
- asks Why3 to split the result into VCs
- lets Alt-Ergo or Z3 try to discharge those VCs

If the SMT solvers prove every VC, no manual proof script is needed.

---

## Concrete workflow

### What SMT is good at

SMT solvers are the normal back end for Why3 goals such as:

- array-bounds checks
- integer arithmetic side conditions
- small facts about maps, arrays, and equalities
- loop-preservation steps that stay local and explicit

That is why PyCSL proof engineering usually prefers local witnesses and cheap
invariants over wide reconstruction arguments.

### Where SMT usually stops

When a VC grows into expensive quantified reasoning or hard algebra, Alt-Ergo or
Z3 may return `Unknown` or time out.

That does not mean the VC is false. It often means the goal exceeded the
available [solver budget](solver-budget.md).

### Automatic first, Rocq/Coq later

If SMT leaves a VC open, `pycsl --rocq DIR file.py` can export the remaining
goal to Rocq (formerly Coq) so it can be proved manually and replayed later as a
[proof companion](proof-companion.md).

---

## SMT is not SAT

A [SAT solver](sat-solver.md) reasons only about propositional Boolean
structure.

An SMT solver adds background theories, which is exactly what PyCSL VCs need
when they mention arithmetic, arrays, maps, or Why3 library symbols.

---

## Related terms

- [sat solver](sat-solver.md)
- [theorem prover](theorem-prover.md)
- [verification condition](verification-condition.md)
- [solver budget](solver-budget.md)
- [proof companion](proof-companion.md)

> **In short:** an SMT solver is the automatic prover that Why3 uses for most
> PyCSL verification conditions.
