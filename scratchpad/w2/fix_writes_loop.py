import re, subprocess, sys, os
REPO='/home/fabrice/git/pycsl'
MIR='src/self-annotate/src/frontend/Module5_IREmitter.py'
MLW='src/self-annotate/src/frontend/Module5_IREmitter.mlw'
env=dict(os.environ); env['PATH']='/home/fabrice/.opam/framac-coq8/bin:'+env['PATH']; env['PYTHONHASHSEED']='0'
for it in range(80):
    r=subprocess.run([sys.executable,'src/pycsl/pycsl.py',MIR,'--import-path','src/pycsl','--no-proof','--keep-mlw'],
                     cwd=REPO,capture_output=True,text=True,env=env,timeout=1800)
    out=r.stdout+r.stderr
    if 'L3-tc ✓' in out:
        print('ITER',it,'L3-tc OK'); break
    m=re.search(r'File "([^"]*Module5_IREmitter\.mlw)", line (\d+),.*\n(.*)',out)
    if not m: print('ITER',it,'unparsed error:'); print(out[-800:]); break
    ln=int(m.group(2)); msg=m.group(3).strip()
    if 'this write effect does not happen' not in msg:
        print('ITER',it,'other error at line',ln,':',msg); print(out[-600:]); break
    lines=open(os.path.join(REPO,MLW)).read().splitlines()
    pat=re.compile(r'^  (let rec|let|with)\s+(?:function\s+|rec\s+)?([A-Za-z0-9_\']+)')
    owner=None
    for i in range(ln-1,-1,-1):
        mm=pat.match(lines[i])
        if mm: owner=mm.group(2); break
    short=owner.replace('pycsltojsonemitter___','')
    print('ITER',it,'line',ln,'owner',short,flush=True)
    # revert that member's assigns in the mirror
    L=open(os.path.join(REPO,MIR)).read().splitlines(True)
    tgt='_'+short if not short.startswith('_') else short
    di=[k for k,l in enumerate(L) if re.match(r'\s*def '+re.escape(tgt)+r'\(', l)]
    if not di: print('  no def for',tgt); break
    k=di[0]-1; done=False
    while k>=0 and (L[k].lstrip().startswith('#') or L[k].lstrip().startswith('@')):
        if L[k].strip()=='#@ assigns self._fresh_var_counter':
            ind=re.match(r'\s*',L[k]).group(0)
            L[k]=ind+'#@ assigns \\nothing\n'; done=True; break
        k-=1
    if not done: print('  could not revert',tgt); break
    open(os.path.join(REPO,MIR),'w').writelines(L)
