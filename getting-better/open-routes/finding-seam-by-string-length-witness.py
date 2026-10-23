#@ requires True
#@ ensures True
def both_kappas() -> int:
    si = set()         # int-keyed set    -> _set_kappa != "string" -> MONO arm
    si.add(1)
    ss = set()         # string-keyed set -> _set_kappa == "string" -> POLY arm
    ss.add("a")
    return 0
