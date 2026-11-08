# Routes #403-#410 census: re-measure the REFUSAL rows whose --no-proof refusal message moved between base
# and candidate (refmsg-base.tsv vs refmsg-cand.tsv), append the new r403-r410 FAIL witnesses (all via _census_row).
import sys, os, glob, re, importlib.util
ROOT = '/home/fabrice/git/pycsl-g1'
spec = importlib.util.spec_from_file_location('rwc', ROOT + '/bin/check-refusal-witness-coverage.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
py = ROOT + '/.venv/bin/python3'
T = ROOT + '/bin/refusal-witness-census.tsv'
lines = open(T).read().splitlines(True)
idx = {l.split('\t')[0]: i for i, l in enumerate(lines) if '\t' in l and not l.startswith('#')}
paths = {os.path.basename(f): f for f in glob.glob(ROOT + '/test-suite/corpus/**/*.py', recursive=True)}
redo = [w.strip() for w in open(sys.argv[1]) if w.strip()]
new = [os.path.basename(f) for f in sorted(glob.glob(ROOT + '/test-suite/corpus/pycsl-reference/[56][90]??_gen37_r4[01][0-9]_*.py'))
       if 'pycsl-expected: FAIL' in open(f).read() and os.path.basename(f) not in idx]
ch = []
def norm(l):
    return re.sub(r'/home/[^ :]*/', '<P>/', l)
for w in redo:
    r = m._census_row(py, paths[w])
    if norm(lines[idx[w]]) == norm(r):
        continue
    ch.append((w, lines[idx[w]].split('\t')[1], r.split('\t')[1]))
    lines[idx[w]] = r
for w in new:
    lines.append(m._census_row(py, paths[w]))
open(T, 'w').writelines(lines)
print('remeasured', len(redo), 'changed', len(ch), 'new', len(new))
for c in ch:
    print('CHANGED', *c)
for w in new:
    print('NEW', lines[-len(new) + new.index(w)].split('\t')[1], w)
