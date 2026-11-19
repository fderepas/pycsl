# census417.py <tree> : append census rows for the route #417 expected-FAIL witnesses, via the tool's
# _census_row on ABSOLUTE paths. Run AS a heavy.sh command.
import sys, os, glob, importlib.util
from concurrent.futures import ThreadPoolExecutor
T = sys.argv[1]
spec = importlib.util.spec_from_file_location('rwc', T + '/bin/check-refusal-witness-coverage.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
py = T + '/.venv/bin/python3'
C = T + '/bin/refusal-witness-census.tsv'
have = {l.split('\t')[0] for l in open(C) if '\t' in l}
new = [f for f in sorted(glob.glob(T + '/test-suite/corpus/pycsl-reference/61[01]?_r417_*.py'))
       if 'pycsl-expected: FAIL' in open(f).read() and os.path.basename(f) not in have]
with ThreadPoolExecutor(4) as ex:
    rows = list(ex.map(lambda f: m._census_row(py, os.path.abspath(f)), new))
with open(C, 'a') as out:
    out.writelines(rows)
for r in rows:
    print(r.rstrip()[:170])
print('appended', len(rows))
