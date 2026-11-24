#@ lemma
#@ requires n >= 0
#@ ensures n >= 0
#@ \variant n
#@ assigns \nothing
def la(n: int) -> None:
    if n > 0:
        lb(n - 1)

#@ lemma
#@ requires n >= 0 and n < 0
#@ ensures n == 99
#@ \variant n
#@ assigns \nothing
def lb(n: int) -> None:
    if n > 0:
        la(n - 1)
