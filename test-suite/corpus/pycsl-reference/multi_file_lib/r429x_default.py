# run #8 u59, route #429 (review rt71): a dependency whose only non-Latin-1 text is a
# parameter DEFAULT (no literal of its own emission holds it).
#@ ensures \result == s
#@ assigns \nothing
def h3(s: str = "€") -> str:
    return s
