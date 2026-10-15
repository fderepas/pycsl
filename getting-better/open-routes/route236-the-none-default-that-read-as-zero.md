# OPEN ROUTE #236 — THE `@dataclass` FIELD WHOSE `None` DEFAULT READ AS ZERO

**Status: OPEN (gen #36, 2026-10-15), Severity 1.** Found by the ch10 chain agent while measuring the
Optional/defaulted-record-field seam; driver-reproduced at HEAD 50b5fa16 (rc=0, "All contracts formally proven").

## Witness (PROVED at HEAD; CPython `g(5)` returns 2)
`witnesses-r236/dataclass_none_default_reads_zero.py`:

    @dataclass
    class P:
        x: int
        k: Optional[int] = None

    #@ ensures \result == 1        <-- PROVED
    #@ assigns \nothing
    def g(c: int) -> int:
        p = P(c)
        if p.k == 0:
            return 1
        return 2

Emission: `let p = { x = c; k = 0 } in if (p.k = 0) ...`. Siblings (also PROVED at HEAD, per the agent):
`u1_optint_eq0` (`\result.k == 0`), `u2_optstr_eq0` (`Optional[str]`, `\result.name == 0`),
`u5_optlist` (`Optional[List[int]]`, `\result.items == 0`).

## Mechanism
Route #183's shape on a second channel. `Module5_IREmitter.py`'s dataclass class-body default collector
sends a `None` default to `pass` (`isinstance(_rhs145, (ast.Constant, ast.Dict, ...)): pass`, ~L3620,
comment: None is "carried by its own channel" — no channel carries it). `expressions.py::_field_default`
(~L14132) then falls through to `defaults.get(fn, 0)`: a DEFINITE `0` for an omitted `Optional[...]`
field that collapses to `int`.

## Related (agent probes)
- Explicit `P(c, None)` -> opaque `pycsl_none`, does not prove (correct).
- `name: str = "w"` omitted -> `name = 0` against a `string` field: Why3 type error (fail-closed by luck).
- `float = 2.5` -> `2` against `real`: type error (fail-closed by luck).
- Corpus: 20 class-body `= None` sites (0772-0776, 0746, 0750, 0941, 0962-0965); Dict/Set ones get a
  definite empty map.

## Repair direction
Record class-body `None` defaults in `field_none_defaults` (int -> `pycsl_none`, str -> `pycsl_none_str`);
capture class-body literal defaults faithfully (str into `field_str_defaults`, float as real) or leave the
field UNCONSTRAINED — never a wrong definite value. Agent's scratch patch:
scratchpad ch10/seam-scratch-full.patch (session scratchpad; re-derive, do not trust).
