def max_sum_subarray_k(values, k):
    if k <= 0 or k > len(values):
        raise ValueError("k must be in range 1..len(values)")
    window_sum = sum(values[:k])
    best = window_sum
    for i in range(k, len(values)):
        window_sum += values[i] - values[i - k]
        if window_sum > best:
            best = window_sum
    return best


def two_sum_sorted(values, target):
    left = 0
    right = len(values) - 1
    while left < right:
        current = values[left] + values[right]
        if current == target:
            return left, right
        if current < target:
            left += 1
        else:
            right -= 1
    return None


if __name__ == "__main__":
    print("max window:", max_sum_subarray_k([1, 4, 2, 10, 23, 3, 1, 0, 20], 4))
    print("two sum:", two_sum_sorted([1, 2, 4, 6, 8, 11], 10))

