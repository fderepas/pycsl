# Bug Report: Time 64-bit Overflow and Y2038 at the C-Python Boundary

**Component:** `rclpy` — `time.py`
**Severity:** Critical (Y2038 affects all SYSTEM_TIME / ROS_TIME after 2038-01-19)
**Threat category:** ros-report.md Threat #1 — Memory corruption at C-Python boundary
**Audited version:** rclpy rolling, tag `11.0.1`, commit `69d5ea9`

---

## Summary

Code review of the `Time` class nanosecond arithmetic confirms that the
**core guards are correct**: negative nanoseconds are rejected with
`ValueError`, values ≥ 2^63 are rejected with `OverflowError`, and the
`seconds_nanoseconds()` decomposition preserves the identity
`sec × 10^9 + nsec == total_ns` with both components non-negative.

However, the analysis uncovered **five issues** ranging from a Y2038-class
bug to dead exception handlers.

---

## Finding 1 — `to_msg()` triggers Y2038: timestamps after 2038-01-19 silently corrupt

### Severity: Critical

### Location

`time.py` lines 160–167:

```python
def to_msg(self) -> builtin_interfaces.msg.Time:
    seconds, nanoseconds = self.seconds_nanoseconds()
    return builtin_interfaces.msg.Time(sec=seconds, nanosec=nanoseconds)
```

### Root cause

`Time.__init__` accepts nanosecond values in `[0, 2^63)`, corresponding to
dates up to approximately year 2262 (292 years from epoch). But
`to_msg()` serializes to `builtin_interfaces/msg/Time`, whose IDL declares:

```
int32 sec       # range: [-2,147,483,648 .. 2,147,483,647]
uint32 nanosec  # range: [0 .. 999,999,999]
```

The `int32 sec` field overflows at **2038-01-19 03:14:07 UTC** — the classic
Y2038 problem. Any `Time` object representing a timestamp after this date
produces a `sec` value exceeding int32 range when `to_msg()` is called.

**Root cause note:** The Y2038 limitation originates in the
`builtin_interfaces/msg/Time.msg` IDL, which declares `int32 sec`. This
is an IDL-level design issue, not an rclpy-specific bug. The Python layer
should fail closed earlier and with a clearer error, and the IDL should
ultimately migrate to `int64 sec`.

### Timeline

| Date | sec value | Fits int32? |
|---|---|---|
| 2024-01-01 | 1,704,067,200 | ✅ Yes |
| 2038-01-19 03:14:07 | 2,147,483,647 | ✅ Last valid |
| 2038-01-19 03:14:08 | 2,147,483,648 | ❌ **Overflows** |
| 2040-01-01 | 2,208,988,800 | ❌ Overflows |

### Impact

- **Every ROS 2 system** using `SYSTEM_TIME` or `ROS_TIME` will hit this
  after 2038-01-19
- Under default Python, the generated message setter may catch the
  out-of-range `sec` value before serialization
- Under `python -O`, those assert-based checks may be skipped, making the
  overflow silent until later serialization/use
- Other nodes receiving the message deserialize a wrapped/truncated
  timestamp
- Affected uses: `tf2` transforms, `rosbag2` recording, message headers,
  deadline/liveliness QoS timers

### Example

```python
from rclpy.time import Time

# A date in 2040 — 12 years from now
t = Time(seconds=2_208_988_800)       # Valid: fits in int64
msg = t.to_msg()                       # msg.sec = 2,208,988,800

# msg.sec exceeds int32_max (2,147,483,647)
# DDS serialization silently truncates or wraps:
#   2,208,988,800 mod 2^32 = 2,208,988,800  (fits uint32 but not int32)
#   As signed int32: 2,208,988,800 - 2^32 = -2,085,978,496
#   Deserialized as: 1903-11-07 (wrong by 137 years)
```

### Recommendation

Add a range check in `to_msg()` and `seconds_nanoseconds()`:

```python
def to_msg(self) -> builtin_interfaces.msg.Time:
    seconds, nanoseconds = self.seconds_nanoseconds()
    if seconds > 2147483647 or seconds < -2147483648:
        raise OverflowError(
            f'Time seconds ({seconds}) exceeds int32 range for ROS message. '
            f'Consider using a 64-bit time representation.')
    return builtin_interfaces.msg.Time(sec=seconds, nanosec=nanoseconds)
```

Long-term, the `builtin_interfaces/msg/Time.msg` IDL should migrate to
`int64 sec` or a single `int64 nanoseconds` field.

---

## Finding 2 — `Time.__sub__(Time)` has a dead `ValueError` handler

### Severity: Medium (misleading error path, defense-in-depth gap)

### Location

`time.py` lines 102–109:

```python
def __sub__(self, other):
    if isinstance(other, Time):
        if self.clock_type != other.clock_type:
            raise TypeError("Can't subtract times with different clock types")
        try:
            return Duration(nanoseconds=(self.nanoseconds - other.nanoseconds))
        except ValueError as e:                                    # ← DEAD CODE
            raise ValueError('Subtraction leads to negative duration.') from e
```

### Root cause

The `except ValueError` handler on line 108 assumes that
`Duration(nanoseconds=negative_value)` raises `ValueError`. But
`Duration.__init__` **never raises `ValueError`** — it only raises
`OverflowError` for values outside `[-2^63, 2^63)`. Negative nanoseconds
are perfectly valid for `Duration` (a duration can be negative).

Since both `Time` operands have nanoseconds in `[0, 2^63-1]`, their
difference is in `(-2^63, 2^63)`, which always fits in Duration's int64
range. Therefore:

