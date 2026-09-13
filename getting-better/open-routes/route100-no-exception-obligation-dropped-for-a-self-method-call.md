# ROUTE #100 — A `#@ no_exception E` ON A **METHOD** IS PROVED WITH NO OBLIGATION AT ALL,
# BECAUSE `self.m(...)` ABSTRACTS TO A `val` THAT THE CALLEE-`raises` REGISTRY CANNOT FIND

**SEVERITY 1. FOUND, REPRODUCED, MINIMAL PAIR MEASURED, POSITIVE CONTROL REFUSING, CPython
CONTRADICTS A PROVED CONTRACT.** Found by the `continue`-census generator — its ranked
candidate #4, whose mechanism the census had VERIFIED by reading while explicitly flagging
*"whether any real name actually misses is INFERRED — not measured."* **It misses. This is
that measurement.**

## THE ONE-LINE STATEMENT

`caller` declares `#@ no_exception ValueError` and calls a method that declares
`#@ raises ValueError when n < 0`, with nothing constraining `n`. As a **free function** the
file is correctly REFUSED. As a **method called through `self.`** it reports
`Verification SUCCESS! All contracts formally proven.` — and CPython raises `ValueError`.

## THE MINIMAL PAIR — SAME CONTRACTS, SAME BODIES, ONE IS A METHOD

```python
#@ ensures \result >= 0
#@ raises ValueError when n < 0
def checked_abs(n: int) -> int:
    if n < 0:
        raise ValueError
    return n

#@ no_exception ValueError
#@ assigns \nothing
def caller(k: int) -> int:
    return checked_abs(k)          # <- or `self.checked_abs(k)` inside a class
```

| shape | verdict |
|---|---|
| free function (control) | **FAILED** — the obligation fires |
| the identical pair as METHODS of one class | **`Verification SUCCESS!`** |

**CPython ground truth:** `Helper().caller(-1)` **raises `ValueError`.** The proved
`#@ no_exception ValueError` is false of the running program.

## THE MECHANISM, READ OFF THE EMITTED WhyML (not inferred)

Free function — the obligation is emitted, and it is exactly right:

```
let caller (k: int) : int
  requires { (k >= 0) }
=
  begin assert { not ((k < 0)) }; try (checked_abs k) with ValueError -> absurd end end
```

The same call as a method:

```
let helper__caller (self: helper) (k: int) : int
=
  (self_checked_abs_1 k)
```

`self.checked_abs(k)` does **not** resolve to the concrete `helper__checked_abs`; it becomes
an **abstract `val self_checked_abs_1`**. `_wrap_call_with_callee_raises_assert`
(`Module6_WhyMLTranspiler.py:325-327`) then does:

```python
raises = self._module_func_raises.get(callee_name, [])
if not raises:
    return inner          # <-- the call is emitted UNWRAPPED
```

and `_build_callee_no_exception_summary` keyed that registry by the **IR function name**
(`helper__checked_abs`). The lookup misses, `raises` is `[]`, no `assert` and no `try/with`
are emitted, and the caller's `no_exception` set is discharged **by nobody**.

>>> **NOTE THE SIBLING PATH IS FAIL-CLOSED AND THE MISS PATH IS NOT.** Four lines below,
>>> `if cond_str is None: asserts.append("assert { false };")` — an unrenderable *condition*
>>> is refused loudly. An unresolvable *callee* returns silently. The same function contains
>>> both dispositions, which is why reading only one of them reads as safe.

## THE DEEPER SHAPE — THIS IS THE TRANSFERABLE PART

The abstract `val` is a **conservative** abstraction of what the caller may ASSUME: it
carries no postcondition, so `ensures \result >= 0` on the caller stops proving (measured —
the guarded method twin FAILS where the guarded free-function twin PROVES). Everyone
inspecting this path sees that strictness and reads it as "abstraction is safe here".

But the *same* abstraction is **permissive** about what the caller must DISCHARGE: losing
the callee's `raises` clause does not make a proof harder, it deletes an obligation.

