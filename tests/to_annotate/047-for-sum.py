def for_sum(arr: list, n: int) -> int:
    total = 0
    for item in arr:
        total += item
    return total


def for_product(arr: list, n: int) -> int:
    result = 1
    for item in arr:
        result *= item
    return result
