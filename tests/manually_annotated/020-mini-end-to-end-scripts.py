""  # pycsl
#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def count_non_empty_lines(lines: list) -> int:
    n = len(lines)
    count = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant count >= 0
    #@ loop invariant count <= i
    #@ loop variant n - i
    while i < n:
        if lines[i] > 0:
            count += 1
        i += 1
    return count


#@ requires 1 == 1
#@ ensures \result == 0
#@ assigns \nothing
def main() -> int:
    return 0


if __name__ == "__main__":
    main()