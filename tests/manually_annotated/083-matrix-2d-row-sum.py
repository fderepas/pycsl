""  # pycsl
#@ requires \length2d(a, m, n)
#@ requires \valid(sums, m)
#@ requires m >= 0
#@ requires n >= 0
def matrix_row_sum(a, sums, m, n):
    #@ loop invariant 0 <= i and i <= m
    #@ loop variant m - i
    for i in range(m):
        s = 0
        #@ loop invariant 0 <= j and j <= n
        #@ loop variant n - j
        for j in range(n):
            s = s + a[i][j]
        sums[i] = s
