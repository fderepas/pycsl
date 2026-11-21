_n = [0]


#@ \trusted
#@ ensures True
def Path(s: str) -> int:
    _n[0] += 1
    return _n[0]
