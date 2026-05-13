""  # pycsl
#@ requires \length2d(a, m, n)
#@ requires m >= 0
#@ requires n >= 0
def matrix_scale(a, m, n, factor):
    #@ loop invariant 0 <= i and i <= m
    #@ loop variant m - i
    for i in range(m):
        #@ loop invariant 0 <= j and j <= n
        #@ loop variant n - j
        for j in range(n):
            a[i][j] = a[i][j] * factor
