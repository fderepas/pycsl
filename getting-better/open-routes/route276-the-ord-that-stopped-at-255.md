# OPEN ROUTE #276 — `ord(s) < 256` / `ord(chr(n)) == n` FOR CODE POINTS >= 256 (residual of route #69)
**Status: OPEN (gen #36, 2026-10-18), Severity 1.** Red-team round 5; driver-reproduced at HEAD (s11/s12 rc=0; CPython 8364/300).
Witnesses `witnesses-r276/`. `ord_op` ensures `0 <= result < 256` (Why3 Char covers 0..255); #69's guard only catches
locals bound to non-ASCII literals. Repair: `ord` of an arbitrary str returns a code point in [0, 0x10FFFF] (no < 256
bound unless provably ASCII); `chr(n)` for n >= 256 must not round-trip through Char; ord("")/ord("ab") under
no_exception must owe len == 1.
