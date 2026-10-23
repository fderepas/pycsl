r"""G29 LP3 — `continue` skipping the increment of an accumulator."""
_ = 0  # anchor


#@ ensures \result == 5
def probe() -> int:
    t = 0
    #@ loop invariant 0 <= t and t <= i
    for i in range(5):
        if i == 1:
            continue
        t += 1
    return t


if __name__ == "__main__":
    print("CPython:", probe())
