r"""G29 LP2 — `return` from inside a for loop over range; the post-loop code is unreachable for that path."""
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    for i in range(5):
        if i == 2:
            return i
    return 5


if __name__ == "__main__":
    print("CPython:", probe())
