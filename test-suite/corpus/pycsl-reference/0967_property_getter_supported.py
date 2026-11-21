"""self-tcb-reduction relaunch #16: a POSITIVE witness for `@property` support.

Before this increment `Module5_IREmitter._should_skip_method` dropped every
`@property` outright, so a decorated getter appeared in the emitted theory
NEITHER as a `let` NOR as a `val` — it simply did not exist, and any `#@`
contract written on it was silently discarded. That is what the
`[UNEMITTABLE @property]` boundary recorded.

The decorator carries no verification semantics: a getter is a 0-argument
method whose result is a pure function of the record's fields. So it is now
emitted exactly like a plain nullary method,

    let box__area (self: box) : int

and its contract is discharged in the ordinary way. This driver PINS that:
`area` has a real `#@ ensures` that is only provable from the field values,
so a regression to the old skip makes the emitted theory lack the symbol and
the `main` driver below fails to type-check — loudly, not silently.

`docs/pycsl-translational-reference.md` §T.11.3 records the change: `@property`
moved out of "Missing Translations" and into the translated-construct table;
`@staticmethod` stays unsupported.
"""
from dataclasses import dataclass


@dataclass
class Box:
    w: int = 0
    h: int = 0

    #@ requires self.w >= 0 and self.h >= 0
    #@ ensures \result == self.w * self.h
    #@ ensures \result >= 0
    #@ assigns \nothing
    @property
    def area(self) -> int:
        return self.w * self.h


    # SELF-RECEIVER read of a `@property` (relaunch #16, the other half of the READ
    # capability): `self.area` inside a sibling method must ALSO route to the getter.
    # `self.<attr>` takes a DIFFERENT emitter path from `<recv>.<attr>`
    # (`_handle_field_get_expr` rather than `_handle_attribute_expr`), so it needs its
    # own rule and its own witness — without the rule this projects a record FIELD named
    # `area`, which does not exist, and the postcondition below is unprovable.
    #@ requires self.w >= 0 and self.h >= 0
    #@ ensures \result == 2 * (self.w * self.h)
    #@ assigns \nothing
    def double_area(self) -> int:
        return self.area + self.area


#@ requires True
#@ ensures \result == 12
#@ assigns \nothing
def main() -> int:
    b = Box(w=3, h=4)
    return b.area


#@ requires True
#@ ensures \result == 24
#@ assigns \nothing
def main_self() -> int:
    b = Box(w=3, h=4)
    return b.double_area()
