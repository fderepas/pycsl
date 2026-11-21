import re, os

MIRROR="src/self-annotate/src"
LIVE="src/pycsl"
files=[]
import subprocess
out=subprocess.check_output(["grep","-rlE",r"\\trusted","%s/module6_whyml"%MIRROR,"%s/frontend"%MIRROR]).decode()
files=out.split()

# find trusted method names per mirror file
def trusted_methods(path):
    lines=open(path).read().split("\n")
    res=[]
    for i,l in enumerate(lines):
        if re.search(r"#@ \\trusted", l):
            # find next def
            for j in range(i,min(i+12,len(lines))):
                m=re.match(r"\s*def (\w+)\s*\(", lines[j])
                if m:
                    res.append((m.group(1), j+1))
                    break
    return res

# for a live file, extract body of a method by name -> text between def and next def at same indent
def live_body(path, name):
    if not os.path.exists(path): return None
    lines=open(path).read().split("\n")
    for i,l in enumerate(lines):
        m=re.match(r"(\s*)def "+re.escape(name)+r"\s*\(", l)
        if m:
            indent=len(m.group(1))
            body=[l]
            for j in range(i+1,len(lines)):
                lj=lines[j]
                if lj.strip()=="" :
                    body.append(lj); continue
                cur=len(lj)-len(lj.lstrip())
                if cur<=indent and lj.strip() and not lj.lstrip().startswith("#") and not lj.lstrip().startswith(("@","\"","'")):
                    # new def/method or class-level
                    if re.match(r"\s*(def |@|class )",lj) or cur<=indent:
                        break
                body.append(lj)
            return "\n".join(body)
    return None

pat_str_for=re.compile(r'for \w+ in \(\s*"')
pat_list_for=re.compile(r'for \w+ in \[\s*"')

for f in sorted(files):
    rel=f[len(MIRROR)+1:]
    livef=os.path.join(LIVE,rel)
    tms=trusted_methods(f)
    for name,ln in tms:
        lb=live_body(livef,name)
        if lb is None:
            print("NOLIVE",rel,name); continue
        if pat_str_for.search(lb) or pat_list_for.search(lb):
            print("HIT",rel,name)
