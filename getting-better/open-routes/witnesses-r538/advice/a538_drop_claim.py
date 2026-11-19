from typing import Any, Tuple

# route #538 advice probe: g1105/bf1047 with the `no_exception` claim dropped; expected to VERIFY.


def f(t: Tuple[int, Any], u: Tuple[int, Any]) -> int:
    return 1 if t < u else 0
