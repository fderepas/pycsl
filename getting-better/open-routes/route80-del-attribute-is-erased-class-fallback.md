# ROUTE #80 — `del obj.attr` IS ERASED, AND A CLASS-ATTRIBUTE FALLBACK MAKES IT TOTAL

**STATUS: FOUND AND REPRODUCED 2026-09-11 (gen #8). BOTH DIRECTIONS MEASURED. OPEN.**

**CLASS: the #69 class** — a FALSE POSTCONDITION about ordinary, TOTAL Python. No
`no_exception`, no opt-in.

**THIS IS ROUTE #77's RESIDUE (a), UPGRADED BY MEASUREMENT.** #77 recorded `del obj.attr` and
`del name` as the *lower-value* half of its erasure: both are erased to `{"stmt": "Pass"}`, but
reading the deleted binding afterwards RAISES in CPython (`UnboundLocalError` /
`AttributeError`), so the program is not total and the value-differential plane rules it OUT OF
SCOPE. **That reasoning is correct for `del name` and WRONG for `del obj.attr`**, because Python
attribute lookup falls back to the CLASS attribute when the instance attribute is gone. The
program then runs to completion and returns a *different* value.

## THE EXPLOIT

```python
class C:
    x: int = 5                       # class attribute — the fallback
    def __init__(self) -> None:
        self.x = 10                  # instance attribute shadows it

#@ ensures \result == 10
def f() -> int:
    c = C()
    del c.x                          # removes the INSTANCE attribute only
    return c.x                       # falls back to the CLASS attribute
```

    CPython:  5
    PyCSL:    [+] Verification SUCCESS! All contracts formally proven.

## BOTH DIRECTIONS, MEASURED

| driver | claim | CPython | PyCSL |
|--------|-------|---------|-------|
| k04 | `\result == 10` | **5** | **PROVED** ❌ |
| k04 twin | `\result == 5` | 5 | refused (Unknown) |

The true twin failing is what makes it a route and not a gap.

## THE MECHANISM

The same site as route #77: `frontend/Module5_IREmitter.py::_py_stmt_delete` appends
`{"stmt": "Pass"}` for any non-Subscript target, under the comment *"`del name` / `del obj.attr`
(rebinding / attribute delete) — stays the unmodelled no-op it always was."* #77's repair closed
the SUBSCRIPT-with-slice arm only; this arm is untouched and still erases.

**THE LESSON THIS SHARPENS.** #77 banked *"a prose carve-out upstream of a guard is a route with
a signpost on it"*. #80 adds the sharper form: **when a residue is filed as "out of scope because
the program raises", that classification is itself a claim about Python, and it must be probed
rather than reasoned about.** One language feature — class-attribute fallback — turned a
non-total residue into a total route. The whole `del name` / `del obj.attr` family was written
off in one sentence; half of it was live.

## REPAIR

Refuse `del <attribute>` at the same site as #77's slice arm. `del name` stays a recorded
residue (it genuinely raises; it is route **#71**'s missing-obligation class, not this one).

**Blast radius: NOT YET MEASURED.** Census `del <name>.<attr>` across
`test-suite/corpus/`, `src/self-annotate/`, `src/pycsl/`, `src/pycsl_lib/` before building —
`src/pycsl_lib/json/encoder.py:20` has a bare `del i` (the `del name` form, out of scope for
this repair), and the subscript forms elsewhere are already handled.

## WITNESSES

`scratchpad/w58/c/k04_del_attr_class_fallback.py`, `k04_twin.py`.
