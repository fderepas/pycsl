r"""Test 1873 — gen #31 FALSE TWIN of 1872 (expected FAIL): the import is not a free pass.

Byte-identical to 1872 except that the method claims `\result == 1` for a body that returns
0. The import fix adds a `use` line and nothing else; a file that now TYPECHECKS must still
be PROVED, and this is the file that says so.

THE FIRST VERSION OF THIS TWIN WAS WRONG, and the way it was wrong is worth keeping. It
claimed `#@ class invariant \length(self.xs) == 1024` for a field initialised to `[]`,
expecting a refusal — and it VERIFIED. The emitted record is

    type c = { mutable xs: array int }
      invariant { ((Array.length xs) = 1024) }
      by { xs = (Array.make 1024 0) }

i.e. **the inhabitation witness is synthesized FROM THE INVARIANT**, not from what
`__init__` actually assigns, so a length invariant is inhabitable whatever it says. Probed
one step further and the obvious escalation does NOT follow: a method returning
`len(self.xs)` with `#@ ensures \result == 1024` FAILS. Recorded in the backlog as an
observation to finish rather than left as a twin that proves the opposite of its name.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ class invariant \length(self.xs) == 0
class C:
    def __init__(self) -> None:
        self.xs: list = []

    #@ ensures \result == 1
    #@ assigns \nothing
    def n(self) -> int:
        return 0
