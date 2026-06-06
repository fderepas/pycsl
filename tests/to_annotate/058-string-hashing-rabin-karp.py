"""String Algorithms 3: Hashing and Rabin-Karp"""


def polynomial_hash(s: str, base: int = 31, mod: int = 10**9 + 9) -> int:
    """Compute a polynomial rolling hash of a string.
    hash = s[0]*base^(n-1) + s[1]*base^(n-2) + ... + s[n-1]*base^0  (mod mod)."""
    h = 0
    power = 1
    for i in range(len(s) - 1, -1, -1):
        h = (h + ord(s[i]) * power) % mod
        power = (power * base) % mod
    return h


def rabin_karp_search(text: str, pattern: str,
                      base: int = 256, mod: int = 101) -> int:
    """Rabin-Karp string search using rolling hash.
    Returns the index of the first occurrence, or -1.
    Average case O(n+m), worst case O(n*m) with hash collisions."""
    n = len(text)
    m = len(pattern)
    if m > n:
        return -1
    if m == 0:
        return 0

    # Precompute base^(m-1) mod q
    h = 1
    for _ in range(m - 1):
        h = (h * base) % mod

    # Compute initial hashes
    p_hash = 0
    t_hash = 0
    for i in range(m):
        p_hash = (base * p_hash + ord(pattern[i])) % mod
        t_hash = (base * t_hash + ord(text[i])) % mod

    for i in range(n - m + 1):
        if p_hash == t_hash:
            # Verify character by character (avoid false positives)
            if text[i:i + m] == pattern:
                return i
        if i < n - m:
            # Roll the hash: remove leading char, add trailing char
            t_hash = (base * (t_hash - ord(text[i]) * h) + ord(text[i + m])) % mod
            if t_hash < 0:
                t_hash += mod
    return -1


def all_rabin_karp(text: str, pattern: str,
                   base: int = 256, mod: int = 101) -> list:
    """Find all occurrences of pattern in text using Rabin-Karp.
    Returns a list of starting indices."""
    n = len(text)
    m = len(pattern)
    results = []
    if m > n or m == 0:
        return results

    h = 1
    for _ in range(m - 1):
        h = (h * base) % mod

    p_hash = 0
    t_hash = 0
    for i in range(m):
        p_hash = (base * p_hash + ord(pattern[i])) % mod
        t_hash = (base * t_hash + ord(text[i])) % mod

    for i in range(n - m + 1):
        if p_hash == t_hash:
            if text[i:i + m] == pattern:
                results.append(i)
        if i < n - m:
            t_hash = (base * (t_hash - ord(text[i]) * h) + ord(text[i + m])) % mod
            if t_hash < 0:
                t_hash += mod
    return results


if __name__ == "__main__":
    assert polynomial_hash("abc") == polynomial_hash("abc")
    assert polynomial_hash("abc") != polynomial_hash("abd")

    assert rabin_karp_search("hello world", "world") == 6
    assert rabin_karp_search("abcabc", "cab") == 2
    assert rabin_karp_search("aaa", "b") == -1

    assert all_rabin_karp("abababab", "ab") == [0, 2, 4, 6]
    assert all_rabin_karp("aaaa", "aa") == [0, 1, 2]
    print("All hashing tests passed.")
