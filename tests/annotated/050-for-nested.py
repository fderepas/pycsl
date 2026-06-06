""  # pycsl
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def matrix_row_sum(row: list, m: int) -> int:
    total = 0
    i = 0
    n = len(row)
    #@ loop invariant 0 <= i and i <= \length(row)
    #@ loop invariant \length(row) == 0 ==> total == 0
    #@ loop variant \length(row) - i
    while i < n:
        total += row[i]
        i += 1
    return total


#@ requires n >= 0
#@ requires \length(a) >= n
#@ requires \length(b) >= n
#@ ensures 1 == 1
#@ assigns \nothing
#@ requires n <= \length(a)
#@ requires n <= \length(b)
def dot_product(a: list, b: list, n: int) -> int:
    total = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        total += a[i] * b[i]
        i += 1
    return total
