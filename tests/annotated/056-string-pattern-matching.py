"""String Algorithms 1: Pattern Matching"""


#@ requires 1 == 1
#@ ensures \result >= -1
#@ ensures 1 == 1
#@ assigns \nothing
def naive_string_search(text: str, pattern: str) -> int:
    """Find the first occurrence of pattern in text.
    Returns the starting index, or -1 if not found.
    Uses the brute-force O(n*m) approach."""
    n = len(text)
    m = len(pattern)
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n + 1
    #@ loop variant n - i
    while i <= n - m:
        is_match = 1
        j = 0
        #@ loop invariant 0 <= j
        #@ loop invariant j <= m
        #@ loop invariant is_match >= 0
        #@ loop invariant is_match <= 1
        #@ loop invariant i <= n - m
        #@ loop variant m - j
        while j < m and is_match == 1:
            if text[i + j] != pattern[j]:
                is_match = 0
            j += 1
        if is_match == 1:
            return i
        i += 1
    return -1


#@ requires 1 == 1
#@ ensures \result >= 0
#@ assigns \nothing
def count_occurrences(text: str, pattern: str) -> int:
    count = 0
    n = len(text)
    m = len(pattern)
    i = 0
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant count >= 0
    #@ loop invariant count <= i
    #@ loop variant n - i
    while i <= n - m:
        is_match = 1
        j = 0
        #@ loop invariant 0 <= j
        #@ loop invariant j <= m
        #@ loop invariant is_match >= 0
        #@ loop invariant is_match <= 1
        #@ loop variant m - j
        while j < m:
            if text[i + j] != pattern[j]:
                is_match = 0
            j += 1
        if is_match != 0:
            count += 1
            i += m
        else:
            i += 1
    return count


#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def kmp_build_failure(pattern: str) -> list:
    m = len(pattern)
    failure = [0] * m
    k = 0
    i = 1
    #@ loop invariant 1 <= i
    #@ loop invariant k >= 0
    #@ loop invariant k < m
    #@ loop invariant \length(failure) == m
    #@ loop invariant \length(failure) > 0 ==> failure[0] == 0
    #@ loop variant m - i
    while i < m:
        #@ loop invariant k >= 0
        #@ loop invariant k < m
        #@ loop invariant i < m
        #@ loop variant k
        while k > 0 and pattern[k] != pattern[i]:
            k = failure[k - 1]
        if pattern[k] == pattern[i]:
            k += 1
        failure[i] = k
        i += 1
    return failure


#@ requires 1 == 1
#@ ensures \result >= -1
#@ ensures 1 == 1
#@ assigns \nothing
def kmp_search(text: str, pattern: str) -> int:
    """Knuth-Morris-Pratt string search.
    Returns the index of the first occurrence, or -1."""
    n = len(text)
    m = len(pattern)
    if m == 0:
        return 0
    failure = kmp_build_failure(pattern)
    k = 0
    i = 0
    found = -1
    #@ loop invariant 0 <= i
    #@ loop invariant i <= n
    #@ loop invariant k >= 0
    #@ loop invariant k < m
    #@ loop invariant found >= -1
    #@ loop invariant found <= n
    #@ loop variant n - i
    while i < n:
        #@ loop invariant k >= 0
        #@ loop invariant k < m
        #@ loop invariant i < n
        #@ loop variant k
        while k > 0 and pattern[k] != text[i]:
            k = failure[k - 1]
        if pattern[k] == text[i]:
            k += 1
        if k == m:
            found = i - m + 1
            i = n
        else:
            i += 1
    return found


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
