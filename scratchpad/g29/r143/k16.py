r"""G29 K16 — route #143 positive control: importer and callee module both import LIM from the
SAME constants module; allowed, and `requires k >= LIM` discharges at `g5(0)`."""
_ = 0  # anchor
from multi_file_lib.r143_consts import LIM
from multi_file_lib.r143_viaconsts import g5


#@ ensures \result == 0
#@ assigns \nothing
def caller() -> int:
    return g5(0)


if __name__ == "__main__":
    print("CPython:", caller())
