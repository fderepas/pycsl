"""Phase 4 — QoS profile validation (rclpy cyber-threat #3).

Verifies QoSProfile constructor validation logic:
  * KEEP_LAST (history == 1) requires depth >= 1
  * KEEP_ALL (history == 0) accepts any depth
  * invalid combinations raise ValueError
  * depth is always non-negative in the result

Models QoSHistoryPolicy as integer: 0 = KEEP_ALL, 1 = KEEP_LAST.

Maps to ros-report.md Threat #3 — semantic input handling.
Source: rclpy/rclpy/rclpy/qos.py
"""
_ = 0  # anchor


# ── 1. qos_validate — models QoSProfile.__init__ history/depth check ─────
#@ requires history == 0 or history == 1
#@ requires depth >= 0
#@ ensures (history == 1 and depth >= 1) ==> (\result[0] == 1 and \result[1] == depth)
#@ ensures (history == 0) ==> (\result[0] == 0 and \result[1] == depth)
#@ raises ValueError when history == 1 and depth == 0
#@ assigns \nothing
def qos_validate(history: int, depth: int) -> tuple:
    h = history
    d = depth
    if h == 1 and d == 0:
        raise ValueError
    return (h, d)


# ── 2. qos_depth_check — verifies depth is positive when KEEP_LAST ───────
#@ requires depth >= 0
#@ ensures (depth >= 1) ==> (\result == 1)
#@ ensures (depth == 0) ==> (\result == 0)
#@ assigns \nothing
def qos_depth_check(depth: int) -> int:
    if depth >= 1:
        return 1
    return 0


# ── 3. qos_history_valid — verifies history policy is in range ────────────
#@ requires 1 == 1
#@ ensures (policy == 0 or policy == 1) ==> (\result == 1)
#@ ensures (policy != 0 and policy != 1) ==> (\result == 0)
#@ assigns \nothing
def qos_history_valid(policy: int) -> int:
    p = policy
    if p == 0 or p == 1:
        return 1
    return 0


if __name__ == "__main__":
    assert qos_validate(0, 0) == (0, 0)
    assert qos_validate(0, 10) == (0, 10)
    assert qos_validate(1, 5) == (1, 5)
    try:
        qos_validate(1, 0)
        assert 0 == 1
    except ValueError:
        pass

    assert qos_depth_check(5) == 1
    assert qos_depth_check(0) == 0

    assert qos_history_valid(0) == 1
    assert qos_history_valid(1) == 1
    assert qos_history_valid(2) == 0
    assert qos_history_valid(-1) == 0

    print("PASS qos_validated")
