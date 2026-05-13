def scale_array(arr: list, n: int, factor: int) -> None:
    i = 0
    while i < n:
        arr[i] = arr[i] * factor
        i += 1


def clamp_array(arr: list, n: int, lo: int, hi: int) -> None:
    i = 0
    while i < n:
        if arr[i] < lo:
            arr[i] = lo
        if arr[i] > hi:
            arr[i] = hi
        i += 1
