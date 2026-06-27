from typing import Callable


# R3 SHIM NO-ENFORCEMENT (runtime gate): the `typing.Callable` shim is an
# introspectable alias object (R1) with NO signature check (R3). `Callable[[int],
# int]` is subscriptable and returns an alias; the builtin `callable(x)` is a
# PRESENCE check (R2), signature-agnostic. Nothing enforces the signature at
# runtime (S3's central negative sentence: the runtime does not enforce
# annotations). This driver exercises the shim surface only — it carries no
# static proof obligation (the static plane is exercised by the S5 drivers).

alias = Callable[[int], int]
present = callable(alias)
