r"""Route #615 witness program (NOT a corpus file: it needs the PATH-prepended why3 wrapper in
./bin, mode R615_MODE=kill-main). Expected verdict WITHOUT the wrapper: FAIL — `cube_sum`'s
postcondition is Fermat's n = 3 case, true but beyond the SMT solvers, so it times out.
With the wrapper, the MAIN full-file why3 run is SIGKILLed right after its first goal record
(the easy `succ` goal) reaches stdout. BASE (pre-#615): if why3 streams that record, the
dispatcher early-exits on an all-Valid PREFIX and reports SUCCESS. HEAD: the dead run fails.
"""
#@ requires x >= 0
#@ ensures \result == x + 1
#@ assigns \nothing
def succ(x: int) -> int:
    return x + 1

#@ requires a > 0 and b > 0 and c > 0
#@ ensures a * a * a + b * b * b != c * c * c
#@ assigns \nothing
def cube_sum(a: int, b: int, c: int) -> int:
    return 0
