def array_max(arr: list, n: int) -> int:
    result = arr[0]
    i = 1
    while i < n:
        if arr[i] > result:
            result = arr[i]
        i += 1
    return result


def array_min(arr: list, n: int) -> int:
    result = arr[0]
    i = 1
    while i < n:
        if arr[i] < result:
            result = arr[i]
        i += 1
    return result
