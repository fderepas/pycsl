**Method-call inlining** verifies a method call on a module-level global instance
by *splicing the method's body* at the call site (with `self`→the global,
formals→actuals) — rather than summarizing the method by its contract. It is the
whole-program alternative to modular contract reasoning, used to close the
method-call contract gap for global receivers.

---

## The gap it closes

PyCSL normally verifies `c.m(args)` **modularly**: it applies the callee's
*contract* at the call site. But a method's *field-referencing* postcondition
(`\result == self.x`, or a post relating `self.x` before/after) does not propagate
to a function that constructs and calls the object — the "method-call contract
gap" (A2c). So you cannot prove a field-mutation fact about the object through its
contract.

**Inlining** sidesteps the contract entirely: the caller's verification condition
then contains the *real* field reads and writes.

```python
acc = Account()                       # a module-level global instance

#@ ensures acc.balance == \old(acc.balance) + amount
def do_deposit(amount: int) -> None:
    acc.deposit(amount)               # inlined → acc.balance <- acc.balance + amount
```

The field-referencing post now discharges (driver `0578`), which the contract path
cannot.

## Scope and guards (`inline.md`, `ir_inline.py`)

Scoped to **module-level global instances** — a single, named, statically-known
object (the simplest aliasing story). The IR pass:

- inlines `g.m(args)` in statement and expression position (freshening locals,
  temp-binding non-trivial actuals);
- **demotes** a global-touching function out of `pure` (a Why3 logic function
  cannot read mutable state — it becomes a program `let`);
- **refuses** recursive methods (verify those by contract + `#@ \variant`), bounds
  inlining depth, and **bans aliasing** a global (binding it to a local / passing it
  as an argument).

The global itself is modeled as a Why3 mutable-record binding `let g : c = {…}`.
Drivers `0576`–`0580`.
