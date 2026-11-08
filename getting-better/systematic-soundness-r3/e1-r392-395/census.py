import sys, os, glob, importlib.util
ROOT='/home/fabrice/git/pycsl-e1'
spec=importlib.util.spec_from_file_location('rwc', ROOT+'/bin/check-refusal-witness-coverage.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
py=ROOT+'/.venv/bin/python3'
T=ROOT+'/bin/refusal-witness-census.tsv'
lines=open(T).read().splitlines(True)
idx={l.split('\t')[0]:i for i,l in enumerate(lines) if '\t' in l and not l.startswith('#')}
paths={os.path.basename(f):f for f in glob.glob(ROOT+'/test-suite/corpus/**/*.py', recursive=True)}
redo=[l.split('\t')[0] for l in lines if 'is HASHED by' in l]
new=[os.path.basename(f) for f in sorted(glob.glob(ROOT+'/test-suite/corpus/pycsl-reference/55[5-8]*_gen37_r39*.py')) if 'pycsl-expected: FAIL' in open(f).read()]
ch=0
for w in redo:
    r=m._census_row(py, paths[w])
    if lines[idx[w]]!=r: ch+=1
    lines[idx[w]]=r
for w in new:
    assert w not in idx
    lines.append(m._census_row(py, paths[w]))
open(T,'w').writelines(lines)
print('remeasured',len(redo),'changed',ch,'new',len(new))
