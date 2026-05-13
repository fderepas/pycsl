def linear_search(arr: list, n: int, target: int) -> int:
    i = 0
    while i < n:
        if arr[i] == target:
            return i
        i += 1
    return -1


def contains(arr: list, n: int, target: int) -> bool:
    i = 0
    while i < n:
        if arr[i] == target:
            return True
        i += 1
    return False
