r"""K2-CTL — the MODULE-LEVEL spelling, where `func` really is a bare name: must be REJECTED
with the no-trust-leakage error."""
_ = 0  # anchor


#@ \trusted
#@ ensures \result == 1 and \result == 2
#@ assigns \nothing
def bogus() -> int:
    return 1


#@ lemma
#@ ensures 1 == 2
#@ assigns \nothing
def leak() -> None:
    x = bogus()
