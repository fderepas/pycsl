"""Route #216 CARRIER (expects SUCCESS — the false certificate).

`Sub.__len__` returns 0 under `#@ ensures \\result == 0`; `Base.__len__` promises
`\\result >= 5`. That is a Liskov violation, and with `--check-behavioral-subtyping` the
identical file spelled `m` instead of `__len__` reports FAILED with the goal
`sub__m_refines_base` in the emission. Spelled as a dunder, both methods are dropped from
emission, the override pair is never recorded, and the run prints

    [+] Verification SUCCESS! All contracts formally proven.

over a module whose entire body is `type sub = {  }`.

Run: pycsl.py --memory-model hoare --check-behavioral-subtyping <this file>
"""
_ = 0  # anchor


class Base:
    #@ ensures \result >= 5
    def __len__(self) -> int:
        return 5


class Sub(Base):
    #@ ensures \result == 0
    def __len__(self) -> int:
        return 0
