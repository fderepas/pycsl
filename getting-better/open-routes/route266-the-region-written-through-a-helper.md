# OPEN ROUTE #266 — THE HAPPY REGION-INTEGRITY CHECK IS BYPASSED THROUGH A HELPER FUNCTION

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Red-team round 3; driver-reproduced at HEAD 13451c8d (rc=0; CPython
disk[600] = 9). Witness `witnesses-r266/h05_happy_write_via_helper.py`: region 512..2560 / writes self.disk outside
region / except _write_meta; non-exempt `evil` calls module fn `poke(self.disk, 600)` which does `a[i] = 9`.
Mechanism: the per-site check is injected only at direct `self.<field>[i] = ...` writes; the by-reference array write
inside the helper is unchecked (the docs claim callees are caught "at their own site" — only for self.<field> writes).
Repair: any call passing a protected field (or an alias) to a callee that may write its parameter must be refused or
carry the region obligation over the callee's frame (writes on the param).

## Probe table (283d1033 = base; every row CPython-writes/reads the protected cell)
| shape | base | after |
|---|---|---|
| h05: module helper `poke(self.disk, 600)` writes `a[i]` | PROVED | refused (E) — 2810 |
| method of another class `h.poke(self.disk, 600)` | PROVED | refused (E) — 2811 |
| getter `return self.disk`, caller writes `d[600]` | PROVED | refused (E) — 2812 |
| `poke2(self)` writes `s.disk[600]` | PROVED | refused (W) — 2813 |
| `o.disk[600] = 9` on another instance | PROVED | refused (W) — 2814 |
| module function writes `s.disk[600]` | PROVED | refused (W) — 2815 |
| `protects d.disk`: `poke(d.disk, 600)` | PROVED | refused (E) — 2816 |
| parametric footprint: `poke(d.disk, 900)` | PROVED | refused (E) — 2817 |
| `protects d.disk`: a `Disk` method writes `self.disk[600]` | PROVED | refused (W) — 2818 |
| read form: `peek(self.secret, 1)` reads `a[1]` | PROVED | refused (E) — 2819 |
| read form: `o.secret[1]` | PROVED | refused (R) — 2825 |
| local alias `x = self.disk; x[600] = 9`, nested helper, tuple target, `del`, `.insert` | failed by accident (Why3 type error / other refusal) | refused (E/W) |
| control: exempt owner passes self.disk to a helper; non-exempt direct out-of-region write | PROVED | PROVED — 2820 |

## Repair (gen #36, 2026-10-17)
Rule (inline in `Module3_Weaver._expand_happy_properties`, before the per-form branches; fail-closed by
rejection, keyed on the protected FIELD NAME = last path component, in every non-exempt
body-verified function — `\trusted`/`\abstract` bodies stay under the existing trust-boundary rules):
- **(E) escape**: a non-scalar protected field may appear only as a subscript base `X.f[...]` or as
  `len(X.f)`. Passing it, aliasing it, returning it, putting it in a container or calling a method on it
  hands out a reference the per-site check cannot follow. An EXEMPT owner may still pass it as a call
  argument (the helper writes under the owner's authority) but may not return/alias it. Scalar = some
  store types it `int`/`bool`/`float`/`str` (annotation or constant initialiser) and none gives it a
  container/object.
- **(W) spelling**: a write / augmented / annotated / `del` / destructuring store reaching `.f` through any
  spelling other than the canonical one the per-form sites stamp is refused (`__init__` may still create
  `self.f`). This also covers passing the OWNING OBJECT (`poke2(self)`): the helper's own write is refused.
- **(R) read form**: a read `X.f[i]` with `X` other than `self` is refused.
The existing refusals keep their own spellings (whole-field rebinding A2, parametric slice/whole R3b,
the read form's `x = self.f` alias, trust boundaries), so no witnessed refusal is shadowed.

Blast radius: corpus root 0 MOVED / 0 GONE (1740/1745 .mlw, 5 new sources); pyref 0 MOVED (2186);
mirror 0 MOVED (53). `--no-proof` census over every `#@ happy` file (corpus + `pycsl_lib` +
`pycsl_lib_test` + route witnesses): one mover, `src/pycsl_lib_test/formal_happy_world.py`, which relied
on shape 2818 — `MiniClock.monotonic` / `MiniFs.sys_write`/`sys_open` / `MiniProc.umask_set`/`chdir` write
the protected fields as `self.<f>` while not exempt. Their names are added to the `except` sets (they ARE
the owners); the file re-proves (base and after: SUCCESS). `pycsl_lib/tm` and `enm` kept (scalar fields).

Residuals: module-level statements outside any function are not scanned; an exempt owner that passes the
field to a helper which itself stores the reference somewhere (a second-order alias) is trusted as the
owner's authority; `getattr`/`setattr` spellings are left to the existing getattr/dynamic planes; a field
of an unrelated class that happens to share the protected field's NAME is now confined too (fail-closed
over-approximation). Side finding: corpus `1742` spells the read form `reading self.secret / region ...`,
which the parser rejects ("expected 'region'/'targets'/'protects'") — its FAIL is a parse error, not the
alias refusal its docstring claims.
