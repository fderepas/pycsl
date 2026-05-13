""  # pycsl
#@ requires k >= 1
#@ ensures 1 == 1
#@ assigns \nothing
def max_sum_subarray_k(values: list, k: int) -> int:
    n = len(values)
    window_sum = 0
    j = 0
    #@ loop invariant 0 <= j and j <= k
    #@ loop variant k - j
    while j < k:
        window_sum += values[j]
        j += 1
    best = window_sum
    i = k
    #@ loop invariant 0 <= i
    #@ loop variant n - i
    while i < n:
        prev = i - k
        new_elem = values[i]
        old_elem = values[prev]
        window_sum = window_sum + new_elem - old_elem
        if window_sum > best:
            best = window_sum
        i += 1
    return best


#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def two_sum_sorted(values: list, target: int) -> tuple:
    n = len(values)
    left = 0
    right = n - 1
    found_left = -1
    found_right = -1
    #@ loop invariant 0 <= left
    #@ loop invariant right >= -1
    #@ loop invariant found_left >= -1
    #@ loop invariant found_right >= -1
    #@ loop variant right - left
    while left < right:
        current = values[left] + values[right]
        if current == target:
            found_left = left
            found_right = right
            left = right
        elif current < target:
            left += 1
        else:
            right -= 1
    return found_left, found_right


if __name__ == "__main__":
    print("max window:", max_sum_subarray_k([1, 4, 2, 10, 23, 3, 1, 0, 20], 4))
    print("two sum:", two_sum_sorted([1, 2, 4, 6, 8, 11], 10))