# ROUTE #73 — an opaque oracle keyed on the literal `"arity"` shadows a user-defined function

**STATUS: CLOSED** (found and repaired in generation #6).

## THE CARRIER

A complete, runnable Python program. Nothing is imported, nothing is untyped, and no
contract directive is opted into beyond an ordinary postcondition:

```python
#@ ensures \result == d
#@ assigns \nothing
def get(k: str, d: int) -> int:
    return d

#@ ensures \result >= 0
#@ assigns \nothing
def f() -> int:
    return get("arity", -1)
```

**CPython answers `-1`. PyCSL proved `\result >= 0`.**

This is the route #69 class and it is the most serious shape available: a FALSE
POSTCONDITION about ordinary TOTAL Python. Every route from #64 to #72 required the user to
opt in to `#@ no_exception`; this one requires nothing.

## THE CAUSE

`module6_whyml/expressions.py`, in `_lower_dict_get_call`. The branch fired on
`func_name == "get" and len(args) == 2` whenever the FIRST ARGUMENT was the literal string
`"arity"`, and emitted

```
val get_arity_field (x0: int) (x1: int) : int
    ensures { result >= 0 }
```

Both arguments are erased through `_coerce_to_int`, so the op is an oracle keyed on nothing
but a key name. The code's own comment concedes the shape — it describes the `ensures` as
"an assumed, trusted-stub-shaped contract" that fires for "ANY `.get("arity", ...)` call the
tool can't type" — and its justification is a DOMAIN CONVENTION OF THE SELF-ANNOTATION
MIRROR ("populated from `len(payload)` / a literal >= 0"), asserted globally, by key name,
over every program PyCSL compiles.

**An `ensures` on an abstract `val` is an AXIOM: available to every proof in the unit, with
nothing ever obliged to prove it.**

## WHAT THE MEASUREMENT ADDED THAT READING COULD NOT

* **Anti-vacuity, both directions.** The TRUE claim `\result == -1` did NOT prove while the
  false one did. So the oracle had not merely made the model permissive — it had REPLACED
  the user's function, leaving the user's own proved contract UNREACHABLE at the call site.
* **The delegated audit that surfaced this got the LOCATION wrong.** It reported the carrier
  as the dotted `cfg.get("arity", -1)`. Measured: an untyped receiver and a `Dict`-typed
  receiver BOTH emit zero occurrences. The live carrier is the BARE two-argument call.
  *Verify a delegated claim's scope, not just its headline* — the lesson route #70 banked.
* **The obvious guard was refuted BEFORE it landed.** Refusing when the DEFAULT argument is
  negative is defeated by moving the hazard one step:

  ```python
  def get(k: str, d: int) -> int: return -5
  def f() -> int: return get("arity", 0)     # CPython: -5;  `\result >= 0` PROVED
  ```

  That is the SIXTH instance of "a guard keyed on a syntactic location is defeated by moving
  the hazard one step", and the first caught before landing rather than after.

## THE REPAIR — STRUCTURAL, NOT SYNTACTIC

`func_name == "get"` arises two ways: a CHAINED `<expr>.get("arity", d)` whose receiver is
itself a call (the shape the oracle exists for — `expr_ghost_spec_ops.py`, where the
receiver's kind is untypable), and a BARE two-argument call to a user-defined function,
which carries no `receiver` field at all. The oracle now requires a receiver.

**A bare call cannot acquire a receiver, so there is no one-step-over spelling.**

## GATES

* Carriers closed: 1175 and 1177 (the stepped-around variant) both fail to prove.
* **Positive control, and the strongest evidence the repair is right:** 1176 — the TRUE
  claim `\result == -1` about the same program now PROVES where it did not before. The
  repair RESTORED the honest lowering; it did not merely refuse.
* Mirror emission BYTE-IDENTICAL, `get_arity_field` still emitted twice for its legitimate
  consumer.

## RETAINED BOUNDARY, AND ITS REOPENING CAPABILITY

With a receiver present this still asserts `result >= 0` of a value read out of a dict PyCSL
cannot type. `d.get("arity", 0)` returns the STORED value when the key is present, and
nothing makes that non-negative in an arbitrary program — it is the mirror's domain
convention, not a property of Python.

**REOPENING CAPABILITY:** emit the non-negativity as an OBLIGATION at the `Array.make` site
that needs it, instead of as an axiom on the getter. That costs the mirror a proof it
currently gets for free, which is why it was not done here.
