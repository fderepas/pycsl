# refscreen.py <tree> <out.tsv> <budget_s> : re-measure every REFUSAL row of <tree>/bin/refusal-witness-census.tsv
# with the tool's own _census_row (absolute paths), 6-parallel, resumable (skips rows already in out.tsv).
# Run AS a heavy.sh command.
import sys, os, glob, time, importlib.util
from concurrent.futures import ThreadPoolExecutor
T, O, B = sys.argv[1], sys.argv[2], float(sys.argv[3])
DL = time.time() + B
spec = importlib.util.spec_from_file_location('rwc', T + '/bin/check-refusal-witness-coverage.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
py = T + '/.venv/bin/python3'
rows = [l.split('\t') for l in open(T + '/bin/refusal-witness-census.tsv').read().splitlines()
        if '\t' in l and not l.startswith('#')]
ref = [r[0] for r in rows if r[1] == 'REFUSAL']
paths = {}
for f in glob.glob(T + '/test-suite/corpus/**/*.py', recursive=True):
    paths.setdefault(os.path.basename(f), f)
done = set()
if os.path.exists(O):
    done = {l.split('\t')[0] for l in open(O) if '\t' in l}
todo = [w for w in ref if w not in done and w in paths]
missing = [w for w in ref if w not in paths]
def one(w):
    if time.time() > DL:
        return None
    return m._census_row(py, paths[w])
with ThreadPoolExecutor(6) as ex, open(O, 'a') as out:
    for r in ex.map(one, todo):
        if r is not None:
            out.write(r); out.flush()
n = len({l.split('\t')[0] for l in open(O) if '\t' in l})
print('refusal rows', len(ref), 'measured', n, 'remaining', len(ref) - n - len(missing), 'missing-source', len(missing))
