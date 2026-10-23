import os, re, ast
root = "src/self-annotate/src"
stubs = []  # (file, funcname)
for dp,_,fs in os.walk(root):
    for f in fs:
        if not f.endswith(".py"): continue
        p = os.path.join(dp,f)
        lines = open(p).read().split("\n")
        for i,l in enumerate(lines):
            if re.search(r'#@ \\trusted', l):
                # find next def within a few lines
                for j in range(i+1, min(i+8, len(lines))):
                    m = re.match(r'\s*def (\w+)\(', lines[j])
                    if m:
                        stubs.append((p, m.group(1), j+1))
                        break
print("FUNCTION-LEVEL TRUSTED STUBS:", len(stubs))
from collections import defaultdict
byfile = defaultdict(list)
for p,n,ln in stubs: byfile[p].append(n)
for p in sorted(byfile): print(f"{len(byfile[p]):3} {p}")
open("scratchpad/stublist.txt","w").write("\n".join(f"{p}\t{n}\t{ln}" for p,n,ln in stubs))
