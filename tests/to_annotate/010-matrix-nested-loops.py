def matrix_fill(out, n, value):
    """Fill a flat matrix (length n) with a constant value."""
    i = 0
    while i < n:
        out[i] = value
        i += 1
    return 0


def matrix_add(a, b, out, n):
    """Element-wise add two flat matrices of the same length n."""
    i = 0
    while i < n:
        out[i] = a[i] + b[i]
        i += 1
    return 0


def matrix_scale(a, out, n, factor):
    """Multiply every element of flat matrix a by factor, store in out."""
    i = 0
    while i < n:
        out[i] = a[i] * factor
        i += 1
    return 0


def matrix_max(a, n):
    """Return the maximum element of flat matrix a (n >= 1)."""
    best = a[0]
    i = 1
    while i < n:
        if a[i] > best:
            best = a[i]
        i += 1
    return best


def matrix_copy(src, dst, n):
    """Copy flat matrix src into dst (length n)."""
    i = 0
    while i < n:
        dst[i] = src[i]
        i += 1
    return 0


if __name__ == "__main__":
    m = [1, 2, 3, 4, 5, 6]
    out = [0] * 6
    matrix_fill(out, 6, 7)
    print("fill:", out)
    matrix_add(m, m, out, 6)
    print("add:", out)
    matrix_scale(m, out, 6, 3)
    print("scale:", out)
    print("max:", matrix_max(m, 6))
    matrix_copy(m, out, 6)
    print("copy:", out)

