r"""Test 9295 -- route #579 CONTROL (expected PASS at base 822621340 and HEAD): R579's advice followed on 9270: the value annotated with the class it really has (`node: CSLFieldAccess`, no `isinstance`, no IR typing), so `node.kind` is the record field and the honest two-sided claim proves
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class CSLFieldAccess:
    obj: str
    kind: str


#@ ensures \result == 1 ==> node.kind == "keys"
#@ ensures node.kind == "keys" ==> \result == 1
#@ assigns \nothing
def probe(node: CSLFieldAccess) -> int:
    if node.kind == "keys":
        return 1
    return 0


if __name__ == "__main__":
    print("result", probe(CSLFieldAccess("o", "keys")), probe(CSLFieldAccess("o", "vals")))
