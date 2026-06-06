"""0421 — array-int instance fields (Phase 1 of remove-trusted-unixfs).

Foundation test for the UnixInodeFileSystem de-trust rewrite: a class
with `array int` instance fields declared via a bare `list` annotation
(`self.disk: list = bytearray(...)`), exercised with element read and
element write through a method body that must emit as `let` (body
verified), not `val` (trusted).

Validates:
  * Module5 `_field_type_from_annotation` honours a bare `list`
    annotation on `self.x` → field type "list" → `array int` in the
    WhyML record (not the legacy `int` default).
  * Module6 subscript-write `self.disk[i] <- v` on a record-array field.
  * Two distinct array fields coexist in one record.
"""

DISK_SIZE = 16


#@ class invariant \length(self.disk) == 16
#@ class invariant \length(self.aux) == 16
class TinyDisk:
    def __init__(self):
        self.disk: list = bytearray(DISK_SIZE)
        self.aux: list = bytearray(DISK_SIZE)

    #@ requires 0 <= i and i < 16
    #@ requires 0 <= v and v < 256
    #@ assigns self.disk
    #@ ensures \result == v
    def set_get(self, i: int, v: int) -> int:
        self.disk[i] = v
        return self.disk[i]

    #@ requires 0 <= i and i < 16
    #@ assigns self.aux
    #@ ensures True
    def touch_aux(self, i: int) -> None:
        self.aux[i] = 1
