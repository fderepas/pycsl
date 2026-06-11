"""multi_file_lib.inductive_fs — a gap-7-shaped filesystem-name view (cross-module
inductive-predicate fixture for 11-0632-spec-8).

`present` is a module-level `#@ inductive` LOGIC predicate that a mutator (`mkdir`)
establishes and an observer (`access`) reflects. Both public contracts reference it.
When this module is imported by a driver (`0703.py`), the dependency's inductive decl
must cross the `from … import …` boundary so the driver's emitted WhyML carries the
real `inductive present string = …` block (not a program `val present_1 (int):int`).
"""
_ = 0  # anchor


#@ inductive present(name: str):
#@     present_intro: \forall n: str; present(n) ==> present(n)


#@ \trusted reviewer: pycsl-reference-fixture
#@ ensures \result == 0 or \result == -1
#@ ensures \result == 0 ==> present(filepath)
def mkdir(filepath: str, mode: int) -> int:
    return 0


#@ \trusted reviewer: pycsl-reference-fixture
#@ ensures \result == 1 or \result == 0
#@ ensures (\result == 1) <==> present(filepath)
def access(filepath: str, mode: int) -> int:
    return 1
