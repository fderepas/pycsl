# Bug Report: Parameter Type Inference Gaps in `rclpy`

**Component:** `rclpy` — `parameter.py`
**Severity:** High (parameter coercion across `/set_parameters` and YAML loading)
**Threat category:** ros-report.md Threat #3 — semantic input handling
**Audited version:** rclpy rolling, tag `11.0.1`, commit `69d5ea9`

---

## Summary

Code review of `rclpy/rclpy/rclpy/parameter.py` confirms that the parameter
API covers the expected ROS 2 parameter kinds, but the current inference and
validation logic still has **five important gaps**:

1. `bool` is silently accepted as `INTEGER`
2. empty lists are classified inconsistently across code paths
3. `NaN` / `Inf` are accepted as `DOUBLE`
4. mixed lists and non-scalar YAML values silently fall back to `STRING`
5. arbitrary-precision Python integers are accepted without int64 bounds

These are not wire-format type-confusion bugs at the DDS layer. They are
**semantic validation bugs** in the Python layer that can let invalid or
surprising parameter values reach node logic, configuration state, or the
C-backed message boundary.

---

## Finding 1 — `bool` / `int` confusion lets `INTEGER.check(True)` succeed

### Severity: High

### Location

`parameter.py` lines 104–109:

```python
if Parameter.Type.BOOL == self:
    return isinstance(parameter_value, bool)
if Parameter.Type.INTEGER == self:
    return isinstance(parameter_value, int)
if Parameter.Type.DOUBLE == self:
    return isinstance(parameter_value, float)
```

### Root cause

In CPython, `bool` is a subclass of `int`, so:

```python
isinstance(True, int) is True
```

That means `Parameter.Type.INTEGER.check(True)` returns `True`, even though
`True` is semantically a boolean parameter. The constructor relies on
`type_.check(value)` as its final guard:

```python
if not type_.check(value):
    raise ValueError("Type '{}' and value '{}' do not agree".format(type_, value))
```

So a caller can construct:

```python
Parameter('flag_like_integer', Parameter.Type.INTEGER, True)
```

and the instance is accepted as an integer parameter.

This is inconsistent with `Parameter.Type.from_parameter_value`, which checks
`bool` before `int` and therefore infers the correct type when the API is used
in inference mode.

### Impact

- A caller using explicit `type_=INTEGER` can accidentally or intentionally
  smuggle booleans through the integer path
- Downstream code that assumes integer-domain semantics may receive values
  originating from boolean configuration
- The API behaves inconsistently depending on whether the caller uses type
  inference or explicit type selection

### Recommendation

Reject `bool` explicitly in the integer path:

```python
if Parameter.Type.INTEGER == self:
    return isinstance(parameter_value, int) and not isinstance(parameter_value, bool)
```

Apply the same exclusion to integer-array validation if mixed `bool` / `int`
containers should not be accepted there either.

---

## Finding 2 — Empty lists are typed inconsistently because `all([])` is true

### Severity: Medium

### Location

`parameter.py` lines 82–92:

```python
elif isinstance(parameter_value, (list, tuple, array.array)):
    if all(isinstance(v, bytes) for v in parameter_value):
        return Parameter.Type.BYTE_ARRAY
    elif all(isinstance(v, bool) for v in parameter_value):
        return Parameter.Type.BOOL_ARRAY
    elif all(isinstance(v, int) for v in parameter_value):
        return Parameter.Type.INTEGER_ARRAY
```

`parameter.py` lines 289–304:

```python
elif isinstance(yaml_value, list):
    if all((isinstance(v, bool) for v in yaml_value)):
        value.type = ParameterType.PARAMETER_BOOL_ARRAY
    elif all((isinstance(v, int) for v in yaml_value)):
        value.type = ParameterType.PARAMETER_INTEGER_ARRAY
    elif all((isinstance(v, float) for v in yaml_value)):
        value.type = ParameterType.PARAMETER_DOUBLE_ARRAY
```

### Root cause

`all()` on an empty iterable returns `True`. In `from_parameter_value`, the
first array branch checks `bytes`, so:

```python
Parameter.Type.from_parameter_value([]) == Parameter.Type.BYTE_ARRAY
```

But in `get_parameter_value`, the first list branch checks `bool`, so the same
semantic input encoded as YAML becomes:

```python
get_parameter_value('[]').type == PARAMETER_BOOL_ARRAY
```

The same empty list therefore maps to different parameter types depending on
which API path is used.

### Impact

- Empty-array parameters are non-deterministic across construction paths
- Nodes that declare or compare expected parameter types can observe different
  types for the same logical input
- This can break configuration round-trips or validation code that expects
  consistent typing between direct Python values and YAML-loaded values

### Recommendation

Handle the empty-list case explicitly before any `all(...)` checks:

```python
if len(parameter_value) == 0:
    raise TypeError('Cannot infer a unique ROS parameter array type from []')
```

Alternatively, define one canonical empty-array type and use it consistently in
both `from_parameter_value` and `get_parameter_value`.

---

## Finding 3 — `NaN` / `Inf` are accepted as `DOUBLE` without finiteness checks

### Severity: High

### Location

`parameter.py` lines 108–109:

```python
if Parameter.Type.DOUBLE == self:
    return isinstance(parameter_value, float)
```

`parameter.py` lines 275–288:

```python
try:
    yaml_value = yaml.safe_load(string_value)
except yaml.parser.ParserError:
    yaml_value = string_value

...
elif isinstance(yaml_value, float):
    value.type = ParameterType.PARAMETER_DOUBLE
    value.double_value = yaml_value
```

### Root cause

YAML floating-point literals such as `.nan`, `.inf`, and `-.inf` are parsed by
`yaml.safe_load()` into Python floats:

