"""Test 0733 — negative: `Literal[b"x"]` rejected (L4a / PEP 586).

typing-engagement ty1 (26-0000-typing-spec-2): `bytes` literals are NOT
permitted as `Literal` arguments (L4a — PEP 586 restricts `Literal` to
int/str/bool/None literals). The front-end normalization
(`_normalize_literal_annotation` → `_classify_literal_value`) rejects the
annotation with a clear error before any WhyML is emitted. The run terminates
with a PIPELINE ERROR (exit 1).
"""
# pycsl-expected: FAIL
from typing import Literal

#@ assigns \nothing
def f(x: Literal[b"x"]) -> int:
    return 0
