""  # pycsl
#@ requires \length2d(a, m, n)
#@ requires \length2d(b, m, n)
#@ requires \length2d(c, m, n)
#@ requires m >= 0
#@ requires n >= 0
def matrix_add(a, b, c, m, n):
    #@ loop invariant 0 <= i and i <= m
    #@ loop variant m - i
    for i in range(m):
        #@ loop invariant 0 <= j and j <= n
        #@ loop variant n - j
        for j in range(n):
            c[i][j] = a[i][j] + b[i][j]