>>> **AN ABSTRACTION THAT IS CONSERVATIVE FOR WHAT A CALLER MAY *ASSUME* IS PERMISSIVE FOR
>>> WHAT A CALLER MUST *DISCHARGE*. Losing a postcondition costs you a proof; losing a
>>> precondition or an effect obligation costs you the check.** The visible strictness on
>>> the assume-side is exactly what makes the discharge-side loss invisible.

This is the `no_exception` sibling of **route #70** (*a dotted stub drops the callee
PRECONDITION*) — same abstraction, same direction of loss, a different obligation. That #70
was found and closed and this survived is itself the evidence that the shape recurs per
obligation kind and should be swept once, not per route.

## THE MECHANISM, SHARPENED BY A SECOND MEASUREMENT — IT IS NOT "ABSTRACTION LOSES
## EVERYTHING", IT IS A **SELECTIVE** TRANSMISSION THAT KEEPS THE ASSUME-SIDE

The first reading above ("`self.m` becomes an abstract val, so the contract is gone") is
TOO KIND to the emitter and would have mis-scoped the repair. Measured on a callee carrying
BOTH clauses:

```python
#@ ensures \result == n
#@ raises ValueError when n < 0
def f(self, n: int) -> int: ...
```

the emitted val is

```
val self_f_1 (x0: int) : int
  ensures { (result = x0) }
```

**THE `ensures` IS TRANSMITTED ONTO THE VAL. THE `raises` IS NOT** — no `raises` clause on
the val, and no `assert`/`try…with` at the call site. Confirmed against the twin with no
`raises` at all: byte-identical val.

So the machinery to propagate a callee's contract across the `self.m(...)` abstraction
**EXISTS AND IS IN USE**. It carries exactly the half that HELPS the caller prove things,
and omits exactly the half that CONSTRAINS the caller. That is why every inspection of this
path reads as sound: the val visibly carries a contract.

>>> **THE BUG IS NOT THE ABSTRACTION. IT IS THAT THE CONTRACT-TRANSMISSION SET WAS
>>> ENUMERATED AS "WHAT THE CALLER MAY ASSUME" AND `raises` LIVES IN THE OTHER HALF.**

(Separately and minor: in the sev-1 reproduction the callee's `ensures \result >= 0` is
ALSO absent from the val, while `ensures \result == n` transmits — so the transmitted set is
narrower than "all ensures" too. That is a capability question, not a soundness one, and it
is NOT what this route is about.)

## STATUS

**OPEN.** Repair scoped below.

## THE REPAIR, SCOPED

0. **PREFERRED, AND SMALLER THAN (1): put `raises` INTO THE EXISTING TRANSMISSION SET.**
   The val already receives the callee's `ensures`; emit the callee's `raises` onto the same
   val (`raises { E -> ... }`) so Why3 itself forces the caller to discharge it. This reuses
   a working mechanism instead of adding a second name-resolution path, and it fixes every
   obligation-kind at once if the set is re-derived as "the callee's whole contract".
1. **OR resolve `self.<m>(...)` to the concrete IR name before the registry lookup.** The
   emitter already knows the enclosing class (`_current_self_type`), so the flattened name
   `<cls>__<m>` is constructible at the call site; look the registry up under it. Then the
   method path emits the same `assert`/`try…with` the free-function path already does.
2. **CO-LANDING, AND IT IS THE FAIL-CLOSED HALF:** a callee that STILL cannot be resolved
   must not return `inner` silently while the caller holds a non-empty `no_exception` set.
   Make that case emit the `assert { false }` its sibling already uses for an unrenderable
   condition — i.e. make the two dispositions in this function agree. Negative-test it with
   a genuinely unresolvable callee.
3. **BOTH DIRECTIONS MUST BE MEASURED:** the exploit must FAIL afterwards, AND the guarded
   method twin (`#@ requires k >= 0`, obligation dischargeable) must **PROVE** — it does NOT
   today, so this repair should *gain* a capability, and that gain is the check that it
   resolved the callee rather than merely refusing everything.
4. **SWEEP THE SHAPE, DO NOT JUST PATCH THIS OBLIGATION.** Enumerate every consumer keyed on
   a callee name — `no_exception`, `raises`, preconditions (#70), frames, `assigns` — and ask
   each whether `self.m(...)` reaches it. One census, not five routes.