```python
yaml.safe_load('.nan')   -> float('nan')
yaml.safe_load('.inf')   -> float('inf')
```

The parameter layer checks only `isinstance(v, float)`, not whether the float
is finite. As a result, special IEEE-754 values are treated as ordinary ROS 2
DOUBLE parameters.

### Example

```python
from rclpy.parameter import Parameter, get_parameter_value

p = Parameter('gain', Parameter.Type.DOUBLE, float('nan'))
msg = p.get_parameter_value()

q = get_parameter_value('.inf')
# q.type == PARAMETER_DOUBLE
# q.double_value == inf
```

### Impact

- Parameter updates can inject `NaN` or `Inf` into node configuration
- Control code that multiplies, accumulates, or compares parameter values may
  become poisoned by IEEE-754 propagation rules
- A bad parameter can silently produce unstable PID gains, undefined thresholds,
  or impossible limits without tripping a type check

**Caveat:** Some ROS 2 components (notably `tf2`) use `NaN` as a sentinel
value in poses and twists to indicate "no value yet." Rejecting `NaN` at
the **parameter** layer is appropriate because parameters control node
behavior and should not carry sentinel values. However, this validation
should be scoped to parameters specifically, not applied as a blanket
rule across all ROS 2 message fields.

### Recommendation

Add finiteness checks in both explicit and inferred DOUBLE paths:

```python
import math

if Parameter.Type.DOUBLE == self:
    return isinstance(parameter_value, float) and math.isfinite(parameter_value)
```

and:

```python
elif isinstance(yaml_value, float):
    if not math.isfinite(yaml_value):
        raise ValueError('floating-point parameters must be finite')
    value.type = ParameterType.PARAMETER_DOUBLE
    value.double_value = yaml_value
```

Apply the same policy to `DOUBLE_ARRAY` values.

---

## Finding 4 — Mixed lists and non-scalar YAML values silently coerce to `STRING`

### Severity: High

### Location

`parameter.py` lines 299–307:

```python
elif all((isinstance(v, str) for v in yaml_value)):
    value.type = ParameterType.PARAMETER_STRING_ARRAY
    value.string_array_value = yaml_value
else:
    value.type = ParameterType.PARAMETER_STRING
    value.string_value = string_value
...
else:
    value.type = ParameterType.PARAMETER_STRING
    value.string_value = yaml_value if yaml_value is not None else string_value
```

### Root cause

When YAML produces a list whose elements are mixed types, the code does not
reject it. Instead, it silently falls back to `PARAMETER_STRING` and stores the
original input text.

Examples:

```python
get_parameter_value('[1, 2.0, "hello"]')
# -> STRING, value '[1, 2.0, "hello"]'
```

Likewise, YAML values outside the supported scalar/array domain also fall back
to STRING. A particularly surprising case is:

```python
get_parameter_value('null')
# yaml.safe_load('null') -> None
# result.type == STRING
# result.string_value == 'null'
```

So the textual YAML spelling `null` does not become `NOT_SET`; it becomes the
literal string parameter `"null"`.

### Impact

- Invalid or unsupported parameter structures are accepted instead of rejected
- Callers may believe the parameter parser validated a list or null-like value,
  when it actually preserved the raw text
- This can mask configuration mistakes and create hard-to-debug mismatches
  between user intent and node state

### Recommendation

Fail closed for unsupported YAML values instead of silently coercing them to
STRING:

```python
else:
    raise TypeError('YAML value does not map to a supported ROS parameter type')
```

If preserving raw text is required for CLI compatibility, expose that as an
explicit fallback mode rather than the default behavior.

---

## Finding 5 — `INTEGER` accepts arbitrary Python ints without int64 bounds

### Severity: High

### Location

`parameter.py` lines 106–107:

```python
if Parameter.Type.INTEGER == self:
    return isinstance(parameter_value, int)
```

`parameter.py` lines 245–246:

```python
elif Parameter.Type.INTEGER == self.type_:
    parameter_value.integer_value = cast(int, self.value)
```

### Root cause

Python integers are arbitrary precision, but ROS parameter integer storage is
backed by a fixed-width signed integer field at the message / C boundary. The
Python validation layer checks only that the value is an `int`; it does not
check that it fits in the representable int64 range.

That means values such as:

```python
2 ** 100
-2 ** 100
```

can be accepted by `Parameter(..., type_=INTEGER, value=...)` even though they
cannot be represented losslessly when encoded into the underlying parameter
message or passed across the C boundary.

### Impact

- Oversized integer parameters are accepted too late in the stack
- The failure mode is deferred to message conversion, binding code, or later
  transport/use, rather than being rejected at parameter construction time
- This mirrors the same boundary-validation pattern seen in the Time/Duration
  reports: Python accepts a value that the fixed-width ROS representation does
  not actually support

### Recommendation

Enforce int64 bounds in both explicit and inferred integer paths:

```python
INT64_MIN = -9223372036854775808
INT64_MAX = 9223372036854775807

if Parameter.Type.INTEGER == self:
    return (
        isinstance(parameter_value, int)
        and not isinstance(parameter_value, bool)
        and INT64_MIN <= parameter_value <= INT64_MAX
    )
```

Add equivalent bounds checks for `INTEGER_ARRAY` and for YAML-derived integer
values in `get_parameter_value()`.

---

## Cross-references

- **ros-report.md** — Threat #3: semantic input handling
- **rclpy/rclpy/rclpy/parameter.py** — audited implementation

## Affected versions

All versions using the current `parameter.py` inference / validation structure.
The specific line numbers above were audited against rolling tag `11.0.1`
(commit `69d5ea9`).
