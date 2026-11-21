r"""Test 1673 - ROUTE #191 carrier (gen #30): a `None` STORED into a list element read back as the integer 0. Route #184 gave a `None` ELEMENT OF A LIST LITERAL route #44's opaque, but the STORE position went through the TYPED `NoneExpr` arm of `_expr_to_whyml`, which still answered the literal `0`. So `xs[0] = None` then `xs[0] == 0` PROVED True while CPython says False. The general repair of route #56 - the typed arm answers the same opaque `pycsl_none` - closes it: the read is UNDECIDED.
"""
# pycsl-expected: FAIL
from typing import List, Optional

_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    xs: List[Optional[int]] = [1]
    xs[0] = None
    v = xs[0]
    if v == 0:
        return 1
    return 2
