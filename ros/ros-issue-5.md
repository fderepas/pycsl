# Bug Report: QoSProfile Validation Gaps in `rclpy`

**Component:** `rclpy` — `qos.py`
**Severity:** High
**Threat category:** ros-report.md Threat #3 — semantic input handling
**Audited version:** rclpy rolling, tag `11.0.1`, commit `69d5ea9`

---

## Summary

Review of `rclpy.qos.QoSProfile` on rolling shows that the basic enum
conversion paths work, but the validation story is inconsistent. The Python
layer permits invalid or misleading states that are later handed to the C
extension, and one exception type is constructed incorrectly.

This report records five findings:

1. `InvalidQoSProfileException` discards its message
2. Negative depth is accepted
3. The depth setter warns but does not reject or repair `KEEP_LAST` + `0`
4. Setter type checks rely on `assert`
5. Post-construction mutation bypasses constructor-level validation

---

## Finding 1 — `InvalidQoSProfileException` discards its message

### Severity: Medium

### Location

`qos.py` lines 56–60:

```python
class InvalidQoSProfileException(Exception):
    """Raised when constructing a QoSProfile with invalid arguments."""

    def __init__(self, message: str) -> None:
        Exception(self, f'Invalid QoSProfile: {message}')
```

### Description

The constructor does **not** initialize the exception instance being created.
`Exception(self, ...)` constructs a separate throwaway `Exception` object and
immediately discards it. That is different from either of the correct forms:

```python
super().__init__(f'Invalid QoSProfile: {message}')
```

or

```python
Exception.__init__(self, f'Invalid QoSProfile: {message}')
```

As written on rolling, `InvalidQoSProfileException('x')` creates an instance
whose `args` remain empty. When `QoSProfile.__init__` raises this type, the
caller receives the right exception class but without the explanatory message.
That weakens diagnostics and can break code that logs or branches on
`exc.args[0]` / `str(exc)`.

**Version note:** This finding was verified against `qos.py` line 60 in
rclpy rolling (tag `11.0.1`, commit `69d5ea9`). The `humble` branch may
have different code — specifically `Exception.__init__(self, ...)` which
would be a correct (though unconventional) parent-init call. On rolling,
the code constructs and discards a new `Exception` object, leaving the
instance uninitialized.

### Impact

- `InvalidQoSProfileException` is raised without the intended text
- Logs and tests see an empty exception payload
- Operators lose the exact reason a QoS profile was rejected

### Recommendation

Replace the constructor body with a real parent-class initialization call:

```python
def __init__(self, message: str) -> None:
    super().__init__(f'Invalid QoSProfile: {message}')
```

---

## Finding 2 — Negative depth is accepted

### Severity: High

### Location

`qos.py` lines 184–193 and 266–276:

```python
@depth.setter
def depth(self, value: int) -> None:
    assert isinstance(value, int)

    if self.history == QoSHistoryPolicy.KEEP_LAST and value == 0:
        warnings.warn(
            "A zero depth with KEEP_LAST doesn't make sense; no data could be stored. "
            'This will be interpreted as SYSTEM_DEFAULT')

    self._depth = value
```

```python
def get_c_qos_profile(self) -> _rclpy.rmw_qos_profile_t:
    return _rclpy.rmw_qos_profile_t(
        self.history,
        self.depth,
        ...,
    )
```

### Description

The setter checks only that `depth` is an `int`; it never enforces `depth >= 0`.
As a result, `QoSProfile(history=KEEP_LAST, depth=-1)` is accepted at the
Python layer. That negative value is later forwarded into the C-backed
`rmw_qos_profile_t` creation path.

At that boundary the queue depth is no longer a Python semantic value; it is a
field in the middleware QoS structure. A negative Python integer can become a
nonsensical or extremely large depth once it reaches the lower layer, depending
on the exact destination type and conversion path. The likely outcomes are late
failures, resource exhaustion, or transport-layer misbehavior far away from the
original call site.

### Impact

