# Re-measure the census rows of named existing witnesses (a refusal that now fires earlier) via the
# tool's own _census_row, replacing each row in place. Run AS a heavy.sh command:
#   heavy.sh python3 remeasure.py <ROOT> <basename.py>...
import sys, importlib.util
ROOT = sys.argv[1]
spec = importlib.util.spec_from_file_location('rwc', ROOT + '/bin/check-refusal-witness-coverage.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
py = ROOT + '/.venv/bin/python3'
T = ROOT + '/bin/refusal-witness-census.tsv'
lines = open(T).read().splitlines(True)
for b in sys.argv[2:]:
    row = m._census_row(py, ROOT + '/test-suite/corpus/pycsl-reference/' + b)
    idx = [i for i, l in enumerate(lines) if l.split('\t')[0] == b]
    assert len(idx) == 1, (b, idx)
    print('OLD', lines[idx[0]].rstrip('\n')[:160]); print('NEW', row.rstrip('\n')[:160])
    lines[idx[0]] = row
open(T, 'w').writelines(lines)
