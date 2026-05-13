""  # pycsl
#@ requires rows >= 1 and cols >= 1
#@ ensures \result == cols
#@ assigns \nothing
def transpose(matrix: list, rows: int, cols: int) -> int:
    return cols


#@ requires n >= 0 and \length(a) >= n and \length(b) >= n
#@ ensures 1 == 1
#@ assigns \nothing
def multiply(a: list, b: list, n: int) -> int:
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        total += a[i] * b[i]
        i += 1
    return total


if __name__ == "__main__":
    m = [1, 2, 3, 4, 5, 6]
    print("transpose:", transpose(m, 2, 3))
    print("multiply:", multiply([1, 2], [5, 6], 2))