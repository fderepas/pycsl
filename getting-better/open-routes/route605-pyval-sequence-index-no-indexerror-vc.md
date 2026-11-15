# OPEN ROUTE #605 — Indexing a PyVal list / tuple / str lowers to hval_nth_str with no bounds VC, so no_exception IndexError proves on an out-of-range index
**Status: OPEN, Severity 1. Red team rt59 family R3 (scratchpad/rt59/FINDINGS.txt, families.txt, logs/). See FINDINGS for INTRODUCED (proves on int61, refused / fails on L9 and 73fd1874f) vs PRE-EXISTING members. Lands with the dict value model r4 (int61): every INTRODUCED member must be refused before L10.**
Witnesses witnesses-r605/.
