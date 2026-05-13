def sum_skip_negative(arr: list, n: int) -> int:
    total = 0
    for item in arr:
        if item < 0:
            continue
        total += item
    return total


def sum_skip_zero(arr: list, n: int) -> int:
    total = 0
    for item in arr:
        if item == 0:
            continue
        total += item
    return total
