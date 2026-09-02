#!/usr/bin/env python3
"""Price the `_Unparser` vararg build: how many CONVERTED methods pass an int-erased
value to `write` once `*text` is `str`-annotated?  Re-trusts each offender IN THE
WORKTREE ONLY (never landed) purely to reach the next error.  Foreground only."""
import os, re, subprocess, sys
ROOT="/home/fabrice/git/pycsl/scratchpad/w3/wt"
MIR="src/self-annotate/src/frontend/pure_ast.py"
MLW=MIR[:-3]+".mlw"
env=dict(os.environ, PATH="/home/fabrice/.opam/framac-coq8/bin:"+os.environ["PATH"], PYTHONHASHSEED="0")
def emit():
    r=subprocess.run(["python3","src/pycsl/pycsl.py",MIR,"--import-path","src/pycsl",
                      "--no-proof","--keep-mlw"],cwd=ROOT,env=env,capture_output=True,text=True)
    return r.stdout+r.stderr
def method_at(line):
    txt=open(os.path.join(ROOT,MLW)).read().split("\n")
    for i in range(min(line,len(txt))-1,-1,-1):
        m=re.match(r"  (?:let rec |let |val |with )([A-Za-z_0-9]+) ",txt[i])
        if m: return m.group(1)
    return None
def retrust(sym):
    short=sym.split("__",1)[1] if "__" in sym else sym
    p=os.path.join(ROOT,MIR); lines=open(p).read().split("\n")
    for i,l in enumerate(lines):
        if re.match(r"    def %s\(" % re.escape(short), l):
            j=i-1
            while j>=0 and (lines[j].lstrip().startswith("#") or lines[j].strip()==""):
                if lines[j].strip().startswith("#@ requires"):
                    lines.insert(j,"    #@ \\trusted reviewer: pycsl-self-annotate")
                    open(p,"w").write("\n".join(lines)); return True
                j-=1
            return False
    return False
hit=[]
for it in range(60):
    out=emit()
    if "L3-tc ✓" in out:
        print("L3-tc GREEN after re-trusting", len(hit)); print(hit); sys.exit(0)
    m=re.search(r'line (\d+), characters',out)
    if not m:
        print("no line in error:"); print(out[-1200:]); sys.exit(1)
    sym=method_at(int(m.group(1)))
    if sym in hit: print("STUCK on",sym); print(out[-900:]); sys.exit(2)
    hit.append(sym)
    if not retrust(sym): print("cannot re-trust",sym); sys.exit(3)
    print("it%-3d re-trusted %s" % (it,sym), flush=True)
print("CAP", hit)
