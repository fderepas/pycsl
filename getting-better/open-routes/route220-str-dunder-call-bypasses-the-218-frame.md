# Route #220 (CLOSED same day) — `x.__str__()` had its own recognizer, and it ran BEFORE route #218's repair

**Found:** 2026-09-23, gen #31, **by the independent fable reviewer** of the emit-dunders
report, running the oracle on route #218's own repair. One grep from the site the repair
touched, and outside everything that gated it.

## The decisive pair

```python
#@ class invariant self.v >= 0
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ assigns self.v
    def __str__(self) -> str:
        self.v = 7
        return "x"


#@ ensures \result == 0
def use() -> int:
    c = C()
    before: int = c.v
    _s: str = c.__str__()
    after: int = c.v
    return before - after
```

    [+] Verification SUCCESS! All contracts formally proven.

CPython answers **-7**; the TRUE twin (`== -7`) FAILS. The reviewer measured it at the
parent commit AND under the emit-dunders spike, where the emitted `let c____str__` exists
and the call site ignores it — so the emitted body and the call-site lowering DISAGREE.

## The mechanism, and the lesson it carries

`module6_whyml/expressions.py::_handle_call_expr` recognized `x.__str__()` early:

```python
if (isinstance(func_name, str)
        and (func_name == "__str__" or func_name.endswith(".__str__"))
        and not expr.get("args")):
    self._add_abstract_op("val str_dunder_op () : string")
    return "(str_dunder_op ())"
```

Nullary, contractless, no `writes` — which Why3 reads as PURE, a POSITIVE claim about the
whole heap. Route #218's body-derived frame lives in `_resolve_dotted_signature`, and this
branch RETURNS long before it.

**LESSON (n3) IN THE DIRECTION NOBODY LOOKS FOR.** (n3) was banked as "a new refusal can
RETIRE an old one by running first". The same is true of a REPAIR: a recognizer that runs
first can retire a fix as easily as it retires a refusal, and the fix's own gates will not
notice — #218 was landed, spiked, byte-swept over 3509 programs and battery-gated the same
morning, and this spelling was outside all of it. The generalisation is uncomfortable and
worth carrying: **after landing a repair at a dispatch point, enumerate every EARLIER
return in the same dispatcher.**

## Why the campaign's own instruments could not see it

* The corpus byte-diff cannot: ZERO corpus files call `.__str__()` explicitly, in either
  corpus, so #218's sweep was green and silent about it.
* The recognizer's own comment said so — "byte-clean (no corpus driver calls
  `.__str__()`)" — and that sentence is TRUE. It scoped the emission risk correctly and
  said nothing about the soundness risk, which is a different question about the same set.
* The refusal-witness and advice planes measure REFUSALS; this is a recognizer, not a raise.

## The repair (landed)

Route #218's, unchanged in shape. When the receiver is a KNOWN RECORD VAR whose class's
`__str__` writes self state (the `skipped_dunder_writes` table Module 5 now records at the
skip), mint

    val <cls>_str_dunder_op (self: <cls>) : string
      writes { self.<f>, ... }

instead of the nullary op. The result stays opaque — nothing is claimed about the string —
and the receiver's fields stop being provably unchanged, so a FALSE claim becomes an ABSENT
one: both `== 0` and `== -7` now fail.

**SCOPE, RE-COUNTED RATHER THAN INHERITED** (lesson f3 twice in one day): explicit
`.__str__()` calls number ZERO in `pycsl-reference`, ZERO in `python-reference`, ZERO in
`pycsl_lib`, THREE in the mirror and FIVE in the live tree — and every one of the eight is
`super().__str__()`, which has no record receiver and keeps the nullary op. Byte-inert by
measurement, not by construction.

## Witnesses

* `1820_route220_str_dunder_call_was_pure.py`                  — expected FAIL (the carrier)
* `1821_route220_ctl_readonly_str_dunder_still_verifies.py`    — expected PASS (a read-only
  `__str__` must still be modelled pure; without it the repair is a blanket "a `__str__()`
  call clobbers the receiver", the over-broad shape route #13's census refused once already)
