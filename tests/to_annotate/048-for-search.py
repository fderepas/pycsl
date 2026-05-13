def for_search(arr: list, n: int, target: int) -> int:
    idx = 0
    for item in arr:
        if item == target:
            return idx
        idx += 1
    return -1


def for_last_occurrence(arr: list, n: int, target: int) -> int:
    result = -1
    idx = 0
    for item in arr:
        if item == target:
            result = idx
        idx += 1
    return result
