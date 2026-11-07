import re,os,sys
def live_body(path, name):
    lines=open(path).read().split("\n")
    for i,l in enumerate(lines):
        m=re.match(r"(\s*)def "+re.escape(name)+r"\s*\(", l)
        if m:
            indent=len(m.group(1))
            body=[(i+1,l)]
            for j in range(i+1,len(lines)):
                lj=lines[j]
                if lj.strip()=="":
                    body.append((j+1,lj)); continue
                cur=len(lj)-len(lj.lstrip())
                if cur<=indent and re.match(r"\s*(def |@|class )",lj):
                    break
                body.append((j+1,lj))
            return body
    return None
path,name=sys.argv[1],sys.argv[2]
b=live_body(path,name)
if b is None: print("NOT FOUND"); sys.exit()
for ln,l in b:
    print(f"{ln}\t{l}")
