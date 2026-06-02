#@ ensures \result == (\str_length(s) + \str_length(t))
#@ assigns \nothing
def concat_length(s: str, t: str) -> int:
    return len(s) + len(t)
