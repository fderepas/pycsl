#@ requires True
#@ ensures True
def int_only() -> int:
    si = set()         # int-keyed set ALONE -> only the MONO arm registers
    si.add(1)
    return 0
