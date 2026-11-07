r"""Test 1890 — gen #31 WITNESS for ROUTE #226 (expected FAIL): a `#@ class invariant` the
CONSTRUCTOR never establishes, published across the module boundary.

Before the repair this file printed `[+] Verification SUCCESS! All contracts formally
proven.` — no `no_exception`, no opt-in, no `\trusted` anywhere. In CPython `read(C())` is
`0`, and `0 >= 5` is False.

The mechanism, stated precisely (the coarse version cost a correction in the route file):
the emitter DOES raise the type-invariant VC where a record is CONSTRUCTED, so a file that
writes `c = C()` is caught. The obligation is attached to the CONSTRUCTION SITE rather than
to the CLASS. This file defines the class, publishes a reader for it, and constructs
nothing — the ordinary shape of a library module — so the question was never asked, while
`read`'s contract is offered to every caller.

The `by { n = 10 }` witness beside the type is what made the type look inhabited: it is
SYNTHESIZED FROM THE INVARIANT, so it is satisfiable whatever the invariant says.

The repair emits the constructor's own obligation beside the type:

    goal _check_class_inv_c : forall n : int. n = 0 -> (n >= 5)

which is the question `by { n = 10 }` was answering with a value `__init__` never produces.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ class invariant self.n >= 5
class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures \result >= 5
    #@ assigns \nothing
    def get(self) -> int:
        return self.n


#@ ensures \result >= 5
#@ assigns \nothing
def read(c: C) -> int:
    return c.get()
