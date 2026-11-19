# Census rows for executor h430's new expected-FAIL witnesses (IDs 6450-6499) via the tool's own
# _census_row (absolute-path form, as g3's census.py). Run AS a heavy.sh command:
#   heavy.sh python3 census.py <ROOT>
import sys, os, glob, importlib.util
from concurrent.futures import ThreadPoolExecutor
ROOT = sys.argv[1]
spec = importlib.util.spec_from_file_location('rwc', ROOT + '/bin/check-refusal-witness-coverage.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
py = ROOT + '/.venv/bin/python3'
T = ROOT + '/bin/refusal-witness-census.tsv'
lines = open(T).read().splitlines(True)
have = {l.split('\t')[0] for l in lines if '\t' in l and not l.startswith('#')}
new = [f for f in sorted(glob.glob(ROOT + '/test-suite/corpus/pycsl-reference/64[5-9][0-9]_*.py'))
       if 'pycsl-expected: FAIL' in open(f).read() and os.path.basename(f) not in have]
with ThreadPoolExecutor(4) as ex:
    rows = list(ex.map(lambda f: m._census_row(py, f), new))
if lines and not lines[-1].endswith('\n'):
    lines[-1] += '\n'
lines += rows
open(T, 'w').writelines(lines)
print('new', len(rows))
for r in rows:
    print('NEW', r.split('\t')[0], r.split('\t')[1], r.rstrip('\n').split('\t')[-1][:110])
