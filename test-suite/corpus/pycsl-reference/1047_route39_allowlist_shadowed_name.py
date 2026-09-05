"""Test 1047 — ROUTE #39, the allowlist's own hole: a context-manager class that
SHADOWS a stdlib context-manager name was waved through by the whitelist.

FALSE OF THE PROGRAM: `__exit__` runs on the way out and sets `g.v` to 5, so Python
returns 5.

Route #39 replaced route #38's blacklist with a whitelist: once a file defines a
context-manager class, every `with` in it is refused unless its context expression is
POSITIVELY recognized as (W1) an in-file `@contextmanager` generator or (W2) one of a
small set of stdlib context managers with no value-model footprint.

W2 matches on the callee's LAST SEGMENT — it has to, because the same manager is
written `open(...)`, `tempfile.NamedTemporaryFile(...)` and `contextlib.closing(...)`.
So a user class named `closing` (or `suppress`, or `open`) that DEFINES
`__enter__`/`__exit__` matched the allowlist and was let through — THE ALLOWLIST WAS
LAUNDERING THE EXACT THING IT EXISTS TO EXCLUDE. Measured at the parent commit:
`\result == 0` PROVED while Python returns 5.

The fix is one clause: a name that is itself in the context-manager-class set is never
allow-listed, by W1 or by W2, whatever else carries that name.

THE RESIDUE, RECORDED RATHER THAN GLOSSED: W1 keys on a SIMPLE method name across the
whole unified AST, so if one class's `foo` is a `@contextmanager` and another class's
`foo` is not, `with self.foo()` on the second class is still allow-listed. Making that
class-aware is the next tightening; it is not one-lined, because `pure_ast` genuinely
defines `block` twice — once as a plain method and once as a `@contextmanager` — and a
"every definition must qualify" rule would refuse the mirror's own 14 `with self.block()`
sites outright.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
class G:
    def __init__(self) -> None:
        self.v: int = 0


g = G()


class closing:
    def __init__(self) -> None:
        self.n: int = 0
    def __enter__(self) -> int:
        return 0
    def __exit__(self, a: int, b: int, c: int) -> int:
        g.v = 5
        return 0


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    g.v = 0
    with closing():
        pass
    return g.v
