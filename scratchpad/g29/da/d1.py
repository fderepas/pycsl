r"""G29 D1 — deferral-audit expressions.py:5778: "a mixed `+` ... only programs whose WhyML was
already rejected at L3-tc". A GENUINELY mixed str + int raises TypeError in CPython."""
_ = 0  # anchor


#@ requires True
#@ ensures True
#@ no_exception TypeError
#@ assigns \nothing
def f(k: int) -> int:
    s = "ab" + k
    return 1


if __name__ == "__main__":
    print("CPython:", f(3))
