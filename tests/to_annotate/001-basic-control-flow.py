def classify_numbers(values):
    negatives = 0
    zeros = 0
    positives = 0

    for value in values:
        if value < 0:
            negatives += 1
        elif value == 0:
            zeros += 1
        else:
            positives += 1

    return negatives, zeros, positives


def first_positive_prefix_sum(values, threshold):
    total = 0
    for value in values:
        if value <= 0:
            continue
        total += value
        if total >= threshold:
            return total
    return total


if __name__ == "__main__":
    data = [-3, 0, 5, 7, -1, 0, 2]
    print("counts:", classify_numbers(data))
    print("prefix sum:", first_positive_prefix_sum(data, threshold=10))
