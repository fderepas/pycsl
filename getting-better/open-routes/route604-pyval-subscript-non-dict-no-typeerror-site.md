# OPEN ROUTE #604 — Subscripting a PyVal that is not a dict is not a TypeError site under \\all (the KeyError check has a | _ -> true arm; the wrong-tag pass does not cover subscripts)
**Status: OPEN, Severity 1. Red team rt59 family R2 (scratchpad/rt59/FINDINGS.txt, families.txt, logs/). See FINDINGS for INTRODUCED (proves on int61, refused / fails on L9 and 73fd1874f) vs PRE-EXISTING members. Lands with the dict value model r4 (int61): every INTRODUCED member must be refused before L10.**
Witnesses witnesses-r604/.
