"""mutable-state-witnesses.py — M.5 witnesses for mutable-self-plan.md (M.2-M.4).

A `@mutable_state @dataclass` class gets CHECKED `assigns` frames: a method's
`#@ assigns self.x` is emitted as a WhyML `writes { self.x }` clause on the
concrete `let`, so Why3 verifies the body writes only its declared frame, the
mutation is visible to callers (escape), and a wrong/`\nothing` assigns FAILS.

These are the SUCCESS witnesses. The non-vacuity twin (`assigns \nothing` on a
mutating body) MUST FAIL — see the trailing comment; it is not in this pass-file.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/mutable-state-witnesses.py
"""
from dataclasses import dataclass


# Opt-in marker (no-op decorator; a proper stdlib entry is future work). Only its
# NAME matters — Module5._is_mutable_state_decorated keys on `@mutable_state`.
def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Counter:
    n: int

    # CHECKED frame: `writes { self.n }` on the concrete let. A `\nothing` here FAILS.
    #@ assigns self.n
    #@ ensures self.n == \old(self.n) + 1
    def bump(self) -> None:
        self.n = self.n + 1


# ESCAPE: the mutation is visible to the caller — `s.bump()` makes `s.n` become 1.
# (On value-semantic records this FAILED — a3-plan.md §9; the @mutable_state model
#  flips it.)
#@ ensures \result == 1
def escape_witness() -> int:
    s = Counter(0)
    s.bump()
    return s.n


# --- NON-VACUITY (expected FAIL, kept OUT of this pass-file) ---
#   @mutable_state @dataclass class C: n: int
#       #@ assigns \nothing            <-- lies: the body writes self.n
#       def bump(self): self.n = self.n + 1
#   => Why3 rejects: "this expression produces an unlisted write effect".
#   The soundness hole (a3-plan.md §9: assigns \nothing passed on a mutating body)
#   is CLOSED for @mutable_state classes.
