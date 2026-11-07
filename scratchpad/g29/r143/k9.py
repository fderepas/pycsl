r"""G29 k9 — route #143 carrier-rerun on gen #29's own refusal: control: LIM imported from the SAME module alongside f (no refusal; the proof must fail because f raises)."""
_ = 0  # anchor
from multi_file_lib.r141_raiselib import f, LIM


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f(k)


if __name__ == "__main__":
    print("CPython:", caller(3))
