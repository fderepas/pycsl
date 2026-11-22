# u66 control 10383 (review rt76 r14): a regular package zh80 in the first --import-path root that DEFINES
# `b`; `from zh80 import b` takes this attribute and CPython never imports a submodule `zh80.b`.


#@ ensures \result == 1
#@ assigns \nothing
def b() -> int:
    return 1
