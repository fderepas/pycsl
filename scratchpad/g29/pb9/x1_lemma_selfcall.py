_ = 0  # anchor


#@ lemma
#@ ensures 1 == 0
def bogus() -> None:
    bogus()


#@ ensures \result == 7
def probe() -> int:
    return 3
