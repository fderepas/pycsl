def factorial(n):
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return 1
    return n * factorial(n - 1)


def sum_list(values):
    if not values:
        return 0
    return values[0] + sum_list(values[1:])


if __name__ == "__main__":
    print("factorial(5):", factorial(5))
    print("sum_list:", sum_list([1, 2, 3, 4]))

