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
