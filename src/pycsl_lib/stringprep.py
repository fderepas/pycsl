"""PyCSL mock for Python's stringprep module — String preparation, as per RFC 3453."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def in_table_a1(code: int) -> int:
    """Mock: Determine whether *code* is in tableA.1 (Unassigned code points in Unicode 3.2)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_b1(code: int) -> int:
    """Mock: Determine whether *code* is in tableB.1 (Commonly mapped to nothing)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def map_table_b2(code: int) -> int:
    """Mock: Return the mapped value for *code* according to tableB.2 (Mapping for case-folding used with NFKC)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def map_table_b3(code: int) -> int:
    """Mock: Return the mapped value for *code* according to tableB.3 (Mapping for case-folding used with no normalization)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c11(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.1.1  (ASCII space characters)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c12(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.1.2  (Non-ASCII space characters)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c11_c12(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.1  (Space characters, union of C.1.1 and C.1.2)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c21(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.2.1  (ASCII control characters)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c22(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.2.2  (Non-ASCII control characters)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c21_c22(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.2  (Control characters, union of C.2.1 and C.2.2)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c3(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.3  (Private use)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c4(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.4  (Non-character code points)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c5(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.5  (Surrogate codes)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c6(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.6  (Inappropriate for plain text)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c7(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.7  (Inappropriate for canonical representation)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c8(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.8  (Change display properties or are deprecated)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_c9(code: int) -> int:
    """Mock: Determine whether *code* is in tableC.9  (Tagging characters)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_d1(code: int) -> int:
    """Mock: Determine whether *code* is in tableD.1  (Characters with bidirectional property 'R' or 'AL')."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def in_table_d2(code: int) -> int:
    """Mock: Determine whether *code* is in tableD.2  (Characters with bidirectional property 'L')."""
    return 0
