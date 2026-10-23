r"""G29 LEM1 — a `#@ lemma` whose body RAISES, "proving" ensures False; then used."""
_ = 0  # anchor


#@ lemma
#@ ensures False
#@ assigns \nothing
def bogus() -> None:
    raise ValueError


#@ ensures \result == 7
def probe() -> int:
    bogus()
    return 1


if __name__ == "__main__":
    print("CPython:", probe())
