**`#@ uses <lemma>`** is a non-instantiating **ordering citation**: it forces a
cited lemma to be emitted *before* the citing function, so the lemma's general
fact is in scope when the function's goal is discharged — without instantiating
the lemma at any particular argument.

---

## The problem it solves

PyCSL orders WhyML declarations by a strongly-connected-component sort of the call
graph. A `#@ lemma`'s exported fact (`\forall n. to_int(n) >= 0`) is in scope only
for goals emitted *after* the lemma. But a function that *relies on* that fact
often does not **name** the lemma anywhere (it just needs the universal in scope),
so no ordinary call-graph edge forms — and the SCC may emit the function first,
leaving its goal unprovable.

```python
#@ ensures \forall x: Nat; to_int(x) >= 0
#@ uses to_int_nonneg          # force to_int_nonneg to be emitted first
def all_nonneg() -> int:
    return 0
```

## How it works

`#@ uses L` adds an explicit ordering **edge** `f → L` into the same SCC machinery
(`module6_whyml/scc.py`) that handles body calls and contract references, so `L`
is emitted before `f`. It **emits no WhyML** of its own — it is purely an ordering
declaration. Contrast an explicit lemma *call* `L(t)`, which instantiates the fact
at one argument `t` and does not, by itself, discharge a `\forall`-over-all goal;
the citation lets the lemma's *general* fact do the work.

## Where it is used

Introduced for the recursive-datatype quantified wrapper (driver `0565`)
and reused throughout [inductive reflection](inductive-reflection.md): the
inversion lemma cites the non-negativity consequence (`#@ uses even_nonneg`), and
the agreement lemma cites the inversion lemma (`#@ uses even_inv`).

It expresses an ordering dependency *explicitly* — the same principle that
motivated adding contract-reference edges to the SCC: orderings should reflect
declared dependencies, not source-order luck.
