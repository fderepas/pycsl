""  # pycsl
#@ requires capacity >= 0
#@ ensures 1 == 1
#@ assigns \nothing
def knapsack_01(weights: list, values: list, capacity: int) -> int:
    n = len(weights)
    remaining = capacity
    total_value = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        if weights[i] <= remaining:
            remaining -= weights[i]
            total_value += values[i]
        i += 1
    return total_value


if __name__ == "__main__":
    print("best value:", knapsack_01([2, 3, 4, 5], [3, 4, 5, 8], 5))