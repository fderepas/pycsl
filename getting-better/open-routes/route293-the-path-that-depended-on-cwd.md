# OPEN ROUTE #293 — os.path.relpath IS MODELLED PURE BUT READS THE CWD
**Status: OPEN (gen #37, 2026-10-20), Severity 1.** Red-team round 8; driver-reproduced at 8d906404 (rc=0; CPython violates).
Witnesses `witnesses-r293/`. os001/os003 `r1 = relpath(s, "/usr"); os.chdir("/"); r2 = relpath(s, "/usr"); #@ check r1 == r2` proves; CPython differs. `_OS_PATH_PURE_STR` includes relpath (and possibly abspath/realpath/expanduser) whose result depends on the cwd/home/filesystem. Repair: make cwd-dependent path functions opaque per call (or depend on a modelled cwd), census `_OS_PATH_PURE_STR`.
