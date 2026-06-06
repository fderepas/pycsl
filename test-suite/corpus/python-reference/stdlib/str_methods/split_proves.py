"""str.split() — returns a list; modeled as a non-negative integer length."""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ \trusted
#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def split_count(s: str, sep: str) -> int:
    return len(s.split(sep))


if __name__ == "__main__":
    pass
