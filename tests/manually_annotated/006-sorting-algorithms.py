""  # pycsl
#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def insertion_sort(values: list) -> int:
    n = len(values)
    inversions = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant inversions >= 0
    #@ loop variant n - i
    while i < n:
        j = i + 1
        #@ loop invariant i + 1 <= j and j <= n
        #@ loop invariant inversions >= 0
        #@ loop variant n - j
        while j < n:
            if values[i] > values[j]:
                inversions += 1
            j += 1
        i += 1
    return inversions


#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def is_sorted_non_decreasing(values: list) -> int:
    n = len(values)
    i = 0
    flag = 1
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant flag >= 0
    #@ loop variant n - i
    while i < n - 1:
        if values[i] > values[i + 1]:
            flag = 0
            i = n
        else:
            i += 1
    return flag


if __name__ == "__main__":
    items = [5, 2, 4, 6, 1, 3]
    ordered = insertion_sort(items)
    print("sorted:", ordered)
    print("is_sorted:", is_sorted_non_decreasing(ordered))