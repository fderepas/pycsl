r"""Test 9031 -- route #566 (control / advice, expected PASS): the refusal's first advice followed -- the node is built with the extra entry already present (a dict display carrying every key), no item store
"""
# pycsl-expected: PASS
from typing import Any, Dict

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ assigns \nothing
    def tagged(self, k: str, an: str) -> "ExprIR":
        d = {"type": "Var", "name": k, "act_name": an}
        return d
