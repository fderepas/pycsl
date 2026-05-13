def linear_search(values, target):
    for index, value in enumerate(values):
        if value == target:
            return index
    return -1


def binary_search(sorted_values, target):
    left = 0
    right = len(sorted_values) - 1
    while left <= right:
        mid = (left + right) // 2
        value = sorted_values[mid]
        if value == target:
            return mid
        if value < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1


if __name__ == "__main__":
    data = [2, 4, 6, 8, 10, 12]
    print("linear:", linear_search(data, 8))
    print("binary:", binary_search(data, 8))

