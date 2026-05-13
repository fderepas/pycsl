def count_positive(arr: list, n: int) -> int:
    count = 0
    for item in arr:
        if item > 0:
            count += 1
    return count


def count_in_range(arr: list, n: int, lo: int, hi: int) -> int:
    count = 0
    for item in arr:
        if item >= lo and item <= hi:
            count += 1
    return count
