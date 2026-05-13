def knapsack_01(weights, values, capacity):
    if len(weights) != len(values):
        raise ValueError("weights and values must have same length")
    n = len(weights)
    dp = [[0 for _ in range(capacity + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        w = weights[i - 1]
        v = values[i - 1]
        for cap in range(capacity + 1):
            dp[i][cap] = dp[i - 1][cap]
            if w <= cap:
                with_item = dp[i - 1][cap - w] + v
                if with_item > dp[i][cap]:
                    dp[i][cap] = with_item
    return dp[n][capacity]


if __name__ == "__main__":
    print("best value:", knapsack_01([2, 3, 4, 5], [3, 4, 5, 8], 5))

