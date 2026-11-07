# OPEN ROUTE #50 — `Optional[str]` IS MODELLED AS "NEVER None, AND None IS THE EMPTY STRING"
# (found 2026-09-08 by relaunch #49, at commit `90fed0c9`; TWO halves, both proved end-to-end)

**How it was found is worth as much as the route.** It was NOT found by probing the emitter's
soundness claims directly. It fell out of MEASURING A DIFFERENT FIX: relaunch #49's route-#46
ambiguity pre-scan poisoned every ambiguous local with route #41's per-name opaque INT, and the
mirror emission diff showed `pycsl_erased_receiver_name` being fed into `str_eq_op` — i.e. the
poisoned local was a STRING. Reading `module6_whyml/types.py`'s own emission at HEAD to find out
why then showed the real defect sitting one line away: `if receiver_name is None or field_name
is None:` had been emitted as `if ((if false || false then 1 else 0) <> 0)`.

## The two halves, both measured at `90fed0c9`, both `[+] Verification SUCCESS`

```python
def mutable_state(cls):
    return cls

@mutable_state
@dataclass
class C:
    tag: int = 0

    #@ requires c < 0
    #@ requires t == "x"
    #@ ensures \result == 7          # <-- FALSE OF THE PROGRAM: Python returns 0
    def m(self, c: int, t: str) -> int:
        s = t
        s = None
        if c > 0:
            s = t
        if s is None:                # HALF (2): emitted as the literal `false`
            return 0
        return 7
```

* **HALF (1) — `None` IS THE EMPTY STRING.** A `None` bound to a str-typed local emits
  `s := ""`. Python's `None == ""` is False; the model's is decidably True. Replace the guard
  above with `if s == "": return 7` and it proves just as well
  (`scratchpad/w49/route50/r50b.py`).
* **HALF (2) — `x is None` IS THE LITERAL `false`.** `expressions.py` (~5153):
  ```python
  # i-feel-good.md I-B: `x is None`/`is not None` on a string-typed operand — an
  # `Optional[str]` local ... Same sound always-present model (empty-string "" is the
  # absent sentinel; both `if` arms type-check). @mutable_state-gated → byte-identical
  # elsewhere.
  if (self._is_string_expr(_nn)
          and getattr(self, "_current_self_type", None)
          in getattr(self, "_mutable_state_classes", set())):
      return "false" if raw_op == "==" else "true"
  ```
  The comment calls it a "sound always-present model". It is not sound and it is not a model:
  the branch is not *approximated*, it is DELETED — `if false then <the None path>` makes the
  path Python actually takes unreachable in the model, so every contract is proved over a
  STRICT SUBSET of the reachable states. The parenthetical "empty-string `""` is the absent
  sentinel" describes half (1), and half (1) does not even hold up on its own: a genuine `""`
  and a `None` are DIFFERENT Python values that this model cannot tell apart.

## Witnesses (all four run at `90fed0c9`, Python answers confirmed by running them)

| file | shape | model | Python |
|---|---|---|---|
| `scratchpad/w49/route50/r50.py`  | `s is None` after a conditional rebind, `@mutable_state` | PROVES `\result == 7` | returns 0 |
| `scratchpad/w49/route50/r50b.py` | `s == ""` on a `None`-bound str local, `@mutable_state`  | PROVES `\result == 7` | returns 0 |
| `scratchpad/w49/route50/r50d.py` | r50 WITHOUT `@mutable_state` | fails closed | returns 0 |
| `scratchpad/w49/route50/r50c.py` | r50b WITHOUT `@mutable_state` | fails closed | returns 0 |

The last two localise the gate exactly: **both halves are `@mutable_state`-gated**, and the
emitter's own classes are `@mutable_state` — so this is LIVE IN THE SELF-ANNOTATION MIRROR, not
only in user code. `module6_whyml/types.py::_field_type_of` is a measured live site
(`if receiver_name is None or field_name is None:` → `false || false`).

## Why the straight-line form fails closed, and why that hid this for so long

Route #44 records a `None` binding and makes a READ of that name the opaque `pycsl_none` — an
INT — so on a str-typed local the straight-line `s = None; if s is None:` reaches the opaque and
Why3 TYPE-REJECTS it. Fail-closed, by type accident rather than by design. The record is LINEAR
(route #46), so a CONDITIONAL rebinding clears it and the guard falls through to this arm. Both
halves therefore need the same ingredient route #46 needs: a rebinding on some path.

## REOPENING CAPABILITY

An `Optional[str]` needs an ABSENT value the model can tell apart from `""`. The cheapest sound
form is route #41's device with a STRING type: `val function pycsl_none_str : string`, no
defining axiom, with `s = None` binding `s := pycsl_none_str` and `s is None` lowering to
`(str_eq_op s pycsl_none_str)`. Then `s == ""` is undecidable (correct — the model does not know
whether s is None), `s is None` is undecidable after a join and DECIDABLE where the binding is
linear, and no branch is deleted.

**The cost is the reason this is recorded rather than landed in the same increment: it makes the
`is None` branches REACHABLE in the mirror's own emission, which adds VCs to whole-file proofs
that currently prove without them.** That is honest work, not a hidden cost, but it must be
measured (emission diff + whole-file re-proof) before it lands.
