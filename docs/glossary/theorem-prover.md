A **theorem prover** is a tool that finds or checks proofs of logical
statements.

In PyCSL, this is an umbrella term. On the automatic side, Why3 sends
[verification conditions](verification-condition.md) to SMT solvers such as
Alt-Ergo and Z3. On the manual side, Rocq (formerly Coq) checks proof scripts
for the harder goals SMT leaves open.

---

## Why theorem provers matter in PyCSL

PyCSL verification does not stop at parsing annotations. It ends with theorem
provers establishing that the generated obligations really hold.

The usual flow is:

- PyCSL lowers Python plus contracts to WhyML
- Why3 generates VCs
- Alt-Ergo or Z3 try to prove them automatically
- if some remain, Rocq/Coq can prove them manually and replay them later

So **theorem prover** is broader than either **SMT solver** or **Rocq proof
companion**.

---

## Concrete workflow

### Automatic theorem proving

For most files, the theorem provers you notice are the SMT back ends behind
Why3.

A successful `pycsl file.py` run usually means every VC was discharged
automatically by Alt-Ergo or Z3.

### Interactive theorem proving

When automatic proof is not enough, `pycsl --rocq DIR file.py` exports the
leftover goals into Rocq proof skeletons.

Those scripts are then checked by the Rocq kernel during
`pycsl --rocq-proofs DIR file.py` or normal replay through a retained
[proof companion](proof-companion.md).

### Short Curry-Howard note

Rocq follows the Curry-Howard viewpoint: a proposition behaves like a type, and
a proof is a term inhabiting that type.

You do not need that idea for day-to-day PyCSL work, but it explains why Rocq
is a proof **checker**, not just a search engine: the finished script builds a
typed proof object that the kernel verifies.

---

## Related terms

- [smt solver](smt-solver.md)
- [sat solver](sat-solver.md)
- [proof companion](proof-companion.md)
- [verification condition](verification-condition.md)
- [solver budget](solver-budget.md)

> **In short:** theorem prover is the umbrella term; PyCSL uses SMT solvers
> automatically and Rocq/Coq when a VC needs manual proof.
