def all_positive(arr: list, n: int) -> bool:
    for item in arr:
        if item <= 0:
            return False
    return True


def any_negative(arr: list, n: int) -> bool:
    for item in arr:
        if item < 0:
            return True
    return False


def none_zero(arr: list, n: int) -> bool:
    for item in arr:
        if item == 0:
            return False
    return True
