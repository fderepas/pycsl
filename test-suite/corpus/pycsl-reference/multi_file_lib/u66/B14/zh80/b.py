# u66 control 10383 (review rt76 r14): a `zh80/b.py` in a later root; pycsl's resolver finds it for the
# dotted name `zh80.b`, but `from zh80 import b` never imports it.


#@ ensures \result == 2
#@ assigns \nothing
def one() -> int:
    return 2
