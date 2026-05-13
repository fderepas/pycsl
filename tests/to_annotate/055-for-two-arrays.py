def prefix_sum(src: list, dst: list, n: int) -> None:
    acc = 0
    i = 0
    while i < n:
        acc += src[i]
        dst[i] = acc
        i += 1


def running_max(src: list, dst: list, n: int) -> None:
    best = src[0]
    i = 0
    while i < n:
        if src[i] > best:
            best = src[i]
        dst[i] = best
        i += 1
