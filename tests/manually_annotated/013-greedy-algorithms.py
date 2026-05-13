""  # pycsl
#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def select_max_non_overlapping(starts: list, ends: list) -> int:
    n = len(starts)
    count = 0
    last_end = -1
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant count >= 0
    #@ loop variant n - i
    while i < n:
        if starts[i] >= last_end:
            count += 1
            last_end = ends[i]
        i += 1
    return count


if __name__ == "__main__":
    starts = [1, 2, 4, 1, 5, 8]
    ends = [3, 5, 7, 8, 9, 9]
    print("count:", select_max_non_overlapping(starts, ends))