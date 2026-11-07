# Census rows for executor h442's new expected-FAIL witnesses (IDs 6750-6799) via the tool's own
# _census_row, plus an in-place RE-MEASURE of named existing rows whose refusal now fires earlier
# (route #443 preempts their base message). Paths in messages are written with the
# /home/fabrice/git/pycsl/ prefix. `--append-new` is not used (it would also run the older
# row-less witnesses). Run AS a heavy.sh command:
#   heavy.sh python3 census.py <ROOT> [remeasure-basename.py ...]
import sys, os, glob, importlib.util
from concurrent.futures import ThreadPoolExecutor
ROOT = sys.argv[1].rstrip('/')
spec = importlib.util.spec_from_file_location('rwc', ROOT + '/bin/check-refusal-witness-coverage.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
py = ROOT + '/.venv/bin/python3'
T = ROOT + '/bin/refusal-witness-census.tsv'
C = ROOT + '/test-suite/corpus/pycsl-reference/'
fix = lambda r: r.replace(ROOT + '/', '/home/fabrice/git/pycsl/')
lines = open(T).read().splitlines(True)
have = {l.split('\t')[0] for l in lines if '\t' in l and not l.startswith('#')}
new = [f for f in sorted(glob.glob(C + '67[5-9][0-9]_*.py'))
       if 'pycsl-expected: FAIL' in open(f).read() and os.path.basename(f) not in have]
rem = sys.argv[2:]
with ThreadPoolExecutor(3) as ex:
    rows = [fix(r) for r in ex.map(lambda f: m._census_row(py, f), new)]
    rrows = [fix(r) for r in ex.map(lambda b: m._census_row(py, C + b), rem)]
for b, row in zip(rem, rrows):
    idx = [i for i, l in enumerate(lines) if l.split('\t')[0] == b]
    assert len(idx) == 1, (b, idx)
    print('OLD', lines[idx[0]].rstrip('\n')[:170]); print('NEW', row.rstrip('\n')[:170])
    lines[idx[0]] = row
if lines and not lines[-1].endswith('\n'):
    lines[-1] += '\n'
lines += rows
open(T, 'w').writelines(lines)
print('new', len(rows))
for r in rows:
    print('NEW', r.split('\t')[0], r.split('\t')[1], r.rstrip('\n').split('\t')[-1][:110])