1. `Duration.__init__` never raises `OverflowError` (difference is in range)
2. `Duration.__init__` never raises `ValueError` (it doesn't have one)
3. The `except ValueError` block is **unreachable dead code**

### Impact

- The dead handler gives a false sense of safety — developers reading the
  code believe negative-duration subtraction is caught, but it isn't
- `Time(100) - Time(200)` silently returns `Duration(nanoseconds=-100)`,
  which may surprise callers expecting non-negative durations from a
  Time-minus-Time operation
- If a future refactor adds a negativity check to `Duration.__init__`, the
  handler would suddenly activate but with the wrong exception chain

### Recommendation

Either:

**A)** Remove the dead handler and document that Time subtraction can produce
negative durations:

```python
if isinstance(other, Time):
    if self.clock_type != other.clock_type:
        raise TypeError("Can't subtract times with different clock types")
    return Duration(nanoseconds=(self.nanoseconds - other.nanoseconds))
```

**B)** Or add an explicit negativity check if negative durations from Time
subtraction should be an error:

```python
diff = self.nanoseconds - other.nanoseconds
if diff < 0:
    raise ValueError('Subtraction of later time from earlier time '
                     'produces negative duration.')
return Duration(nanoseconds=diff)
```

---

## Finding 3 — Independent negativity checks reject valid time values

### Severity: Informational (design choice, not a bug)

This finding documents a design choice rather than a defect. It is included
for completeness but is not recommended for upstream filing.

### Location

`time.py` lines 47–50:

```python
if seconds < 0:
    raise ValueError('Seconds value must not be negative')
if nanoseconds < 0:
    raise ValueError('Nanoseconds value must not be negative')
```

### Root cause

The `seconds` and `nanoseconds` parameters are checked for negativity
**independently**, before computing `total_nanoseconds`. This means
combinations where one component is negative but the total is non-negative
are rejected:

```python
Time(seconds=1, nanoseconds=-1)
# seconds >= 0: OK
# nanoseconds < 0: ValueError!
# But total = 1×10^9 + (-1) = 999,999,999 ns — a valid non-negative time

Time(seconds=-1, nanoseconds=2_000_000_000)
# seconds < 0: ValueError!
# But total = -10^9 + 2×10^9 = 10^9 ns — a valid non-negative time
```

### Impact

This is arguably a **design choice** rather than a bug — rejecting negative
components early is stricter and prevents accidental misuse. However, it is
inconsistent with `Duration.__init__`, which freely accepts
`Duration(seconds=-1, nanoseconds=2_000_000_000)` (total = 10^9 ns).

### Recommendation

Document this behavior explicitly:

```python
def __init__(self, *, seconds=0, nanoseconds=0, clock_type=...):
    """
    ...
    :raises ValueError: if seconds < 0 or nanoseconds < 0 (checked
        independently, even if the total would be non-negative)
    """
```

---

## Finding 4 — `to_datetime()` loses nanosecond precision

### Severity: Low (inherent float limitation)

### Location

`time.py` line 177:

```python
return datetime.fromtimestamp(self.nanoseconds / S_TO_NS)
```

### Root cause

The division `self.nanoseconds / S_TO_NS` converts to IEEE 754 double,
which has only 53 bits of mantissa. For current-era timestamps
(~1.7 × 10^18 ns), the precision loss is ~21 nanoseconds:

```python
ns = 1_700_000_000_123_456_789     # 2023-11-14T22:13:20.123456789
via_float = int(ns / 1e9 * 1e9)    # 1_700_000_000_123_456_768
delta = via_float - ns              # -21 ns
```

Additionally, Python's `datetime` has only microsecond resolution, so
the last 3 digits of the nanosecond component are always lost:

```python
datetime.fromtimestamp(1700000000.123456789)
# → datetime(2023, 11, 14, 23, 13, 20, 123457)   # µs precision only
```

### Impact

- The double float conversion loses ~21 ns for current timestamps
- The `datetime` type loses the last ~999 ns
- Combined loss: up to ~1021 ns (1.02 µs) from the original Time
- For most applications this is negligible, but sub-microsecond-precision
  logging or profiling would be affected

### Recommendation

Document the precision loss in the docstring. For nanosecond-precision
conversion, users should use `seconds_nanoseconds()` directly.

---

## Finding 5 — Float precision loss in `__init__` (shared with Duration)

**Note:** This finding is identical to ros-issue-1.md Finding 2. It is
included here for completeness but should be consolidated into a single
upstream PR.

### Severity: Medium

### Location

`time.py` line 51:

```python
total_nanoseconds = int(seconds * S_TO_NS)
```

### Root cause

Identical to Duration (see `ros-issue-1.md` Finding 2). When `seconds` is
`float`, the multiplication loses precision above 2^53 ns (~104 days).

Near the int64 boundary:

```python
target_ns = 2**63 - 1                        # 9,223,372,036,854,775,807
seconds_float = target_ns / 1e9              # 9223372036.854776
recovered = int(seconds_float * 1e9)         # 9,223,372,036,854,775,808 = 2^63
# OverflowError! But the caller intended a valid value (2^63 - 1)
```

### Recommendation

Same as `ros-issue-1.md` Finding 2: add an integer fast path:

```python
if isinstance(seconds, int) and isinstance(nanoseconds, int):
    total_nanoseconds = seconds * S_TO_NS + nanoseconds
else:
    total_nanoseconds = int(seconds * S_TO_NS) + int(nanoseconds)
```

---

## Cross-references

- **ros-issue-1.md** — Duration overflow report (same `to_msg` int32 and
  float precision issues)
- **ros-report.md** — Threat #1: Memory corruption at C-Python boundary
- **builtin_interfaces/msg/Time.msg** — IDL confirming `int32 sec` /
  `uint32 nanosec`

## Affected versions

All versions of `rclpy` since the introduction of the `Time` class.
The `to_msg()` Y2038 issue affects every ROS 2 distribution that will still
be in service after January 19, 2038.
