#@ requires True
#@ ensures True
#@ assigns \nothing
def scan_keys(s: str) -> int:
    n = 0
    for k in ("body", "orelse"):
        if s.startswith(k):
            n = n + 1
    return n
