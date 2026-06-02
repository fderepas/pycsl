def array_sum_nonneg(arr: list, n: int) -> int:
    s = 0
    i = 0
    while i < n:
        s = s + arr[i]
        i = i + 1
    return s
