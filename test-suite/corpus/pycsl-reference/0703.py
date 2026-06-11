"""Test 0703 — cross-module inductive predicate (11-0632-spec-8).

A driver imports two functions (`mkdir`, `access`) from `multi_file_lib.inductive_fs`
whose `#@ ensures` reference the module-level `#@ inductive` LOGIC predicate `present`.
The predicate's logic declaration must survive the `from … import …` boundary: the
importer's emitted WhyML must carry the real `inductive present string = …` block so
that `present(filepath)` lowers to the logic application `(present filepath)` — NOT a
program `val present_1 (x0:int):int` (illegal in `ensures`, mistyped `int` vs `string`).

The driver proves a CONSEQUENCE that only the shared `present` law links: after a
successful `mkdir(d)` (rc == 0 ⇒ present(d)), `access(d)` must return 1 (result == 1 ⇔
present(d)). The two trusted stubs share no program state — only the logic predicate
ties the mutator's effect to the observer's reading. Expected PASS."""
_ = 0  # anchor
from multi_file_lib.inductive_fs import mkdir, access


#@ ensures \result == 1
def mkdir_then_access_present(d: str) -> int:
    rc = mkdir(d, 0)
    if rc != 0:
        return 1
    return access(d, 0)
