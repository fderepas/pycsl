"""Phase 1B — Time arithmetic verification (rclpy cyber-threat #1).

Verifies that 64-bit nanosecond arithmetic in rclpy Time:
  * respects non-negativity invariant (Time >= 0)
  * stays within uint63 bounds (0 to 2^63-1) after operations
  * raises ValueError on negative, OverflowError on overflow
  * decomposes correctly into (seconds, nanoseconds) with both >= 0

Maps to ros-report.md Threat #1 — memory-corruption at C-Python boundary.
Source: rclpy/rclpy/rclpy/time.py

Note: contracts use 9223372036854775808 (2^63) as boundary constant because
it survives float round-trip in the transpiler.
"""
_ = 0  # anchor


# ── 1. time_create — models Time.__init__ with non-negativity guard ──────
#@ requires 1 == 1
#@ ensures \result == nanoseconds
#@ raises ValueError when nanoseconds < 0
#@ raises OverflowError when nanoseconds >= 9223372036854775808
#@ assigns \nothing
def time_create(nanoseconds: int) -> int:
    ns = nanoseconds
    if ns < 0:
        raise ValueError
    if ns >= 9223372036854775808:
        raise OverflowError
    return ns


# ── 2. time_add_duration — models Time.__add__(Duration) ─────────────────
#@ requires 0 <= t_ns and t_ns < 9223372036854775808
#@ requires -9223372036854775808 <= d_ns and d_ns < 9223372036854775808
#@ ensures \result == t_ns + d_ns
#@ raises ValueError when t_ns + d_ns < 0
#@ raises OverflowError when t_ns + d_ns >= 9223372036854775808
#@ assigns \nothing
def time_add_duration(t_ns: int, d_ns: int) -> int:
    total = t_ns + d_ns
    if total < 0:
        raise ValueError
    if total >= 9223372036854775808:
        raise OverflowError
    return total


# ── 3. time_sub_time — models Time.__sub__(Time) → Duration ─────────────
#@ requires 0 <= a_ns and a_ns < 9223372036854775808
#@ requires 0 <= b_ns and b_ns < 9223372036854775808
#@ ensures \result == a_ns - b_ns
#@ assigns \nothing
def time_sub_time(a_ns: int, b_ns: int) -> int:
    return a_ns - b_ns


# ── 4. time_eq — models Time.__eq__ ──────────────────────────────────────
#@ requires 0 <= a_ns and a_ns < 9223372036854775808
#@ requires 0 <= b_ns and b_ns < 9223372036854775808
#@ ensures (a_ns == b_ns) ==> (\result == 1)
#@ ensures (a_ns != b_ns) ==> (\result == 0)
#@ assigns \nothing
def time_eq(a_ns: int, b_ns: int) -> int:
    if a_ns == b_ns:
        return 1
    return 0


# ── 5. time_lt — models Time.__lt__ ──────────────────────────────────────
#@ requires 0 <= a_ns and a_ns < 9223372036854775808
#@ requires 0 <= b_ns and b_ns < 9223372036854775808
#@ ensures (a_ns < b_ns) ==> (\result == 1)
#@ ensures (a_ns >= b_ns) ==> (\result == 0)
#@ assigns \nothing
def time_lt(a_ns: int, b_ns: int) -> int:
    if a_ns < b_ns:
        return 1
    return 0


# ── 6. time_seconds_nanoseconds — models Time.seconds_nanoseconds() ─────
#@ requires 0 <= total_ns and total_ns < 9223372036854775808
#@ ensures \result[0] >= 0
#@ ensures \result[1] >= 0
#@ ensures \result[0] * 1000000000 + \result[1] == total_ns
#@ assigns \nothing
def time_seconds_nanoseconds(total_ns: int) -> tuple:
    sec = total_ns // 1000000000
    nsec = total_ns - sec * 1000000000
    return (sec, nsec)


if __name__ == "__main__":
    assert time_create(0) == 0
    assert time_create(9223372036854775807) == 9223372036854775807
    try:
        time_create(-1)
        assert 0 == 1
    except ValueError:
        pass
    try:
        time_create(9223372036854775808)
        assert 0 == 1
    except OverflowError:
        pass

    assert time_add_duration(100, 200) == 300
    assert time_add_duration(100, -50) == 50
    try:
        time_add_duration(100, -200)
        assert 0 == 1
    except ValueError:
        pass

    assert time_sub_time(300, 100) == 200
    assert time_sub_time(100, 300) == -200

    assert time_eq(42, 42) == 1
    assert time_eq(42, 43) == 0
    assert time_lt(42, 43) == 1
    assert time_lt(43, 42) == 0

    s, ns = time_seconds_nanoseconds(2500000000)
    assert s == 2 and ns == 500000000
    assert s * 1000000000 + ns == 2500000000

    print("PASS time_verified")
