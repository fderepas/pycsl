""  # pycsl
#@ requires n >= 1
#@ ensures \result >= 1
#@ assigns \nothing
def factorial(n: int) -> int:
    k = n
    acc = 1
    #@ loop invariant k >= 0
    #@ loop invariant acc >= 1
    #@ loop variant k
    while k > 1:
        acc *= k
        k -= 1
    return acc


#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def sum_list(values: list) -> int:
    n = len(values)
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        total += values[i]
        i += 1
    return total


if __name__ == "__main__":
    print("factorial(5):", factorial(5))
    print("sum_list:", sum_list([1, 2, 3, 4]))