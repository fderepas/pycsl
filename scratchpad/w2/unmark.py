#!/usr/bin/env python3
"""Remove the SHADOWED-SELFCALL REPAIR note + `#@ sibling_concrete` above a method."""
import re, sys
def unmark(path, meth):
    lines = open(path).read().split("\n")
    di = None
    for i, l in enumerate(lines):
        if re.match(r"^    def %s\(" % re.escape(meth), l):
            di = i; break
    if di is None: return "NO-DEF"
    j = di
    while j > 0 and (lines[j-1].lstrip().startswith("#@") or lines[j-1].lstrip().startswith("#")):
        j -= 1
    # find the note start and the sibling_concrete line within [j, di)
    out = []
    k = j
    while k < di:
        if lines[k].startswith("    # SHADOWED-SELFCALL REPAIR"):
            while k < di and not lines[k].strip() == "#@ sibling_concrete":
                k += 1
            k += 1   # skip the marker line itself
            continue
        out.append(lines[k]); k += 1
    if len(out) == di - j: return "NOT-MARKED"
    lines[j:di] = out
    open(path, "w").write("\n".join(lines))
    return "UNMARKED"
if __name__ == "__main__":
    print(unmark(sys.argv[1], sys.argv[2]))
