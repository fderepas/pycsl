#!/usr/bin/env python3
"""Insert `#@ sibling_concrete` immediately above a method's `#@ requires` line."""
import re, sys

NOTE = ("    # SHADOWED-SELFCALL REPAIR (lesson (ay)): CONVERTED and PROVED, yet every\n"
        "    # `self.%s(...)` call site in this file went through the receiver-less abstract\n"
        "    # `val self__%s_<n>`, whose result is UNCONSTRAINED — so no caller saw anything\n"
        "    # this body computes. The opt-in marker is the SECOND admission route into the\n"
        "    # concrete lowering; the first (`_record_array_fields`) is a PROXY that holds only\n"
        "    # for the parser-cursor shape and is empty for this file. Sound: the callee is a\n"
        "    # same-file VERIFIED method in `_module_func_names`, and `scc.find_self_method_calls`\n"
        "    # already supplies the callee-before-caller ordering edge for a marked callee.\n"
        "    # Corpus byte-inert BY CONSTRUCTION — no corpus program writes the directive.\n"
        "    #@ sibling_concrete\n")

def mark(path, meth):
    src = open(path).read()
    lines = src.split("\n")
    # find the def line
    di = None
    for i, l in enumerate(lines):
        if re.match(r"^    def %s\(" % re.escape(meth), l):
            di = i
            break
    if di is None:
        return "NO-DEF"
    # walk up over the contiguous `#@`/comment block
    j = di
    while j > 0 and (lines[j-1].lstrip().startswith("#@")
                     or lines[j-1].lstrip().startswith("#")):
        j -= 1
    block = "\n".join(lines[j:di])
    if "#@ sibling_concrete" in block:
        return "ALREADY"
    if "\\trusted" in block:
        return "TRUSTED-SKIP"
    if "#@ requires" not in block and "#@ ensures" not in block:
        return "NO-CONTRACT"
    lines.insert(j, (NOTE % (meth, meth)).rstrip("\n"))
    open(path, "w").write("\n".join(lines))
    return "MARKED"

if __name__ == "__main__":
    print(mark(sys.argv[1], sys.argv[2]))
