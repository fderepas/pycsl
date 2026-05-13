def matrix_row_sum(row: list, m: int) -> int:
    total = 0
    for item in row:
        total += item
    return total


def dot_product(a: list, b: list, n: int) -> int:
    total = 0
    i = 0
    while i < n:
        total += a[i] * b[i]
        i += 1
    return total
