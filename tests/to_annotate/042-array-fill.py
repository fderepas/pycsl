def fill_zeros(arr: list, n: int) -> None:
    i = 0
    while i < n:
        arr[i] = 0
        i += 1


def fill_value(arr: list, n: int, val: int) -> None:
    i = 0
    while i < n:
        arr[i] = val
        i += 1
