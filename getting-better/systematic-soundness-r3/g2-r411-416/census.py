# Routes #412-#416 census (g2, run #3): re-measure the REFUSAL/VERIFY-FAIL rows of the expected-FAIL witnesses
# listed in argv[1] (one basename per line: GONE/MOVED witnesses of the sweep + view-loop + `%` rows),
# append the new r412-r416 FAIL witnesses -- every row via _census_row.
import sys, os, glob, re, importlib.util
ROOT = '/home/fabrice/git/pycsl-g2'
spec = importlib.util.spec_from_file_location('rwc', ROOT + '/bin/check-refusal-witness-coverage.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
py = ROOT + '/.venv/bin/python3'
T = ROOT + '/bin/refusal-witness-census.tsv'
lines = open(T).read().splitlines(True)
idx = {l.split('\t')[0]: i for i, l in enumerate(lines) if '\t' in l and not l.startswith('#')}
paths = {os.path.basename(f): f for f in glob.glob(ROOT + '/test-suite/corpus/**/*.py', recursive=True)}
redo = [w.strip() for w in open(sys.argv[1]) if w.strip() in idx]
new = [os.path.basename(f) for f in sorted(glob.glob(ROOT + '/test-suite/corpus/pycsl-reference/60[5-9]?_gen37_r41[1-6]_*.py'))
       if 'pycsl-expected: FAIL' in open(f).read()]
def norm(l):
    return re.sub(r'/home/[^ :]*/', '<P>/', l)
ch = []
for w in redo:
    r = m._census_row(py, paths[w])
    if norm(lines[idx[w]]) == norm(r):
        continue
    ch.append((w, lines[idx[w]].split('\t')[1], r.split('\t')[1], r.split('\t')[2][:90].strip()))
    lines[idx[w]] = r
for w in new:
    assert w not in idx, w
    lines.append(m._census_row(py, paths[w]))
open(T, 'w').writelines(lines)
print('remeasured', len(redo), 'changed', len(ch), 'new', len(new))
for c in ch:
    print('CHANGED', *c)
for w in new:
    print('NEW', [l for l in lines if l.startswith(w)][0].rstrip()[:160])
