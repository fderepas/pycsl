# qtab.py <logA> <logB> [tagA tagB] : join two D.sh / r.sh outputs by probe key; print rows where the class differs (or all with -a)
import sys, re
def cls(line):
    if "Verification SUCCESS" in line: return "SUCCESS"
    if "does NOT type-check" in line: return "TC-FAIL"
    if "PIPELINE ERROR" in line:
        m = re.search(r":: \[!\] PIPELINE ERROR: :: (.*)$", line)
        t = m.group(1) if m else ""
        for k, v in (("uses `", "REF:MODULE-VALUE"), ("module-level hook", "REF:MODULE-HOOK"),
                     ("manipulates the import system", "REF:STATE-MANIP"), ("imports the standard li", "REF:STATE-MANIP(dep)"),
                     ("stores (line", "REF:REBOUND"), ("wildcard import", "REF:WILDCARD"), ("rebound after its definition", "REF:rebound-name"),
                     ("runtime value is not", "REF:runtime-value"), ("[ir-semantic]", "REF:#483")):
            if k in t: return v
        return "REF:other"
    if "Verification FAIL" in line: return "FAIL"
    return "OTHER"
def load(f):
    d = {}
    for l in open(f):
        l = l.rstrip("\n")
        m = re.match(r"^(?:\[[^\]]*\] )?(\S+) (?:hdr=\S+ )?rc=", l)
        if m: d[m.group(1)] = (cls(l), l)
    return d
a, b = load(sys.argv[1]), load(sys.argv[2])
allrows = "-a" in sys.argv
for k in sorted(set(a) | set(b)):
    ca = a.get(k, ("-", ""))[0]; cb = b.get(k, ("-", ""))[0]
    if allrows or ca != cb:
        print(f"{k:40s} {ca:22s} {cb:22s}")
