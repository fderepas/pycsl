# ROUTE #151 — a `@dataclass` `field(init=False)` field was treated as a synthesized constructor PARAMETER

**Status: REPAIR DRAFTED by gen #29 (worktree wt150, with route #150); battery E pending.**
Severity 1. Generator: carrier-rerun (construction neighbourhood of #148-#150).

## Measured at `8ebb31e8` (CPython contradicting)

    @dataclass
    class P:
        y: int = field(init=False, default=5)
        x: int = 0
    P(3).x   #@ ensures \result == 0   <-- PROVED; CPython 3   (record literal { y = 3; x = 0 })
    P(3).y   #@ ensures \result == 3   <-- PROVED; CPython 5

and a base `field(init=False)` field merged into a derived `@dataclass`: `B(3).gety() == 3` PROVED,
CPython 5. The dataclass synthesis walk took every non-`ClassVar`, non-`KW_ONLY` `AnnAssign` as a
positional parameter (route #146 read `field(kw_only=...)` but not `field(init=...)`).

## Repair

The walk skips a field whose `field(...)` call passes `init=False` (constant); the field keeps its
own default channel and the #144 donor list (`dataclass_fields`) inherits the same exclusion.
Witnesses 1507-1509 (XFAIL), 1510 (PASS). `dataclasses.replace` and NamedTuple `_replace` measured
FAIL-CLOSED (the result is an opaque `ref 0`).
