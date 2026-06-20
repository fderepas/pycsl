# Test: HAPPY ownership declarations (07-1143 R1+R2)
#
# Validates that the `#@ happy` protects/except syntax works on a
# small self-contained example modelling clock_ownership.
# - `tick()` is the sole writer of `clk.ticks` (exempt)
# - `get_pid()` only reads proc fields — no violation
# - The module should prove with zero unproven VCs.

# pycsl-flags: --memory-model hoare

#@ class invariant self.ticks >= 0
class Clock:
    def __init__(self) -> None:
        self.ticks: int = 0


#@ class invariant self.pid >= 0
class Proc:
    def __init__(self) -> None:
        self.pid: int = 1


clk = Clock()
prc = Proc()

#@ happy clock_ownership:
#@     protects clk.ticks
#@     except tick

#@ happy proc_ownership:
#@     protects prc.pid
#@     except spawn


#@ ensures clk.ticks >= \old(clk.ticks)
#@ assigns clk.ticks
def tick() -> None:
    clk.ticks = clk.ticks + 1


#@ ensures \result >= 0
#@ assigns \nothing
def get_pid() -> int:
    return prc.pid


#@ requires new_pid >= 0
#@ assigns prc.pid
def spawn(new_pid: int) -> None:
    prc.pid = new_pid


#@ ensures \result >= 0
#@ assigns \nothing
def read_clock() -> int:
    return clk.ticks
