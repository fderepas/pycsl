# ROUTE #157 — a slice assignment that RESIZES the list is modelled as a fixed-length blit

**Status: CLOSED AND FULLY GATED by gen #29 (2026-09-16), battery G (with #155/#156).** Severity 1.
Generator: carrier-rerun (route #81's alias fence led to the no-alias shape).

## Measured at `52a02d5a`

    a = [1, 2]; a[2:] = [3, 4]; return len(a)     #@ ensures \result != 4   PROVED (CPython 4)
    a = [1, 2]; a[0:1] = [7, 8]; return a[1]      #@ ensures \result != 8   PROVED (CPython 8)

`_handle_array_slice_set_stmt` emits `Array.blit src 0 dst lo (hi - lo)`; Why3's precondition only
needs `hi - lo <= length src`, so a longer source is truncated and the list never grows.

## Repair

`pycsl.py::_run_pipeline` appends `assert { Array.length <src> = (<width>) }` after the emitter's own
per-element hint on the emitted text (the handler is a converted mirror method; `_run_pipeline` is
trusted and already rewrites nothing else). Equal-length stores keep their model (all 9 PASS
corpus files with slice stores re-prove); resizing ones fail to prove. Witnesses 1531/1532 (XFAIL),
1533 (PASS control).

**Battery G (every leg predicted and hit):** emission vs the #152-#154-closed tree 1170 -> 1180 with
EXACTLY the ten predicted corpus files MOVED (the slice-store files; each diff is one appended length
assertion per store), python-reference and mirrors inert; conformance 38/38 + 38/38; suite 3659/3677
same 18, zero XPASS; planes --slow 34/34; dropped-mutation TRYFINAL ratchet 9 -> 5.
