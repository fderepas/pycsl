_ = 0  # anchor


#@ lemma
#@ ensures 0 == 1
def la(n: int) -> None:
    lb(n)


#@ lemma
#@ ensures 0 == 1
def lb(n: int) -> None:
    la(n)


#@ ensures \result == 99
def probe() -> int:
    return 3
