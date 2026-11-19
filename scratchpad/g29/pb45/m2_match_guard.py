_ = 0  # anchor


#@ ensures \result == 1
def probe(x: int) -> int:
    match x:
        case n if n > 5:
            return 1
        case _:
            return 0
