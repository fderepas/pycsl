#!/usr/bin/env python3
"""Mark route #190 CLOSED once battery AB2 is green."""

BATTERY = ("**Status: CLOSED by gen #29 (battery AB green: suite 3797/3815, the same 18 "
           "CONFIRMED FAIL, zero XPASS; planes --slow 34/34; emission 16 corpus + 8 mirror "
           "emissions MOVED, pyref byte-inert).**\nSeverity 1.")

path = "getting-better/open-routes/route190-an-open-ended-string-slice-is-the-empty-string.md"
old = ("**Status: REPAIR DRAFTED by gen #29 (worktree wtAJ, branch wip/g29-r190, on top of "
       "#189).** Severity 1.")
s = open(path).read()
assert old in s
s = s.replace(old, BATTERY, 1)
s = s.replace("## Repair (draft)", "## Repair", 1)
open(path, "w").write(s)
print("closed", path)

p = "getting-better/open-routes/probes.tsv"
s = open(p).read()
s = s.replace("abstract-op-ensures\tROUTE\t190", "abstract-op-ensures\tCLOSED\t190", 1)
open(p, "w").write(s)
print("probes.tsv updated")
