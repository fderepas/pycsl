r"""Test 9276 -- route #579 (expected FAIL: PROVED at base 822621340 in the default model, REFUSED PYCSL-R579-IR-CLASS-NOT-RESOLVED in every model; red team 55 probe (u36 probe p579c)): `import ast` at module level, but the method's PARAMETER named `ast` shadows it: `ast.Name` is the caller's class, not the standard library's; CPython returns 1 under `ensures \result == 0`
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def mutable_state(cls): return cls

import ast

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def probe(self, node: "ExprIR", ast: Any) -> int:
        if isinstance(node, ast.Name):
            if node.kind == "keys":
                return 1
        return 0


@dataclass
class N:
    id: str
    kind: str


class K:
    Name = N


if __name__ == "__main__":
    try:
        r = Em().probe(N("zz", "keys"), K())
        print("VIOLATION contract" if r != 0 else "result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
