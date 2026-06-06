# Negative test: loop invariant that is not preserved
# Dynamic oracle should catch invariant violation

_ = 0  # anchor for LibCST leading_lines
#@ requires n >= 0
#@ ensures \result >= 0
def broken_loop(n: int) -> int:
    s = 0
    i = 0
    #@ loop invariant i <= n
    #@ loop invariant s == i * i
    #@ loop variant n - i
    while i < n:
        s = s + 2 * i + 1
        i = i + 1
    return s

if __name__ == "__main__":
    # s = i*i is actually correct for sum of odd numbers!
    # Let's check: 0→0, 1→1, 2→4, 3→9 — yes it's correct
    # But a truly broken one:
    pass

# Actually correct — let's make a truly broken invariant
#@ requires n >= 0
#@ ensures \result >= 0
def truly_broken(n: int) -> int:
    s = 0
    i = 0
    #@ loop invariant i <= n
    #@ loop invariant s == i
    #@ loop variant n - i
    while i < n:
        s = s + 2
        i = i + 1
    return s

if __name__ == "__main__":
    print("truly_broken(5) =", truly_broken(5))