- Invalid queue sizes are accepted by the public Python API
- Failure moves from construction time to a later C-extension / middleware path
- Negative values may be reinterpreted as huge queue depths

### Recommendation

Reject negative depth immediately in the Python setter:

```python
if not isinstance(value, int):
    raise TypeError('depth must be an int')
if value < 0:
    raise ValueError('depth must be >= 0')
```

---

## Finding 3 — The depth setter warns but does not reject or repair `KEEP_LAST` + `0`

### Severity: Medium

### Location

`qos.py` lines 188–193:

```python
if self.history == QoSHistoryPolicy.KEEP_LAST and value == 0:
    warnings.warn(
        "A zero depth with KEEP_LAST doesn't make sense; no data could be stored. "
        'This will be interpreted as SYSTEM_DEFAULT')

self._depth = value
```

### Description

The warning text says the configuration will be "interpreted as
SYSTEM_DEFAULT", but the code does not perform any interpretation or repair.
It simply stores `0` in `_depth`. The resulting object therefore remains in the
very state the warning claims will be normalized away.

This is especially problematic because callers may treat the warning as proof
that the object has been coerced into a safe default. It has not. The profile
still carries `history == KEEP_LAST` and `depth == 0`.

### Impact

- Warning text does not match actual behavior
- Callers may continue with an invalid profile under false assumptions
- The invalid combination can survive until the C/middleware boundary

### Recommendation

Choose one behavior and implement it consistently:

- raise `ValueError` for `KEEP_LAST` with `depth == 0`, or
- actually rewrite the value to the intended system default representation

---

## Finding 4 — Setter type checks rely on `assert`

### Severity: Medium

### Location

Representative examples from `qos.py`:

```python
assert isinstance(value, QoSHistoryPolicy) or isinstance(value, int)
assert isinstance(value, Duration)
assert isinstance(value, bool)
```

### Description

Most `QoSProfile` setters use `assert` as their only type check. Under normal
execution that catches obvious misuse, but under `python -O` those assertions
are stripped. The API then loses its front-line type validation.

After optimization, bad values can flow into enum constructors, be stored in the
object, or be forwarded to `_rclpy.rmw_qos_profile_t` before failing. That
changes failure mode from a clean, deterministic Python-side error into a later
and less predictable exception path.

### Impact

- Validation behavior changes under optimized execution
- Type errors surface later and less clearly
- More malformed state can reach the C extension

### Recommendation

Replace assertion-based checks with explicit runtime validation:

```python
if not isinstance(value, Duration):
    raise TypeError('lifespan must be a Duration')
```

Do this consistently for every setter.

---

## Finding 5 — Post-construction mutation bypasses constructor-level validation

### Severity: High

### Location

`qos.py` constructor validation versus independent property setters.

### Description

`QoSProfile.__init__` performs a cross-field check for one invalid combination:
`KEEP_LAST` requires a depth value. But after construction, the individual
property setters validate fields in isolation. They do not re-check the overall
invariant.

That means callers can construct a profile in a valid order and then mutate it
into an invalid state. For example:

```python
q = QoSProfile(history=QoSHistoryPolicy.KEEP_ALL, depth=0)
q.history = QoSHistoryPolicy.KEEP_LAST
# Now history == KEEP_LAST and depth == 0, but no exception was raised.
```

The same class of problem appears with other multi-field QoS invariants: once
construction is complete, no central validator is invoked to keep the object
coherent.

### Impact

- Invalid QoS profiles can exist after successful construction
- Invariants enforced in `__init__` are not preserved over object lifetime
- Broken state can be serialized to the C/middleware layer later

### Recommendation

Centralize validation in a helper that is called from both `__init__` and the
relevant setters, or make the object immutable after construction.

---

## Cross-references

- `rclpy/rclpy/rclpy/qos.py` — audited Python implementation
- `rclpy/rclpy/src/rclpy/qos.cpp` — C-backed QoS profile construction path

## Affected version

Verified on `rclpy` rolling tag `11.0.1` (`69d5ea9`). Other branches may differ
for specific findings, especially Finding 1's exception-constructor bug.
