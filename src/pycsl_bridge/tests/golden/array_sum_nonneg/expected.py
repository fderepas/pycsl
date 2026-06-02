#@ proof rocq: array_sum_nonneg_nonneg
#@ proof lean: array_sum_nonneg_nonneg
#@ requires n >= 0
#@ ensures (n <= \length(arr)) ==> (\result >= 0)
#@ assigns \nothing
def array_sum_nonneg(arr: list, n: int) -> int:
    s = 0
    i = 0
    while i < n:
        s = s + arr[i]
        i = i + 1
    return s
