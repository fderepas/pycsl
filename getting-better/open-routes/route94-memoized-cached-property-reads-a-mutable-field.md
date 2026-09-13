# ROUTE #94 — `@cached_property` reading a MUTABLE FIELD passes the UB-7.7 referential-
# transparency gate, and the proved postcondition is FALSE IN CPYTHON
# (demonstrated by running it)

**STATUS: OPEN — FULLY MEASURED INCLUDING A CPYTHON WITNESS, REPAIR SCOPED, NOT LANDED
(gen #13, 2026-09-13). SEVERITY 1.**
Left open deliberately: three routes (#91/#92/#93) were mid-gate-battery when this was found,
and landing a fourth would have meant killing the suite a third time and risking a window that
gated nothing. **The measurement is complete; only the repair is owed.** This is the same
hand-over shape route #51 was inherited in, successfully.

## THE GATE THAT WAS SUPPOSED TO CATCH IT

`frontend/module5/memoization_rt.py::_check_memoization_soundness` exists for exactly this
hazard. Its docstring:

> *"a memoizing decorator (lru_cache/cache/cached_property) is sound only on a
> **referentially transparent** function — one that is pure (effect-free) **AND reads no
> mutable global state**. Otherwise the cache returns results inconsistent with the verified
> (uncached) body — unsound. Reject (UB-7.7)."*

Corpus **0515**'s docstring states the same fourth conjunct — *"pure … **and reading no mutable
global**"*.

## THE MECHANISM — three independent reasons the fourth conjunct does not bite

```python
if not func_ir.get("pure"):
    reasons.append(...)
shared = {sv["name"] for sv in self.program_ir.get("shared_vars", [])}
if shared and self._reads_any(func_ir["body"], shared):
    reasons.append("it reads a `#@ shared` mutable global (non-deterministic)")
```

1. **`if shared and …` SHORT-CIRCUITS THE WHOLE CLAUSE when the module declares no
   `#@ shared` variable at all.** A file with zero `#@ shared` declarations gets zero
   mutable-state checking — the clause evaluates to nothing rather than to "no mutable reads".
2. **`shared_vars` is populated EXCLUSIVELY from `#@ shared` declarations**
   (`Module5_IREmitter`: `[{"name": d.variable, ...} for d in shared_decls]`). Module-level
   mutable singletons live in a *different* IR field, `module_globals`.
3. **`_reads_any` matches only `ir.get("type") == "Var"`.** A `self.<field>` read lowers to
   `FieldGet`, so **no field read can ever be seen by this check**, whatever is declared.

And `pure` does not help: `_detect_purity` is about **`assigns`**, not reads —
`assigns \nothing` ∧ ¬`diverges` ∧ ¬`trusted`. A method that reads a mutable field and writes
nothing is "pure" by that definition.

`cached_property` **is** recognised (`_MEMOIZING_DECORATORS = {"lru_cache", "cache",
"cached_property"}`, matched bare/dotted/called), so **the gate RAN and PASSED.** This is not
an unrecognised-decorator gap; it is the gate's own clause failing to cover the commonest case
of the very thing it names.

## MEASURED — AND THE FALSEHOOD IS EXHIBITED BY RUNNING CPYTHON

Driver:
```python
#@ class invariant self.a >= 0
class C:
    def __init__(self) -> None:
        self.a: int = 0

    #@ ensures \result == self.a
    #@ assigns \nothing
    @cached_property
    def total(self) -> int:
        return self.a

    #@ assigns self.a
    #@ ensures self.a == \old(self.a) + 1
    def bump(self) -> None:
        self.a = self.a + 1
```

| direction | verdict |
|---|---|
| PyCSL, `ensures \result == self.a` | **VERIFICATION SUCCESS** |
| PyCSL, `ensures \result == self.a + 1` (the DISAGREE twin) | **REFUSED** — so the channel discriminates; not vacuous |
| **0515** — a pure `@lru_cache` over a parameter | **PROVES** — the gate still admits a genuinely RT function |
| **0516** — an `@lru_cache` lacking `assigns \nothing` | **PIPELINE ERROR** — the gate demonstrably fires |
| **CPYTHON, the same program, executed** | `first access: total = 0, self.a = 0`; **after `bump()`: total = 0, self.a = 1**; `c.total == c.a` → **False** |

>>> **PyCSL PROVES `\result == self.a`, AND CPYTHON DISAGREES WITH IT.** The postcondition is
>>> not merely unjustified — it is false in the real language, on the first mutation, and
>>> `cached_property`'s entire purpose is to make that happen. This is UB-7.7, the exact
>>> divergence class `_check_memoization_soundness` was written to reject.

The two pre-existing corpus controls are what make this airtight: 0515 proves the gate has not
become a blanket refusal, and 0516 proves it is not dead code. Both were written by the
feature's own author.

## WHAT THIS CORRECTS IN THE INHERITED HANDOFF — WORTH READING

Gen #12 named **`module5/memoization_rt.py:74` the in-tree EXEMPLAR of safe remediation
advice**, because it *"bakes its exclusions into the sentence ('requires `#@ assigns \nothing`,
and no `\trusted` / `\diverges`') and its `_detect_purity` enforces exactly those three
conjuncts."* **That praise is accurate and it is also the trap.** The sentence names three
conjuncts and the code enforces exactly those three — but the guard's *own docstring* promises a
**FOURTH** ("reads no mutable global state") that the sentence never mentions and the code
barely implements.

>>> **ADVICE THAT NAMES ONLY CONDITIONS THE EMITTER REALLY CHECKS IS SAFE FOR THE USER WHO
>>> FOLLOWS IT — BUT IT IS NOT EVIDENCE THE GUARD IS COMPLETE. A PERFECTLY HONEST MESSAGE CAN
>>> SIT ON AN INCOMPLETE GUARD. AUDIT THE DOCSTRING'S PROMISE AGAINST THE CODE, NOT JUST THE
>>> MESSAGE'S.** The campaign spent gen #12 learning to distrust advice that over-promises;
>>> #94 is the mirror image — advice that *under*-promises relative to its own guard's stated
>>> contract, so nothing in the message looks wrong.

## HOW IT WAS FOUND

The deferral generator's census ranked this #2 (`Module5_IREmitter`: *"requires a referentially
transparent function (**checked in `_check_memoization_soundness`**)"*). I re-verified the three
matching rules myself and then measured all six drivers, because every candidate I checked this
generation needed narrowing.

## REPAIR — SCOPED, WITH THE OVER-NARROWING HAZARD NAMED

The clause must cover reads of **all** mutable state, not just `#@ shared` `Var`s:
1. **Delete the `if shared and …` short-circuit** — with no `#@ shared` declarations the clause
   must still evaluate, not vanish.
2. **Add a FieldGet arm**: a memoized function whose body reads `self.<field>` is not RT.
3. **Add the `module_globals` mutable singletons** alongside `shared_vars`.

**THE OVER-NARROWING HAZARD — NOW MEASURED, SEE THE SECTION BELOW (corpus 1057's lesson):** a
`@cached_property` *inherently* reads `self`, so a blanket field rule rejects **every**
`cached_property` on a mutable object. That may well be correct — a `cached_property` is RT only
if every field it reads is immutable — but it is a capability removal and must be measured, not
assumed. The narrower, clearly-sound version: reject only when a field the memoized body reads
is **assigned somewhere in the class** (i.e. demonstrably mutable), which admits a
`cached_property` over `Final`/never-written fields. **Build the positive control FIRST** — a
`cached_property` over a never-assigned field that still proves — or the repair cannot be
distinguished from a blanket ban.

## THE POSITIVE CONTROL IS ALREADY BUILT AND MEASURED — THE NARROW REPAIR IS VIABLE

I did not leave the over-narrowing hazard as a warning; I measured it, so the next generation
inherits a de-risked repair rather than a worry.

```python
#@ class invariant self.b >= 0
class C:
    def __init__(self) -> None:
        self.b: int = 7          # written ONLY in __init__, never again

    #@ ensures \result == self.b
    #@ assigns \nothing
    @cached_property
    def snapshot(self) -> int:
        return self.b
```

| | verdict |
|---|---|
| PyCSL | **VERIFICATION SUCCESS** |
| **CPython, executed** | `snapshot = 7, self.b = 7`, `snapshot == self.b` → **True** |

**So this `cached_property` is genuinely referentially transparent, and the model and CPython
AGREE about it.** That settles the design question: the repair must **NOT** be a blanket
field-read ban, because a real and correctly-modelled capability exists on the other side of
it. The discriminator that separates the two measured drivers is exactly:

>>> **REJECT A MEMOIZED BODY THAT READS A FIELD ASSIGNED SOMEWHERE OTHER THAN `__init__`.**

`memo_x2`'s `self.a` is assigned in `bump()` → reject. `snapshot`'s `self.b` is assigned only in
the constructor → admit. Note the `__init__` carve-out is the SAME one routes #91 and #92 needed,
for the same reason: the constructor establishes the object rather than mutating it. Three
repairs this generation have now wanted that carve-out, which is worth noticing as a pattern
rather than re-deriving a fourth time.

**So the repair has a PASS case and a FAIL case that are already written and already measured in
both PyCSL and CPython.** What remains is only the implementation plus the witnesses.

## OWED WITH THE REPAIR

Witnesses: the exploit as `# pycsl-expected: FAIL` with its mechanism; the never-assigned-field
control that must still PROVE; and — because the falsehood is a MODEL-vs-RUNTIME divergence
rather than an in-model contradiction — **a VALUE-DIFFERENTIAL pair, which is the corpus built
for exactly this class.** 0515 and 0516 must both stay green.
