"""os.path.exists() — total function, never raises, returns bool (0 or 1)."""
# pycsl-flags: --no-proof
_ = 0  # anchor
import os.path  # noqa: F401


#@ \trusted
#@ requires True
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def check_exists(p: int) -> int:
    return os.path.exists(p)


if __name__ == "__main__":
    pass
