#!/usr/bin/env python3
"""Mark routes #187, #188 and #189 CLOSED once battery AA is green."""
import re

BATTERY = ("**Status: CLOSED by gen #29 (battery AA green: suite 3793/3811, the same 18 "
           "CONFIRMED FAIL, zero XPASS; planes --slow 34/34; emission byte-inert in all "
           "three directions).**\nSeverity 1.")

FILES = {
    "getting-better/open-routes/route187-fresh-globals-ignores-the-module-body.md":
        "**Status: REPAIR DRAFTED by gen #29 (worktree wtAI, branch wip/g29-r187, on top of #186).** Severity 1.",
    "getting-better/open-routes/route188-the-stub-name-hash-suffix-collides.md":
        "**Status: REPAIR DRAFTED by gen #29 (worktree wtAI, branch wip/g29-r188, on top of #187).** Severity 1.",
    "getting-better/open-routes/route189-one-receiver-name-two-classes.md":
        "**Status: REPAIR DRAFTED by gen #29 (worktree wtAI, branch wip/g29-r189, on top of #188).** Severity 1.",
}

for path, old in FILES.items():
    s = open(path).read()
    assert old in s, path
    s = s.replace(old, BATTERY, 1)
    s = s.replace("## Repair (draft)", "## Repair", 1)
    open(path, "w").write(s)
    print("closed", path)

p = "getting-better/open-routes/probes.tsv"
s = open(p).read()
for gen_tag in ("pb12-fresh-globals\tROUTE\t187",
                "r166-stub-suffix-hash\tROUTE\t188",
                "r188-lesson-lossy-resolution\tROUTE\t189"):
    s = s.replace(gen_tag, gen_tag.replace("\tROUTE\t", "\tCLOSED\t"), 1)
open(p, "w").write(s)
print("probes.tsv updated")
