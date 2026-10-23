r"""G29 GH3 — a ghost augmented assignment to a PARAMETER name."""
_ = 0  # anchor


#@ ensures \result == k + 6
def probe(k: int) -> int:
    #@ ghost k += 6
    y = 0
    return k


if __name__ == "__main__":
    print("CPython:", probe(1))
