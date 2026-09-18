# ROUTE #188 — route #166's disambiguating stub suffix is a 100000-bucket hash, and a collision puts #166 back

**Status: REPAIR DRAFTED by gen #29 (worktree wtAI, branch wip/g29-r188, on top of #187).** Severity 1.
Generator: carrier-rerun of the landed #166, read for the assumption its repair makes.

## Measured at `8a30d42f`

    class C:  #@ ensures \result == 1     def get(self) -> int: return 1
    class D:  #@ ensures \result == 123   def get(self) -> int: return 123
    class E:  #@ ensures \result == 441   def get(self) -> int: return 441

    #@ ensures \result == 1     def f() -> int:  o = C(); return o.get()
    #@ ensures \result == 123   def g() -> int:  o = D(); return o.get()
    #@ ensures \result == 123   def h() -> int:  o = E(); return o.get()    PROVED (CPython 441)

Route #166 gives a clashing abstract-stub name a suffix `_c{stable_hash(decl) % 100000}`, and
`_add_abstract_op` **still** resolves a same-name/different-declaration clash by keeping the LONGER
declaration (`abstract_ops.py`, "Same arity but different declaration — keep longer"). So two callees
whose suffixes collide share one stub and one contract — route #166 exactly, one indirection later.

The collision is not luck: the declaration format is
`val o_get_0 () : int\n    ensures { (result = N) }`, so the pair `N = 123` / `N = 441` (both
`_c84185`) falls out of a few hundred candidates. 100000 buckets means a birthday collision at a few
hundred distinct stubs of one base name.

## Repair (draft)

The suffix is made INJECTIVE per base name: a declaration keeps the name it was first given (a map
from `(base, declaration)` to the chosen name), and a different declaration landing on a taken name is
pushed to the next free `_2`, `_3`, …. Emission is unchanged wherever no two declarations collide,
which is every file in the corpus today. Witness 1664 (XFAIL), 1665 (PASS control — all three call
sites keep their own callee's contract); 1566/1567/1568 unchanged.

**The general lesson, worth carrying to the next generator: a hash-derived NAME is not a
disambiguator unless the collision case is handled.** Every other `stable_hash(...) % <modulus>` in
the emitter is a candidate for the same reading — `_<fn>_fold_<h % 100000>` and
`strfold_<fn>_<h % 100000>` in `expressions.py` are the two others at this modulus.
