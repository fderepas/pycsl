r"""Test 5890 -- driver run #3 route #226 polarity flip CONTROL (expected PASS): `self.ok = True` under `self.ok == True`; goal stage 2d states `forall ok : bool. ok = true -> ..`, which discharges.
"""
# pycsl-expected: PASS


#@ class invariant self.ok == True
class C:
    def __init__(self) -> None:
        self.ok = True

    #@ ensures \result == True
    #@ assigns \nothing
    def get(self) -> bool:
        return self.ok


if __name__ == "__main__":
    print(C().get())
