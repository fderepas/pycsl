r"""G29 K15 — route #143 positive control: importer and callee module both import LIM from the
SAME constants module, so it is one binding; allowed (and the proof fails because f4 raises)."""
_ = 0  # anchor
from multi_file_lib.r143_consts import LIM
from multi_file_lib.r143_viaconsts import f4


#@ requires k >= 0
#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    return f4(k) + LIM


if __name__ == "__main__":
    print("CPython:", caller(3))
