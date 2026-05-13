""  # pycsl
#@ requires \length2d(a, n, n)
#@ requires n >= 0
def matrix_zero_diagonal(a, n):
    result = 1
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    for i in range(n):
        if a[i][i] != 0:
            result = 0
    return result
