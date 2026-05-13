""  # pycsl
#@ requires 1 == 1
#@ ensures \result >= -1
#@ assigns \nothing
def linear_search(values: list, target: int) -> int:
    n = len(values)
    i = 0
    found = -1
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant found >= -1
    #@ loop variant n - i
    while i < n:
        if values[i] == target:
            found = i
            i = n
        else:
            i += 1
    return found


#@ requires 1 == 1
#@ ensures \result >= -1
#@ assigns \nothing
def binary_search(sorted_values: list, target: int) -> int:
    n = len(sorted_values)
    left = 0
    right = n - 1
    found = -1
    #@ loop invariant 0 <= left
    #@ loop invariant right >= -1
    #@ loop invariant right <= n - 1
    #@ loop invariant found >= -1
    #@ loop variant right - left + 1
    while left <= right:
        mid = (left + right) // 2
        value = sorted_values[mid]
        if value == target:
            found = mid
            left = right + 1
        elif value < target:
            left = mid + 1
        else:
            right = mid - 1
    return found


if __name__ == "__main__":
    data = [2, 4, 6, 8, 10, 12]
    print("linear:", linear_search(data, 8))
    print("binary:", binary_search(data, 8))