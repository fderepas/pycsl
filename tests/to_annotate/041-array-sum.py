def array_sum(arr: list, n: int) -> int:
    total = 0
    i = 0
    while i < n:
        total += arr[i]
        i += 1
    return total


def array_all_positive(arr: list, n: int) -> bool:
    i = 0
    while i < n:
        if arr[i] <= 0:
            return False
        i += 1
    return True
