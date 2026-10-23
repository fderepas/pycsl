# ROUTE #170 — a CAUGHT missing-key dict read proves the placeholder value, erasing the handler

**Status: CLOSED by gen #29 (battery N green: suite 3717/3735, same 18 CONFIRMED FAIL, zero XPASS; planes --slow 34/34).** Severity 1. Generator: hand
(implicit-exception handler probes).

## Measured at `bd4054d3`

    #@ ensures \result == 0
    def probe() -> int:
        d: Dict[str, int] = {"a": 1}
        try:
            v = d["b"]
        except KeyError:
            return 9
        return v                                  PROVED   (CPython 9)

Same with an int-keyed dict and under `except Exception`. Emitted read:
`(match Map.get !d "b" with | Some v_ -> v_ | None -> 0 end)` inside `try ... with KeyError -> ...`.
The `None ->` placeholder (`_dv_missing_default`) is documented as "proven dead under
`#@ no_exception KeyError`, the ambient default otherwise": the ambient convention lets an UNCAUGHT
KeyError go unmodelled, but a CAUGHT one is an ordinary control-flow path, and the placeholder
deleted it. Controls refused at HEAD: IndexError / ZeroDivisionError / ValueError caught in the same
function; errors raised in a helper and caught by the caller (function or method).

## Repair (draft)

In `_handle_subscript` (trusted), when the function being emitted (`_current_sig_func_name`) contains
a `try` handler that can catch KeyError (KeyError, LookupError, Exception, BaseException, bare or
unrecognised handler type), the missing-key arm is `(raise KeyError)`. Under `except KeyError` the
handler path is modelled faithfully (control 1586 proves `\result == 9`); under a broader handler
KeyError is undeclared and Why3 refuses (fail-closed); reads outside the `try` in such a function
become unprovable escapes (completeness only). Emission: corpus/pyref/mirrors byte-inert.
Witnesses 1583–1585 (XFAIL), 1586–1587 (PASS). Fast planes 19/19, conformance, sync green.

## WATCH (recorded, not a route)

An UNCAUGHT missing-key read (`return d["b"]`, no try, no `no_exception`) still proves under the
ambient convention, while an uncaught list IndexError and a ZeroDivisionError are always checked.
The asymmetry is documented design (#57), not a contradiction of a stated claim.
