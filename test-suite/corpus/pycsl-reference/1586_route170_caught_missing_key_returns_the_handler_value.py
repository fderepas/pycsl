r"""Test 1586 - ROUTE #170 control (gen #29): with the missing-key arm raising, the handler path is modelled and `\result == 9` PROVES (FAILS at HEAD).
"""
from typing import Dict
_ = 0  # anchor


#@ ensures \result == 9
def probe() -> int:
    d: Dict[str, int] = {"a": 1}
    try:
        v = d["b"]
    except KeyError:
        return 9
    return v
