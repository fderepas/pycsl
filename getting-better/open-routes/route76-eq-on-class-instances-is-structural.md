# ROUTE #76 — `==` ON CLASS INSTANCES IS STRUCTURAL, PYTHON'S IS IDENTITY

**STATUS: OPEN — found 2026-09-11 (gen #7) at HEAD `e7c25f0d`.** Reproduced at HEAD,
mechanism read off the emission, ground truth measured by RUNNING each program under
CPython (not reasoned about).

**THIS IS THE DUAL OF ROUTES #42/#52.** Those found `is` decided by VALUE equality — `is`
too WEAK. This is the mirror image: `==` on class instances decided by STRUCTURAL
equality — `==` too STRONG. #42/#52 were closed by giving `is` its own IR operator; the
`==` side of that same coin was never examined.

**IT IS THE #69 CLASS, THE SERIOUS ONE:** a FALSE POSTCONDITION about ordinary TOTAL
Python. No `no_exception`, no memory-model flag, no opt-in of any kind.

## THE ROUTE

```python
class C:
    v: int
    def __init__(self, v: int) -> None:
        self.v = v

#@ ensures \result == x          # <-- FALSE OF THE PROGRAM. PyCSL: SUCCESS.
def dup(x: C) -> C:
    return C(x.v)
```

**CPython measured, not reasoned about:** `dup(a) == a` is **`False`**. `C` defines no
`__eq__`, so Python's `==` falls back to *identity*, and `dup` returns a FRESH object.

**BOTH DIRECTIONS MEASURED, which is what makes this a route and not a gap:**

    \result == x    FALSE of the program  ->  **Verification SUCCESS**   (the unsoundness)
    \result != x    TRUE  of the program  ->  FAILED                     (so not merely incomplete)

## THE MECHANISM, READ OFF THE EMITTED WhyML

```whyml
type c = { mutable v: int }

let dup (x: c) : c
  ensures  { (result = x) }        (* Why3 logic `=` — STRUCTURAL on the record *)
=
  { v = x.v }                      (* a fresh record with the same field value *)
```

`==` is emitted as Why3's polymorphic logic `=`. On a record type that is equality of the
FIELD VALUES. Python's `==` on a class that defines no `__eq__` is `object.__eq__`, i.e.
**identity**. Two distinct objects with equal fields are `=` in Why3 and `!=` in Python.

## CARRIER 2 — A USER-DEFINED `__eq__` IS DISCARDED OUTRIGHT

Sharper than carrier 1, because here the user *wrote the definition* and the tool ignored it:

```python
class C:
    v: int
    def __init__(self, v: int) -> None: self.v = v
    def __eq__(self, o: 'C') -> bool:  return False      # NOTHING is equal

#@ ensures \result == x          # <-- PyCSL: SUCCESS.  CPython: ident(a) == a is False
def ident(x: C) -> C:
    return x
```

Module 5 **skips dunders for body emission** (its own comment, `preamble.py` ~9060), so
`__eq__` is never emitted and never consulted. This is the #73/#74/#75 shape — **a
built-in default beats the definition the user wrote** — with the default being Why3's
structural `=` rather than a hand-added oracle.

## THE ESCALATION: THE FALSE FACT DISCHARGES A **PRECONDITION**

Not merely an `ensures` about objects — it certifies a CALL whose documented precondition
is false at runtime:

```python
#@ ensures \result == x
def dup(x: C) -> C:            return C(x.v)

#@ requires a == b
#@ ensures \result == 1
def only_if_equal(a: C, b: C) -> int:  return 1

#@ ensures \result == 1
def caller(x: C) -> int:
    return only_if_equal(dup(x), x)    # `a == b` is FALSE here in CPython
```
**`[+] Verification SUCCESS! All contracts formally proven.`** — CPython measures the
call-site precondition as `False`. So contract-based reasoning about object equality is
unsound in BOTH the assume and the guarantee direction.

## WHAT MAKES IT SHARP: THE `@dataclass` CARRIER IS **CORRECT**

Measured in the same session, and it is the control that bounds the route:

```python
@dataclass
class P:
    v: int
#@ ensures \result == x
def dup(x: P) -> P: return P(x.v)
```
CPython: `dup(a) == a` is **`True`** — `@dataclass` GENERATES a structural `__eq__`.
PyCSL: SUCCESS. **FAITHFUL.** Structural `=` is the right model here.

So this is not "object equality is unmodelled". It is: the model hard-codes STRUCTURAL
equality, which is right for exactly the classes whose `__eq__` *is* structural
(`@dataclass` with default `eq=True`, `NamedTuple`) and wrong for every other class —
a plain class (identity), a custom `__eq__`, and `@dataclass(eq=False)` (identity again).
Same shape as route #59's List-vs-Dict control: two kinds of class have DIFFERENT equality
semantics in Python and the model gives both the same one.

## WHAT FAILS CLOSED, AND ONLY BY A TYPE ACCIDENT — READ THIS BEFORE BUILDING

**THE WHOLE BODY PLANE IS CONFINED BY ONE SHARED WHY3 TYPE ACCIDENT.** Nine dunder
carriers were enumerated mechanically (`__eq__`, `__ne__`, `__lt__`, `__bool__`, `__len__`,
`__contains__`, `__getitem__`, `__add__`, plus a non-dunder control). In a function BODY
every one dies with the SAME Why3 message:

    This expression has type PyCSL_Program.c @rho, but is expected to have type int

i.e. the class record type is not usable where the lowering wants an int. **That is a
`SAFE-TYPED` verdict, which this campaign has banked as a type accident and never a
guard.** The SPEC plane has no such constraint — `requires`/`ensures` lower `==` to
polymorphic `=`, which typechecks fine on records — and that is the whole reason the route
lives in the spec plane only.

**REOPENING CONDITION FOR THE WHOLE DUNDER FAMILY, stated once:** any change that makes a
class record type usable in an int context in a BODY (an unboxing, a `__bool__`/`__len__`
lowering, an `__eq__`-to-int coercion) reopens ALL NINE body carriers simultaneously. One
condition to watch, not nine.

**THE VALUE-LEVEL ESCALATION FAILS CLOSED, and by Why3's OWN REGION TYPING** — the same
mechanism that fails-closed route #59's return carrier. `setv(dup(x)); return x.v` with
`ensures \result == 5` comes back **Unknown**: the logic `=` between two records does NOT
make them the same REGION, so a write through one is not a write through the other.
Recorded so the next generation does not re-probe it.

**INCIDENTAL EMISSION BUG FOUND ALONGSIDE (not this route, worth its own look):** a local
with an EXPLICIT class annotation whose RHS is a CALL is pre-declared as `let b = ref 0` —
an int — so `b: C = dup(a)` ill-types. The annotation is ignored when the RHS is a Call.
That is the same "the RHS is a Call and the guard keys on a bare name" shape route #59's
return carrier had.

## REPAIR — SCOPED, NOT YET BUILT

Refuse (or model faithfully) a spec-plane `==`/`!=` whose operands are of a user CLASS type
whose `__eq__` is NOT structural:

  * `@dataclass` with default `eq=True`, and `NamedTuple`  -> ALLOW (measured faithful).
  * plain class with no `__eq__`                           -> Python is IDENTITY; refuse,
    or lower to the `is` operator that routes #42/#52 already built.
  * class with a user-defined `__eq__`                     -> the definition is discarded;
    refuse.
  * `@dataclass(eq=False)`                                 -> identity again; refuse.

**THE CENSUS COMES FIRST** (lesson (p)): routes #42/#52 already built a dedicated `is`
IR operator, so the identity machinery EXISTS and may be reusable rather than new. And the
cost question that decides the shape is how many corpus/mirror specs compare two
class-typed operands with `==` — that must be MEASURED before a refusal is written, since
a refusal that breaks the mirror is a fidelity-plane failure.

## WITNESSES (to land with the repair)

    carrier 1  plain class, fresh object      `\result == x`  PROVES  / CPython False
    carrier 1' true twin                      `\result != x`  FAILS
    carrier 2  user `__eq__` returns False     `\result == x`  PROVES  / CPython False
    control    `@dataclass`                    `\result == x`  PROVES  / CPython True (FAITHFUL)
    escalation precondition discharge          SUCCESS         / CPython precondition False
