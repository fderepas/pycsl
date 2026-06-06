"""Phase 1A — Duration arithmetic verification (rclpy cyber-threat #1).

Verifies that 64-bit nanosecond arithmetic in rclpy Duration:
  * stays within int64 bounds after add / subtract
  * raises OverflowError on out-of-range values (no silent wraparound)
  * decomposes correctly into (seconds, nanoseconds) for ROS messages

Maps to ros-report.md Threat #1 — memory-corruption at C-Python boundary.
Source: rclpy/rclpy/rclpy/duration.py

Note: contracts use 9223372036854775808 (2^63) as boundary constant because
it survives float round-trip in the transpiler; 9223372036854775807 (2^63-1)
does not.
"""
_ = 0  # anchor

# Boundary constants (2^63 = 9223372036854775808, used with >= / <)
# Valid int64 range: [-9223372036854775808, 9223372036854775808)


# ── 1. duration_create — models Duration.__init__ overflow guard ─────────
#@ requires 1 == 1
#@ ensures \result == nanoseconds
#@ raises OverflowError when nanoseconds >= 9223372036854775808 or nanoseconds < -9223372036854775808
#@ assigns \nothing
def duration_create(nanoseconds: int) -> int:
    ns = nanoseconds
    if ns >= 9223372036854775808 or ns < -9223372036854775808:
        raise OverflowError
    return ns


# ── 2. duration_add — models Duration.__add__ ────────────────────────────
#@ requires -9223372036854775808 <= a_ns and a_ns < 9223372036854775808
#@ requires -9223372036854775808 <= b_ns and b_ns < 9223372036854775808
#@ ensures \result == a_ns + b_ns
#@ raises OverflowError when a_ns + b_ns >= 9223372036854775808 or a_ns + b_ns < -9223372036854775808
#@ assigns \nothing
def duration_add(a_ns: int, b_ns: int) -> int:
    total = a_ns + b_ns
    if total >= 9223372036854775808 or total < -9223372036854775808:
        raise OverflowError
    return total


# ── 3. duration_sub — models Duration.__sub__ ────────────────────────────
#@ requires -9223372036854775808 <= a_ns and a_ns < 9223372036854775808
#@ requires -9223372036854775808 <= b_ns and b_ns < 9223372036854775808
#@ ensures \result == a_ns - b_ns
#@ raises OverflowError when a_ns - b_ns >= 9223372036854775808 or a_ns - b_ns < -9223372036854775808
#@ assigns \nothing
def duration_sub(a_ns: int, b_ns: int) -> int:
    diff = a_ns - b_ns
    if diff >= 9223372036854775808 or diff < -9223372036854775808:
        raise OverflowError
    return diff


# ── 4. duration_eq — models Duration.__eq__ ──────────────────────────────
#@ requires -9223372036854775808 <= a_ns and a_ns < 9223372036854775808
#@ requires -9223372036854775808 <= b_ns and b_ns < 9223372036854775808
#@ ensures (a_ns == b_ns) ==> (\result == 1)
#@ ensures (a_ns != b_ns) ==> (\result == 0)
#@ assigns \nothing
def duration_eq(a_ns: int, b_ns: int) -> int:
    if a_ns == b_ns:
        return 1
    return 0


# ── 5. duration_lt — models Duration.__lt__ ──────────────────────────────
#@ requires -9223372036854775808 <= a_ns and a_ns < 9223372036854775808
#@ requires -9223372036854775808 <= b_ns and b_ns < 9223372036854775808
#@ ensures (a_ns < b_ns) ==> (\result == 1)
#@ ensures (a_ns >= b_ns) ==> (\result == 0)
#@ assigns \nothing
def duration_lt(a_ns: int, b_ns: int) -> int:
    if a_ns < b_ns:
        return 1
    return 0


# ── 6. duration_to_msg — models Duration.to_msg() decomposition ──────────
#@ requires -9223372036854775808 <= total_ns and total_ns < 9223372036854775808
#@ ensures \result[0] * 1000000000 + \result[1] == total_ns
#@ assigns \nothing
def duration_to_msg(total_ns: int) -> tuple:
    sec = total_ns // 1000000000
    nsec = total_ns - sec * 1000000000
    return (sec, nsec)


if __name__ == "__main__":
    assert duration_create(0) == 0
    assert duration_create(9223372036854775807) == 9223372036854775807
    assert duration_create(-9223372036854775808) == -9223372036854775808
    try:
        duration_create(9223372036854775808)
        assert 0 == 1
    except OverflowError:
        pass

    assert duration_add(100, 200) == 300
    assert duration_add(-100, 50) == -50
    assert duration_sub(300, 100) == 200
    assert duration_sub(-100, 200) == -300

    assert duration_eq(42, 42) == 1
    assert duration_eq(42, 43) == 0
    assert duration_lt(42, 43) == 1
    assert duration_lt(43, 42) == 0

    s, ns = duration_to_msg(2500000000)
    assert s == 2 and ns == 500000000
    assert s * 1000000000 + ns == 2500000000

    s, ns = duration_to_msg(-500000000)
    assert s * 1000000000 + ns == -500000000

    print("PASS duration_verified")
