# ROUTE #92 — the PARAMETRIC (R3 `footprint`) confinement form is PROVED while a
# non-exempt, footprint-less function overwrites the protected per-object region
# — and its collector's docstring NAMES a guard that does not cover the case

**STATUS: OPEN — FULLY MEASURED, REPAIR NOT YET LANDED (gen #13, 2026-09-13). SEVERITY 1. TWO CARRIERS.**
Found within the hour of #91, by the generator #91 itself produced.

## MECHANISM

`Module3_Weaver._weave_happy`, R3 parametric branch (`hp.param is not None`), realises
`happy N(n): protects <path>[lo(n) : hi(n)] except …` by collecting write sites with
`_collect_protect_index_sites` and injecting, per site, either the substituted
containment check (if the writer declared `#@ footprint N(arg)`) or `CSLBool(False)`
(non-exempt with no footprint → forbidden).

`_collect_protect_index_sites` matches **only a POINT write** — `isinstance(tgt,
ast.Subscript)` with a non-`Slice` index. Its own docstring says so, and then says what
happens to the rest:

> *"(Slice/whole-array writes to a parametric path are not certifiable per-object; they
> are left to the **non-footprint reject**.)"*

**THERE IS NO SUCH REJECT.** The only "non-footprint reject" in the branch is
`pred = CSLBool(False)` at line 850 — and it fires **only on sites the collector already
returned**, which by construction are exactly the point writes. A slice or whole-array
store to the protected path is in no list, gets no check, and is rejected by nothing.
The branch `continue`s before the R1/R2 `protects` form, which *would* have caught both
(it matches `_target_dotted_path`), so nothing downstream saves it either.

>>> **THE DOCSTRING DEFERS THE TWO HARDEST CASES TO A GUARD THAT, BY THE COLLECTOR'S OWN
>>> MATCHING RULE, CAN NEVER SEE THEM. A DEFERRAL IS A CLAIM ABOUT ANOTHER PIECE OF CODE,
>>> AND IT IS THE ONE KIND OF CLAIM NOBODY RE-READS — the author who writes "handled over
>>> there" and the reader who reads it are never the same person on the same day.**

## BOTH DIRECTIONS MEASURED, BOTH CARRIERS, ON THE 0614 SHAPE

`happy inode_conf(n): protects d.disk[512 + n*64 : 512 + (n+1)*64] except formatter`.

| driver (non-exempt, NO `#@ footprint`) | claim | verdict |
|---|---|---|
| **control** `d.disk[600] = v` (point write) | guard fires | **REFUSED** (`check False`) |
| **control** 0614's `writer` with its footprint | capability alive | **PROVED** |
| **carrier 1** `d.disk = a` (whole-array) | file verifies | **VERIFIED** |
| carrier 1 + `requires a[512] == 99`, `ensures d.disk[512] == 99` | region took attacker value | **PROVED** |
| carrier 1 + `requires d.disk[512] == 7`, `ensures d.disk[512] == 7` | region preserved | **REFUSED** |
| **carrier 2** `d.disk[512:576] = a` (slice) | file verifies | **VERIFIED** |
| carrier 2 + `requires d.disk[512] == 7`, `ensures d.disk[512] == 7` | region preserved | **REFUSED** |

Index 512 is inside object 0's region [512, 576). The last row is what makes carrier 2
a real carrier rather than an erasure artefact: **the slice store is NOT erased** — the
model refuses the claim that the cell survived it — so the write genuinely lands in the
protected region while the property asserting per-object containment proves.

Per the #86 lesson, both carriers were measured BEFORE the repair, so neither could be
masked by fixing the other, and both were re-measured after.

## RELATION TO #91 — THE SAME DEFECT, THE THIRD BRANCH OF THE SAME FUNCTION

#91 was the region-write form missing a whole-field rebinding. #92 is the parametric form
missing whole-array **and** slice. Completing the table from #91's record:

| form | point write | whole-path store | slice store | alias |
|---|---|---|---|---|
| `protects` (R1/R2) | caught | **caught** (dotted path) | **caught** (dotted path — `_target_dotted_path` strips the trailing subscript) | `x = self` caught |
| `reading` (H-I1) | caught | n/a | n/a | caught explicitly |
| region-write | caught | **was MISSED → #91** | caught (`kind: slice`) | type accident only |
| **parametric (R3)** | caught | **was MISSED → #92** | **was MISSED → #92** | type accident only |

**The one form that keys on the PATH is the one form with no holes.** The two forms that
key on the syntactic SHAPE of the target each missed a different subset — and each missed
a *strictly more destructive* write than the one it caught.

## REPAIR

Same discipline as #91 and as `_check_protect_aliasing`: sound-by-rejection. In the R3
branch, a non-exempt function containing a store whose `_target_dotted_path` is the
protected path but which is **not** a point subscript (i.e. a whole-path store or a slice
store) is a hard error — a per-index footprint check cannot constrain it, so there is
nothing to defer. `__init__` is exempt (it creates the field).

The collector docstring's false deferral was corrected in the same increment: it now says
the cases are rejected, and names where.

## GATES

(see the progress-log entry and the #91 record; batteries were run over both repairs
together, with the byte-diff entries predicted in advance)
