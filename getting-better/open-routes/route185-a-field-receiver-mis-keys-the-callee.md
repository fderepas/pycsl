# ROUTE #185 — a `self.<field>.<m>()` receiver mis-keys the callee, so #167/#176 look up nothing

**Status: CLOSED by gen #29 (battery Y green: suite 3783/3801, same 18 CONFIRMED FAIL, zero XPASS; planes --slow 34/34).**
Severity 1. Generator: carrier-rerun of the landed #167/#176 (receiver spellings).

## Measured at `59611f89`

    class Inner:
        #@ requires self.x != 0
        def get(self) -> int: return self.x // self.x
    class Outer:
        def __init__(self): self.inner = Inner(0)
        #@ ensures \result == 5
        def run(self) -> int:  self.inner.get(); return 5      PROVED   (CPython ZeroDivisionError)

    class Inner:  def go(self, v): 
                      if v < 0: raise ValueError()
                      return v
    #@ ensures \result == 0
    def run(self) -> int:
        try: v = self.inner.go(-1)
        except ValueError: return 9
        return v * 0                                            PROVED   (CPython 9)

Route #100's receiver resolution maps `self.inner.go` to the key `outer__inner_go` — a name no
function of the file carries. Routes #167 (precondition assert) and #176 (may-raise prefix) treat a
non-empty key as authoritative, so they looked up NOTHING and emitted neither obligation. A
`self.<field>.<m>()` call to a missing-key dict reader was already refused by #178 (its scan is
name-based), which is why only these two obligations were missing.

## Repair (draft)

In `_handle_dotted_call`, a resolved key that matches no IR function falls back to the method-name
suffix match (the same fallback the unresolved-receiver case already used). Emission: one corpus file
MOVED — `1277_route97_...` (XFAIL, now carries the R167 assert), pyref and mirrors byte-inert.
Witnesses 1655, 1656 (XFAIL), 1657 (PASS control). Fast planes 19/19, conformance, sync green.
