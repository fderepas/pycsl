def copy_array(src: list, dst: list, n: int) -> None:
    i = 0
    while i < n:
        dst[i] = src[i]
        i += 1


def copy_reverse(src: list, dst: list, n: int) -> None:
    i = 0
    while i < n:
        dst[i] = src[n - 1 - i]
        i += 1
