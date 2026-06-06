"""String Algorithms 5: Palindromes and Transformations"""


def is_palindrome(s: str) -> bool:
    """Check whether a string is a palindrome using two pointers."""
    left = 0
    right = len(s) - 1
    while left < right:
        if s[left] != s[right]:
            return False
        left += 1
        right -= 1
    return True


def longest_palindrome_substring(s: str) -> str:
    """Find the longest palindromic substring using expand-around-center.
    O(n^2) time, O(1) extra space."""
    n = len(s)
    if n == 0:
        return ""
    start = 0
    max_len = 1

    def expand(left: int, right: int) -> tuple:
        while left >= 0 and right < n and s[left] == s[right]:
            left -= 1
            right += 1
        return left + 1, right - left - 1

    for i in range(n):
        # Odd-length palindrome centered at i
        lo, length = expand(i, i)
        if length > max_len:
            start = lo
            max_len = length
        # Even-length palindrome centered between i and i+1
        lo, length = expand(i, i + 1)
        if length > max_len:
            start = lo
            max_len = length

    return s[start:start + max_len]


def min_palindrome_partitions(s: str) -> int:
    """Minimum number of cuts to partition s into palindromic substrings.
    Returns the number of cuts (partitions - 1).
    Uses dynamic programming: O(n^2)."""
    n = len(s)
    if n <= 1:
        return 0

    # is_pal[i][j] = True if s[i..j] is a palindrome
    is_pal = [[False] * n for _ in range(n)]
    for i in range(n):
        is_pal[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if length == 2:
                is_pal[i][j] = (s[i] == s[j])
            else:
                is_pal[i][j] = (s[i] == s[j]) and is_pal[i + 1][j - 1]

    # cuts[i] = min cuts for s[0..i]
    cuts = list(range(n))  # worst case: cut after every character
    for i in range(1, n):
        if is_pal[0][i]:
            cuts[i] = 0
            continue
        for j in range(1, i + 1):
            if is_pal[j][i]:
                cuts[i] = min(cuts[i], cuts[j - 1] + 1)
    return cuts[n - 1]


def run_length_encode(s: str) -> str:
    """Run-length encoding: compress consecutive identical characters.
    Example: 'aaabbc' -> 'a3b2c1'."""
    if not s:
        return ""
    result = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            result.append(s[i - 1] + str(count))
            count = 1
    result.append(s[-1] + str(count))
    return "".join(result)


def reverse_words(s: str) -> str:
    """Reverse the order of words in a string.
    Words are separated by single spaces; leading/trailing spaces removed."""
    words = s.strip().split()
    words.reverse()
    return " ".join(words)


if __name__ == "__main__":
    assert is_palindrome("racecar") is True
    assert is_palindrome("hello") is False
    assert is_palindrome("a") is True
    assert is_palindrome("") is True

    assert longest_palindrome_substring("babad") in ("bab", "aba")
    assert longest_palindrome_substring("cbbd") == "bb"
    assert longest_palindrome_substring("a") == "a"

    assert min_palindrome_partitions("aab") == 1  # "aa" | "b"
    assert min_palindrome_partitions("aba") == 0  # already palindrome
    assert min_palindrome_partitions("abcd") == 3

    assert run_length_encode("aaabbc") == "a3b2c1"
    assert run_length_encode("a") == "a1"
    assert run_length_encode("") == ""

    assert reverse_words("hello world") == "world hello"
    assert reverse_words("  the sky is blue  ") == "blue is sky the"
    print("All palindrome & transformation tests passed.")
