""  # pycsl
#@ requires n >= 0
#@ ensures \result >= 1
#@ assigns \nothing
def factorial(n: int) -> int:
    if n < 0:
        pass
    if n <= 1:
        return 1
    return n * factorial(n - 1)


#@ requires 1 == 1
#@ ensures \result >= 0 or \result < 0
#@ assigns \nothing
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def sum_list(values: list) -> int:
    n = len(values)
    total = 0
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop variant n - i
    while i < n:
        total += values[i]
        i += 1
    return total


if __name__ == "__main__":
    print("factorial(5):", factorial(5))
    print("sum_list:", sum_list([1, 2, 3, 4]))

