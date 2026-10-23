# ROUTE #124 — `from m import *` AFTER a `def` rebinds the name silently

**Status: CLOSED AND FULLY GATED by gen #24 (2026-09-15), battery-A (cheap legs, emission vs HEAD, suite 3481/3499 same 18 0 XPASS, planes 34/34 — every leg predicted and hit).**
**Severity: SEV-1. Order 2** (carrier = #118 rule (1)'s import arm, which reads the alias NAMES; a star
import binds names no alias spells).

## MEASURED at HEAD `7c9dede2`
`def inc -> y + 1`, then `from starlib import *` (starlib: `def inc -> y - 1`), `f() = inc(3)` with
`\result == 4` PROVES; CPython 2. The star import leaves no trace in the emission.

## REPAIR (to scope)
Refuse a star import that follows a def/class of the module (conservatively, any star import after
one; census the four trees first).
Driver: `scratchpad/g24/p1/star_after_def.py` (+ `starlib.py`).
