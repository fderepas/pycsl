import os, re, sys, json
MIRROR = "src/self-annotate/src"
tot_loops=0; ann=0; missing=[]
for root,_,files in os.walk(MIRROR):
    for fn in files:
        if not fn.endswith('.py'): continue
        p=os.path.join(root,fn)
        lines=open(p,errors='replace').read().split('\n')
        for i,l in enumerate(lines):
            s=l.strip()
            if not (s.startswith('while ') or s.startswith('for ')): continue
            if s.startswith('for ') and ' in ' not in s: continue
            tot_loops+=1
            # look back over contiguous #@ / comment lines
            j=i-1; has=False
            while j>=0:
                t=lines[j].strip()
                if t.startswith('#@'):
                    if 'loop variant' in t or 'loop invariant' in t: has=True
                    j-=1; continue
                if t.startswith('#') or t=='':
                    j-=1; continue
                break
            if has: ann+=1
            else: missing.append(f"{p}:{i+1}: {s[:70]}")
print("loops:",tot_loops," annotated:",ann," missing:",len(missing))
for m in missing[:20]: print("  ",m)
