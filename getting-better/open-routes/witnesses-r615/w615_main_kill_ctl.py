r"""Route #615 witness program (NOT a corpus file: it needs the PATH-prepended why3 wrapper in
./bin, mode R615_MODE=kill-main). Expected verdict WITHOUT the wrapper: FAIL — `z_cube_sum`'s
postcondition is Fermat's n = 3 case, true but beyond the SMT solvers: Z3 times out on it.
With the wrapper, the MAIN full-file why3 run is SIGKILLed right after its first goal record
reaches stdout. That record is the easy `a_succ` goal: the emitter puts `a_succ` first (it is
first both by name and in reverse source order, the two orders measured on this program).
BASE (pre-#615): why3 STREAMS its --json records, so the dispatcher sees an all-Valid PREFIX,
early-exits with rc 0 and reports SUCCESS on one goal. HEAD: the signal-killed run fails.
"""
#@ requires a > 0 and b > 0 and c > 0
#@ ensures a * a * a + b * b * b != c * c * c
#@ assigns \nothing
def z_cube_sum(a: int, b: int, c: int) -> int:
    return 0

#@ requires x >= 0
#@ ensures \result == x + 1
#@ assigns \nothing
def a_succ(x: int) -> int:
    return x + 1
