def insertion_sort(values):
    result = values[:]
    for i in range(1, len(result)):
        key = result[i]
        j = i - 1
        while j >= 0 and result[j] > key:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = key
    return result


def is_sorted_non_decreasing(values):
    for i in range(1, len(values)):
        if values[i - 1] > values[i]:
            return False
    return True


if __name__ == "__main__":
    items = [5, 2, 4, 6, 1, 3]
    ordered = insertion_sort(items)
    print("sorted:", ordered)
    print("is_sorted:", is_sorted_non_decreasing(ordered))

