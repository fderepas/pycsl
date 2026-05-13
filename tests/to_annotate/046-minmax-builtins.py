def clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(value, hi))


def bounded_sum(arr: list, n: int, cap: int) -> int:
    total = 0
    i = 0
    while i < n:
        total += min(arr[i], cap)
        i += 1
    return total


def array_max_bounded(arr: list, n: int, bound: int) -> int:
    best = arr[0]
    i = 1
    while i < n:
        best = max(best, arr[i])
        i += 1
    return min(best, bound)


def midpoint(a: int, b: int) -> int:
    lo = min(a, b)
    hi = max(a, b)
    return lo + (hi - lo) // 2
