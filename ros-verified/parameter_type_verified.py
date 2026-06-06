"""Phase 5 — Parameter type inference exhaustiveness (rclpy cyber-threat #3).

Verifies that parameter type inference and checking cover all 10 type codes:
  * type_from_tag maps every tag in [0..9] to a valid type code
  * type_check returns 1 iff the tag matches the expected type
  * no tag falls through without being handled (exhaustiveness)

Models Parameter.Type as integer codes 0-9 matching rclpy ParameterType:
  0 = NOT_SET, 1 = BOOL, 2 = INTEGER, 3 = DOUBLE, 4 = STRING,
  5 = BYTE_ARRAY, 6 = BOOL_ARRAY, 7 = INTEGER_ARRAY,
  8 = DOUBLE_ARRAY, 9 = STRING_ARRAY

Maps to ros-report.md Threat #3 — semantic input handling.
Source: rclpy/rclpy/rclpy/parameter.py
"""
_ = 0  # anchor


# ── 1. type_from_tag — models Parameter.Type.from_parameter_value ─────────
#@ requires 0 <= tag and tag <= 9
#@ ensures \result == tag
#@ assigns \nothing
def type_from_tag(tag: int) -> int:
    t = tag
    if t == 0:
        return 0
    if t == 1:
        return 1
    if t == 2:
        return 2
    if t == 3:
        return 3
    if t == 4:
        return 4
    if t == 5:
        return 5
    if t == 6:
        return 6
    if t == 7:
        return 7
    if t == 8:
        return 8
    return 9


# ── 2. type_check — models Parameter.Type.check ──────────────────────────
#@ requires 0 <= expected and expected <= 9
#@ requires 0 <= actual and actual <= 9
#@ ensures (expected == actual) ==> (\result == 1)
#@ ensures (expected != actual) ==> (\result == 0)
#@ assigns \nothing
def type_check(expected: int, actual: int) -> int:
    if expected == actual:
        return 1
    return 0


# ── 3. type_is_array — models array-type detection ───────────────────────
#@ requires 0 <= tag and tag <= 9
#@ ensures (tag >= 5) ==> (\result == 1)
#@ ensures (tag < 5) ==> (\result == 0)
#@ assigns \nothing
def type_is_array(tag: int) -> int:
    if tag >= 5:
        return 1
    return 0


# ── 4. type_valid — validates tag is in valid range ───────────────────────
#@ requires 1 == 1
#@ ensures (tag >= 0 and tag <= 9) ==> (\result == 1)
#@ ensures (tag < 0 or tag > 9) ==> (\result == 0)
#@ assigns \nothing
def type_valid(tag: int) -> int:
    t = tag
    if t >= 0 and t <= 9:
        return 1
    return 0


if __name__ == "__main__":
    for i in range(10):
        assert type_from_tag(i) == i
        assert type_check(i, i) == 1
        for j in range(10):
            if j != i:
                assert type_check(i, j) == 0

    assert type_is_array(0) == 0
    assert type_is_array(4) == 0
    assert type_is_array(5) == 1
    assert type_is_array(9) == 1

    assert type_valid(0) == 1
    assert type_valid(9) == 1
    assert type_valid(-1) == 0
    assert type_valid(10) == 0

    print("PASS parameter_type_verified")
