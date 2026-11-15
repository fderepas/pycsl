# OPEN ROUTE #606 — After isinstance(v, float), v == v is decided true (hval_eq reflexive on HFloat); CPython NaN != NaN; FLOAT-FINITE is not surfaced by --soundness-report for these programs and --strict-float-finite has no effect
**Status: OPEN, Severity 1. Red team rt59 family R4 (scratchpad/rt59/FINDINGS.txt, families.txt, logs/). See FINDINGS for INTRODUCED (proves on int61, refused / fails on L9 and 73fd1874f) vs PRE-EXISTING members. Lands with the dict value model r4 (int61): every INTRODUCED member must be refused before L10.**
Witnesses witnesses-r606/.
