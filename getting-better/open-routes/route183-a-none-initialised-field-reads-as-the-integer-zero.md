# ROUTE #183 — a field whose only initialiser is `None` reads back as the integer 0

**Status: CLOSED by gen #29 (battery V green: suite 3776/3794, same 18 CONFIRMED FAIL, zero XPASS; planes --slow 34/34).** Severity 1.
Generator: hand (the None-as-zero carriers measured against the open route #56).

## Measured at `57dd2d87`

    class C:
        def __init__(self) -> None:
            self.v: Optional[int] = None
    #@ ensures \result == True
    def probe() -> bool:  c = C(); return c.v == 0        PROVED   (CPython False)

Emitted `let c = { v = 0 }`: `_field_default`'s scalar fallback is the captured int, default 0, and a
`None` initialiser captures nothing. Route #56 records the same shape for Optional LOCALS and gen #29
measured it for LIST ELEMENTS and DICT VALUES too (recorded in route56); this repair closes the FIELD
carrier, which needs no new value model.

## Repair (draft)

Module 5 `_collect_class_fields` collects the fields whose `__init__` stores are ALL the literal
`None` (a field later assigned a real value is not collected) into the additive type_decl key
`field_none_defaults`; `preamble` copies it into `rec_info`; `_field_default` returns route #44's
opaque `pycsl_none` for them instead of `0`. The comparison becomes UNDECIDED — the false claim and
its true twin are both refused (witnesses 1648, 1649), while a field assigned a real value keeps its
captured default (1650 proves). Emission byte-inert (corpus/pyref/mirrors); fast planes 19/19,
conformance, sync green.

## Still open (route #56 family)

Optional LOCALS (route #56 itself), LIST ELEMENTS, DICT VALUES, and `None` used in arithmetic still
read as the carrier's zero — same repair capability (a distinguishable `None` in the value model).
