"""1178 — ROUTE #74 NEGATIVE: a str-predicate NAME must not shadow a user class method.

`_call_named_builtins` matched on the METHOD-NAME SUFFIX alone, with the receiver ERASED,
and is consulted BEFORE `_handle_dotted_call` — so a user class whose method carries one of
twelve ordinary English names (islower, isdigit, startswith, endswith, ...) had it replaced
by `val self_isdigit_0 () : int ensures { ((result = 0) || (result = 1)) }`. Note the EMPTY
parameter list: the receiver is gone, so nothing tied the axiom to any object.

CPython answers 7. Before the fix `\\result <= 1` PROVED, with the user's real
`let c__isdigit` emitted in the same file and never used.

ANTI-VACUITY is carried by 1179: the TRUE claim about this same program PROVES.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0


class C:
    #@ ensures \result == 7
    #@ assigns \nothing
    def isdigit(self) -> int:
        return 7

    #@ ensures \result <= 1
    #@ assigns \nothing
    def g(self) -> int:
        return self.isdigit()
