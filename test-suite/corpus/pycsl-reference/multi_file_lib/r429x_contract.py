# run #8 u59, route #429 (review rt71): a dependency whose CONTRACT holds a non-Latin-1 literal.
#@ ensures \result == "€"
#@ assigns \nothing
def h() -> str:
    return "€"
