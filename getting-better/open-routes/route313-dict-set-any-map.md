# OPEN ROUTE #313 — DICT/SET VALUES LOWERED TO `(any_map ())` DROP THEIR EFFECTS (display args, dict-returning calls, field stores)
**Status: OPEN (gen #37, 2026-10-23), Severity 1.** Red-team round 15; driver-reproduced on main 65b22999 (rc=0; CPython violates).
Witnesses `witnesses-r313/`: `gd({0: inc(xs)})` (t04), `len({0: inc(xs)})` -> `let _ = (any_map ()) in 1` (i04): a dict display is lowered
faithfully only when the enclosing function returns a map (expressions.py ~21780), otherwise `(any_map ())` — #310's text check
passes vacuously; `gd(mkd(xs))` with Dict-typed param emits `(gd (any_map ()))`, the call vanishes (s09; set variant s02 `gs(mks(xs))`);
field store `k.d = {0: inc(xs)}` / `{**mkd(xs)}` -> `k.d <- (any_map ())` (u01, u07; statements.py ~3285).
Repair: never replace an expression containing an effectful call by `(any_map ())`/`(any_set ..)`: evaluate effects in order then havoc
the value, or refuse. Census every `any_map`/`any_set`/`any_array` emission site.
