"""0446 — a driver constructs a class instance and calls its method; the
method's `ensures` propagates to the caller's proof obligation. Body-verified,
0 \trusted. Run under the hoare memory model.

Regression for the method-call contract fix: `c.get()` from a free function
previously lowered to a contract-less abstract op, so `run`/`use_bump`'s
postcondition was reported Unknown.
"""


#@ class invariant self.x >= 0
class Counter:
    def __init__(self):
        self.x: int = 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def get(self) -> int:
        return self.x

    #@ ensures \result >= 0
    #@ assigns self.x
    def bump(self) -> int:
        self.x = self.x + 1
        return self.x


#@ ensures \result >= 0
#@ assigns \nothing
def run() -> int:
    c = Counter()
    return c.get()


#@ ensures \result >= 0
#@ assigns \nothing
def use_bump() -> int:
    c = Counter()
    return c.bump()
