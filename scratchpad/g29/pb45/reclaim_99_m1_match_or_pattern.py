_ = 0  # anchor


#@ ensures \result == 99
def probe(x: int) -> int:
    match x:
        case 1 | 2:
            return 1
        case _:
            return 0
