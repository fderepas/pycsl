# Route #402 census: re-measure every REFUSAL row whose message is a hash refusal or whose
# source binds `__hash__` / `__eq__`, append the new r402 FAIL witnesses (all via _census_row).
import sys, os, glob, re, importlib.util
ROOT = '/home/fabrice/git/pycsl-e3'
spec = importlib.util.spec_from_file_location('rwc', ROOT + '/bin/check-refusal-witness-coverage.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
py = ROOT + '/.venv/bin/python3'
T = ROOT + '/bin/refusal-witness-census.tsv'
lines = open(T).read().splitlines(True)
idx = {l.split('\t')[0]: i for i, l in enumerate(lines) if '\t' in l and not l.startswith('#')}
paths = {os.path.basename(f): f for f in glob.glob(ROOT + '/test-suite/corpus/**/*.py', recursive=True)}
redo = []
for l in lines:
    if '\t' not in l or l.startswith('#'):
        continue
    w, cls = l.split('\t')[:2]
    if w not in paths:
        continue
    src = open(paths[w], errors='replace').read()
    if ('is HASHED by' in l or 'puts an UNHASHABLE' in l
            or (cls == 'REFUSAL' and re.search(r'__(hash|eq)__', src))):
        redo.append(w)
new = [os.path.basename(f) for f in sorted(glob.glob(ROOT + '/test-suite/corpus/pycsl-reference/57[89]?_gen37_r402_*.py'))
       if 'pycsl-expected: FAIL' in open(f).read()]
ch = []
def norm(l):
    # a row that embeds the witness's absolute path keeps its recorded path: only a change
    # of class or of message text (modulo the path) is a re-measured change
    return re.sub(r'/home/[^ :]*/', '<P>/', l)
for w in redo:
    r = m._census_row(py, paths[w])
    if norm(lines[idx[w]]) == norm(r):
        continue
    if lines[idx[w]] != r:
        ch.append((w, lines[idx[w]].split('\t')[1], r.split('\t')[1]))
    lines[idx[w]] = r
for w in new:
    assert w not in idx, w
    lines.append(m._census_row(py, paths[w]))
open(T, 'w').writelines(lines)
print('remeasured', len(redo), 'changed', len(ch), 'new', len(new))
for c in ch:
    print('CHANGED', *c)
