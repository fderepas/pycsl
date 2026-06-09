A **satisfiability modulo theories (SMT) solver** decides logical formulas that
combine Boolean structure with background theories such as integers, arrays,
uninterpreted functions, and algebraic data. Internally it is a CDCL/DPLL
Boolean (SAT) core wrapped by theory decision procedures (the DPLL(T)
architecture) and, for quantified goals, by trigger-based quantifier
instantiation (E-matching).

In PyCSL, **Alt-Ergo** (2.6.2) and **Z3** (4.13.3) are the main SMT solvers.
**Why3** generates the [verification conditions](verification-condition.md) by a
weakest-precondition calculus and dispatches them to those solvers. A solver
discharges a goal by reporting it **Valid** — equivalently, by showing the
goal's negation unsatisfiable.

---

## Why SMT solvers matter in PyCSL

Most PyCSL proofs are supposed to finish here automatically.

A typical `pycsl file.py` run:

- lowers annotated Python to WhyML
- has Why3 generate VCs by weakest precondition and split them into sub-goals
- lets Alt-Ergo or Z3 try to discharge each sub-goal under a per-goal time limit

If the SMT solvers report every VC Valid, no manual proof script is needed.

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

When a VC grows into expensive quantifier instantiation (E-matching) or hard
algebra, Alt-Ergo or Z3 may return `Unknown` or time out. For PyCSL's quantified
VCs the dominant cost is usually E-matching, not the propositional search.

That does not mean the VC is false. It often means the goal exceeded the
available [solver budget](solver-budget.md).

### Automatic first, Rocq/Coq later

The Rocq and Lean kernels do **not** run during a normal `pycsl` proof. If SMT
leaves a VC open, `pycsl --rocq DIR file.py` exports the remaining goal to Rocq
(formerly Coq) so it can be proved manually, offline, and replayed later as a
[proof companion](proof-companion.md).

---

## SMT is not SAT

A [SAT solver](sat-solver.md) reasons only about propositional Boolean
structure.

An SMT solver wraps that Boolean core with background theory procedures and
quantifier instantiation, which is exactly what PyCSL VCs need when they mention
arithmetic, arrays, uninterpreted functions, or Why3 library symbols.

---

## Related terms

- [sat solver](sat-solver.md)
- [theorem prover](theorem-prover.md)
- [verification condition](verification-condition.md)
- [solver budget](solver-budget.md)
- [proof companion](proof-companion.md)

> **In short:** an SMT solver is the automatic prover that Why3 uses for most
> PyCSL verification conditions.
