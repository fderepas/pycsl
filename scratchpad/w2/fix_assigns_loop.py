import re, subprocess, sys, os
REPO='/home/fabrice/git/pycsl'
REL=sys.argv[1]                      # e.g. module6_whyml/expressions.py
FIELDS=sys.argv[2].split(',')        # e.g. _current_params,_current_self_type,...
MIR='src/self-annotate/src/'+REL
MLW=MIR[:-3]+'.mlw'
env=dict(os.environ); env['PATH']='/home/fabrice/.opam/framac-coq8/bin:'+env['PATH']; env['PYTHONHASHSEED']='0'
touched=[]
for it in range(60):
    r=subprocess.run([sys.executable,'src/pycsl/pycsl.py',MIR,'--import-path','src/pycsl','--no-proof','--keep-mlw'],
                     cwd=REPO,capture_output=True,text=True,env=env,timeout=1800)
    out=r.stdout+r.stderr
    if 'L3-tc ✓' in out:
        print('ITER',it,'L3-tc OK; touched:',touched); break
    m=re.search(r'File "[^"]*\.mlw", line (\d+),[^\n]*\n(.*)',out)
    if not m: print('ITER',it,'unparsed:'); print(out[-700:]); break
    ln=int(m.group(1)); msg=m.group(2).strip()
    if 'unlisted write effect' not in msg:
        print('ITER',it,'other error line',ln,':',msg); break
    lines=open(os.path.join(REPO,MLW)).read().splitlines()
    pat=re.compile(r'^  (let rec|let|with)\s+(?:function\s+|rec\s+)?([A-Za-z0-9_\']+)')
    owner=None
    for i in range(ln-1,-1,-1):
        mm=pat.match(lines[i])
        if mm: owner=mm.group(2); break
    short=re.sub(r'^[a-z0-9]+___','_',owner) if '___' in owner else owner
    print('ITER',it,'line',ln,'owner',owner,'->',short,flush=True)
    L=open(os.path.join(REPO,MIR)).read().splitlines(True)
    di=[k for k,l in enumerate(L) if re.match(r'\s*def '+re.escape(short)+r'\(', l)]
    if not di: print('  no def for',short); break
    k=di[0]-1; done=False
    while k>=0 and (L[k].lstrip().startswith('#') or L[k].lstrip().startswith('@')):
        s=L[k].strip()
        if s.startswith('#@ assigns'):
            ind=re.match(r'\s*',L[k]).group(0)
            cur=set()
            if s!='#@ assigns \\nothing':
                cur={t.strip() for t in s[len('#@ assigns'):].split(',') if t.strip()}
            cur |= {'self.'+f for f in FIELDS}
            L[k]=ind+'#@ assigns '+', '.join(sorted(cur))+'\n'; done=True; break
        k-=1
    if not done: print('  no assigns line for',short); break
    open(os.path.join(REPO,MIR),'w').writelines(L)
    touched.append(short)
else:
    print('DID NOT CONVERGE; touched:',touched)
