""  # pycsl
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def first_duplicate(values: list) -> int:
    n = len(values)
    i = 0
    found = -1
    found_flag = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant found_flag >= 0
    #@ loop variant n - i
    while i < n:
        j = 0
        #@ loop invariant 0 <= j and j <= i
        #@ loop invariant found_flag >= 0
        #@ loop variant i - j
        while j < i:
            if values[j] == values[i]:
                found = values[i]
                found_flag = 1
                j = i
            else:
                j += 1
        if found_flag == 1:
            i = n
        else:
            i += 1
    return found


#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def group_anagrams(keys: list) -> int:
    n = len(keys)
    count = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant count >= 0
    #@ loop variant n - i
    while i < n:
        j = 0
        is_new = 1
        #@ loop invariant 0 <= j and j <= i
        #@ loop invariant is_new >= 0
        #@ loop variant i - j
        while j < i:
            if keys[j] == keys[i]:
                is_new = 0
                j = i
            else:
                j += 1
        if is_new == 1:
            count += 1
        i += 1
    return count


if __name__ == "__main__":
    print("first duplicate:", first_duplicate([3, 1, 4, 2, 4, 5]))
    print("distinct group count:", group_anagrams([1, 2, 1, 3, 2, 4]))