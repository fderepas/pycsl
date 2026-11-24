# u71 witness 10438 helper (review rt79 z1, route #627): the module pycsl reads from the SECOND
# --import-path entry (a directory).
#@ ensures \result == 1
#@ assigns \nothing
def one() -> int:
    return 1
