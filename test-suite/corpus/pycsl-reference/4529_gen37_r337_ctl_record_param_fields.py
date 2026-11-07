r"""Test 4529 -- gen #37 route #337 (expected PASS): CONTROL: a class WITH fields is a record; `p.x - p.y` PROVES.
"""
# pycsl-expected: PASS
class Pt:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y

#@ ensures \result == p.x - p.y
def diff(p: Pt) -> int:
    return p.x - p.y

if __name__ == "__main__":
    assert diff(Pt(3, 1)) == 2
