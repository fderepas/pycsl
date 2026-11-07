# Census rows for NAMED witnesses only (never the whole-corpus --append-new, which also measures
# other executors' row-less witnesses). For each basename: replace its row if present, else append.
# Rows are produced by the tool's own _census_row; a worktree path prefix is rewritten to the
# coordinator's (/home/fabrice/git/pycsl/). Run AS: heavy.sh python3 census_rows.py <ROOT> <basename.py>...
import sys, importlib.util
ROOT = sys.argv[1]
spec = importlib.util.spec_from_file_location('rwc', ROOT + '/bin/check-refusal-witness-coverage.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
py = ROOT + '/.venv/bin/python3'
T = ROOT + '/bin/refusal-witness-census.tsv'
lines = open(T).read().splitlines(True)
for b in sys.argv[2:]:
    row = m._census_row(py, ROOT + '/test-suite/corpus/pycsl-reference/' + b)
    row = row.replace(ROOT.rstrip('/') + '/', '/home/fabrice/git/pycsl/')
    idx = [i for i, l in enumerate(lines) if l.split('\t')[0] == b]
    assert len(idx) <= 1, (b, idx)
    if idx:
        print('OLD', lines[idx[0]].rstrip('\n')[:160]); lines[idx[0]] = row
    else:
        lines.append(row)
    print('NEW', row.rstrip('\n')[:160], flush=True)
    open(T, 'w').writelines(lines)
