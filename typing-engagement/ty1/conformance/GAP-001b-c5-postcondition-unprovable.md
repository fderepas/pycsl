# GAP-001b — C5 driver postcondition independently unprovable (driver spec issue)

**Construct:** `Union` (TY1 tier)
**Clause:** C5 (union-twoplane-spec.md §1.2) — narrowing
**Plane:** Static
**Finding type:** Driver postcondition too strong (NOT a lowering gap)
**Severity:** Medium — blocks the C5 driver from fully PASSing, but the narrowing
itself (GAP-001's scope) is fixed and typechecks.

## Context

GAP-001 (the narrowing lowering gap) is FIXED: `if x is None:` on a
`Union[A, None]` value now lowers to a constructor-pattern match that projects
the variant to the non-`None` arm's carrier on the False branch. The generated
WhyML is:

```why3
match x with
  | Arm_0_None -> raise (Return 0)
  | Arm_0_0 x -> let x = x in (); raise (Return x)
end
```

The False branch yields the `int` carrier (not the variant), so `return x`
typechecks — the C5 narrowing obligation is discharged.

## Witness
- Driver: `typing-engagement/ty1/conformance/C5_is_none_narrowing.py`
- Body: `def f(x: Union[int, None]) -> int: if x is None: return 0; return x`
- Contract: `#@ requires True` / `#@ ensures \result >= 0`

## Evidence (the independent postcondition issue)

After the narrowing fix, the WhyML typechecks, but one sub-goal of the
postcondition `f'vc` remains unprovable:

```
File "...mlw", line 12, characters 15-28:
Sub-goal postcondition of goal f'vc.
Prover result is: Unknown (why3: Unknown (sat))
```

The split-VC emits TWO sub-goals for the postcondition (one per match arm):

- **True arm** (`Arm_0_None -> raise (Return 0)`): the postcondition
  `result >= 0` reduces to `0 >= 0` → **Valid**.
- **False arm** (`Arm_0_0 v -> raise (Return v)`): the postcondition
  `result >= 0` reduces to `v >= 0` where `v` is the projected `int` carrier
  — an ARBITRARY int (the caller's `x` is only constrained by
  `requires True`, which gives NO lower bound). → **Unknown (sat)**:
  `v = -1` is a counter-model.

The SMT2 for the failing sub-goal confirms it:
```smt
(declare-fun x1 () Int)           ; the projected int carrier, unconstrained
(assert (= x (Arm_0_0 x1)))
(assert (not (<= 0 x1)))          ; the negated postcondition
(check-sat)                       ; sat — counter-model x1 = -1
```

## Why this is NOT a lowering gap

The narrowing (GAP-001's scope) is fixed and correct. The False branch DOES
project the variant to the `int` carrier, the body typechecks, and the
function is well-typed. The unprovability is purely a consequence of the
driver's contract: `ensures \result >= 0` cannot hold when `return x` returns
an unconstrained `int` and `requires True` provides no `x >= 0` fact.

The GAP-001 doc's claim that "the postcondition `\\result >= 0` discharges"
is incorrect — there is no precondition bounding `x`, so the False-branch
return of `x` cannot prove `\\result >= 0` for ALL inputs. This is independent
of the narrowing lowering: ANY faithful lowering of `return x` on the False
branch (where `x` narrows to an arbitrary `int`) yields the same
unprovable `result >= 0` obligation.

## NO-BLEND
The runtime shim is not invoked; this is a pure static-plane postcondition
issue. NOT a blend.

## Recommendation
This gap is NOT fixable without either:
1. Weakening the driver's postcondition (e.g. `ensures \result == 0 \/
   \result == x`) — forbidden by the engagement rules (no weakening).
2. Strengthening the driver's precondition (e.g. `requires x >= 0`) —
   forbidden (cannot edit the conformance-agent's driver).
3. Adding `\\trusted` — forbidden.

Per the engagement rules ("If a gap is genuinely unfixable without weakening,
write a gap doc explaining why and leave it open — do NOT shortcut"), this
gap is left OPEN. The narrowing (GAP-001) is fixed; the driver's
postcondition is a separate spec issue owned by the conformance-agent.

## Status
Open (driver spec issue). The C5 narrowing lowering (GAP-001) is FIXED.
