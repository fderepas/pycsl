"""String Algorithms 1: Pattern Matching"""


def naive_string_search(text: str, pattern: str) -> int:
    """Find the first occurrence of pattern in text.
    Returns the starting index, or -1 if not found.
    Uses the brute-force O(n*m) approach."""
    n = len(text)
    m = len(pattern)
    for i in range(n - m + 1):
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            return i
    return -1


def count_occurrences(text: str, pattern: str) -> int:
    """Count non-overlapping occurrences of pattern in text."""
    count = 0
    n = len(text)
    m = len(pattern)
    i = 0
    while i <= n - m:
        match = True
        for j in range(m):
            if text[i + j] != pattern[j]:
                match = False
                break
        if match:
            count += 1
            i += m  # skip past this occurrence
        else:
            i += 1
    return count


def kmp_build_failure(pattern: str) -> list:
    """Build the KMP failure function (partial match table).
    failure[i] = length of the longest proper prefix of pattern[0..i]
    that is also a suffix."""
    m = len(pattern)
    failure = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and pattern[k] != pattern[i]:
            k = failure[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        failure[i] = k
    return failure


def kmp_search(text: str, pattern: str) -> int:
    """Knuth-Morris-Pratt string search.
    Returns the index of the first occurrence, or -1."""
    n = len(text)
    m = len(pattern)
    if m == 0:
        return 0
    failure = kmp_build_failure(pattern)
    k = 0
    for i in range(n):
        while k > 0 and pattern[k] != text[i]:
            k = failure[k - 1]
        if pattern[k] == text[i]:
            k += 1
        if k == m:
            return i - m + 1
    return -1


if __name__ == "__main__":
    assert naive_string_search("hello world", "world") == 6
    assert naive_string_search("abcabc", "cab") == 2
    assert naive_string_search("aaa", "b") == -1

    assert count_occurrences("abababab", "ab") == 4
    assert count_occurrences("aaaa", "aa") == 2

    assert kmp_build_failure("abcabd") == [0, 0, 0, 1, 2, 0]
    assert kmp_search("abxabcabcaby", "abcaby") == 6
    assert kmp_search("aaaa", "b") == -1
    print("All pattern matching tests passed.")
