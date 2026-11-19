r"""G29 LP1 — `break` out of a while loop: after the loop, NOT(cond) does not hold."""
_ = 0  # anchor


#@ ensures \result == 10
def probe() -> int:
    i = 0
    #@ loop invariant 0 <= i and i <= 10
    #@ loop variant 10 - i
    while i < 10:
        if i == 3:
            break
        i += 1
    return i


if __name__ == "__main__":
    print("CPython:", probe())
