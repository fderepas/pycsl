"""String Algorithms 2: Edit Distance and Alignment"""


def hamming_distance(s1: str, s2: str) -> int:
    """Compute the Hamming distance between two equal-length strings.
    Counts positions where corresponding characters differ."""
    assert len(s1) == len(s2), "Strings must have equal length"
    dist = 0
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            dist += 1
    return dist


def levenshtein_distance(s1: str, s2: str) -> int:
    """Compute the Levenshtein (edit) distance between two strings.
    Allowed operations: insert, delete, substitute (each costs 1).
    Uses dynamic programming with an (n+1) x (m+1) table."""
    n = len(s1)
    m = len(s2)
    # dp[i][j] = edit distance between s1[:i] and s2[:j]
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                cost = 0
            else:
                cost = 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,      # deletion
                dp[i][j - 1] + 1,      # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )
    return dp[n][m]


def longest_common_subsequence_length(s1: str, s2: str) -> int:
    """Compute the length of the longest common subsequence (LCS).
    Uses dynamic programming."""
    n = len(s1)
    m = len(s2)
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[n][m]


def longest_common_substring_length(s1: str, s2: str) -> int:
    """Find the length of the longest common substring (contiguous).
    Uses dynamic programming."""
    n = len(s1)
    m = len(s2)
    best = 0
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > best:
                    best = dp[i][j]
            else:
                dp[i][j] = 0
    return best


if __name__ == "__main__":
    assert hamming_distance("karolin", "kathrin") == 3
    assert hamming_distance("abc", "abc") == 0

    assert levenshtein_distance("kitten", "sitting") == 3
    assert levenshtein_distance("", "abc") == 3
    assert levenshtein_distance("abc", "abc") == 0

    assert longest_common_subsequence_length("ABCBDAB", "BDCAB") == 4
    assert longest_common_subsequence_length("abc", "def") == 0

    assert longest_common_substring_length("abcdef", "zbcdf") == 3
    assert longest_common_substring_length("abc", "xyz") == 0
    print("All edit distance tests passed.")
