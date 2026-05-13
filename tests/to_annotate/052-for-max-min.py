def for_max(arr: list, n: int) -> int:
    best = arr[0]
    for item in arr:
        if item > best:
            best = item
    return best


def for_min(arr: list, n: int) -> int:
    best = arr[0]
    for item in arr:
        if item < best:
            best = item
    return best
