# OPEN ROUTE #607 — A bytes literal flowing into a PyVal is tagged HArr of ints, so isinstance(v, list) is true, isinstance(v, bytes) false and b'' == [] true
**Status: OPEN, Severity 1. Red team rt59 family R5 (scratchpad/rt59/FINDINGS.txt, families.txt, logs/). See FINDINGS for INTRODUCED (proves on int61, refused / fails on L9 and 73fd1874f) vs PRE-EXISTING members. Lands with the dict value model r4 (int61): every INTRODUCED member must be refused before L10.**
Witnesses witnesses-r607/.
