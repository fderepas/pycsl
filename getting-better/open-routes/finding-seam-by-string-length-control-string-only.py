from typing import Set


#@ requires True
#@ ensures True
def only_string() -> int:
    s = set()          # string-keyed set ALONE -> only the POLY arm registers
    s.add("a")
    return 0
