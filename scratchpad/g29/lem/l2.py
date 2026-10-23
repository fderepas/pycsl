r"""G29 LEM2 — a `#@ lemma` whose body LOOPS FOREVER."""
_ = 0  # anchor


#@ lemma
#@ ensures False
#@ assigns \nothing
def bogus() -> None:
    while True:
        pass


#@ ensures \result == 7
def probe() -> int:
    return 1


if __name__ == "__main__":
    print("CPython:", probe())
