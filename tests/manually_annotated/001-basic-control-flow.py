#@ ensures \result[0] >= 0
#@ ensures \result[1] >= 0
#@ ensures \result[2] >= 0
#@ ensures \result[0] + \result[1] + \result[2] == n
#@ assigns \nothing
def classify_numbers(values: list) -> tuple:
    negatives = 0
    zeros = 0
    positives = 0
    n = len(values)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant negatives >= 0
    #@ loop invariant zeros >= 0
    #@ loop invariant positives >= 0
    #@ loop invariant negatives + zeros + positives == i
    #@ loop variant n - i
    while i < n:
        if values[i] < 0:
            negatives += 1
        elif values[i] == 0:
            zeros += 1
        else:
            positives += 1
        i += 1
    return negatives, zeros, positives


#@ requires threshold > 0
#@ ensures \result >= 0
#@ assigns \nothing
def first_positive_prefix_sum(values: list, threshold: int) -> int:
    total = 0
    n = len(values)
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant total >= 0
    #@ loop variant n - i
    while i < n:
        if values[i] <= 0:
            i += 1
            continue
        total += values[i]
        if total >= threshold:
            i = n
        else:
            i += 1
    return total


if __name__ == "__main__":
    data = [-3, 0, 5, 7, -1, 0, 2]
    print("counts:", classify_numbers(data))
    print("prefix sum:", first_positive_prefix_sum(data, threshold=10))
