r"""Test 1844 — gen #31: a call BETWEEN two `#@ verify_module` groups (expected PASS).

annotations.md row 29 promises that "a cross-module `self.<m>(...)` call (a sibling in a
DIFFERENT `#@ verify_module` group, or the flat default module) is lowered to the PROVEN
contract of the callee via Why3 module `clone`-refinement". The flat-caller half worked.
The sibling-in-another-group half did not, and the cause was one missing line: the
expression layer correctly rewrites the call to `LeafSig.c__leaf`, `PyCSL_Program` was
given `use <G>Sig` for every group, and a GROUP module was given `use Shared` and nothing
else — so the qualified name named a module the enclosing module never imported:

    module Top
      use Shared
      let c__caller (self: c) : int = (LeafSig.c__leaf self)
                                       ^ unbound function or predicate symbol

Repaired by emitting ALL `<G>Sig` modules first and THEN all providers, each provider
using every other group's Sig. The order matters: Why3 needs a module defined earlier in
the file than its use, and the old interleaved order could not satisfy two groups that
each need the other. A `<G>Sig` is bodyless `val`s over `Shared`, so the Sig layer is
acyclic however the groups call each other — see 1846 for the mutually-recursive case.

Here `leaf` is in `LeafMod` and `caller` is in `TopMod`, and `caller` proves `\result >= 0`
— exactly what `leaf`'s CONTRACT gives. 1845 is the negative twin: the same file claiming
`\result >= 7`, the body's actual value, which must FAIL because a module boundary conveys
the contract and not the body.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class C:
    def __init__(self) -> None:
        self.n: int = 0

    #@ verify_module LeafMod
    #@ ensures \result >= 0
    #@ assigns \nothing
    def leaf(self) -> int:
        return 7

    #@ verify_module TopMod
    #@ ensures \result >= 0
    #@ assigns \nothing
    def caller(self) -> int:
        return self.leaf()
