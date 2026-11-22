# u70 helper (routes #624 / #625, review rt77 F1 / F2): imported by witnesses 10420-10427 from the
# program's directory. Its `val1` returns 1 and its `helper` returns 1.


#@ ensures \result == 1
#@ assigns \nothing
def val1() -> int:
    return 1


#@ ensures \result == 1
#@ assigns \nothing
def helper() -> int:
    return 1
