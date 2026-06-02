#@ requires n >= 0
#@ ensures (n <= \length(arr)) ==> (\result >= 0)
#@ assigns \nothing
def array_fill_zero(arr: list, n: int) -> int:
    i = 0
    while i < n:
        arr[i] = 0
        i = i + 1
    return n
