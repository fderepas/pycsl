r"""Test 9257 -- route #577 CONTROL (expected PASS at base and HEAD): a `.value` / `.name` that is NOT an Enum member's is not
judged: record fields named `value` and `name` holding strs, searched for a str needle.
"""
# pycsl-expected: PASS
from dataclasses import dataclass


@dataclass
class Q:
    value: str
    name: str


#@ no_exception \all
def f1(c: str, q: Q) -> int:
    return 1 if c in q.value or c in q.name else 0


if __name__ == "__main__":
    print(f1("a", Q("ab", "c")))
