"""Print `_census_row` rows (the check's own writer, run for real) for the given witnesses."""
import importlib.util, sys, os
spec = importlib.util.spec_from_file_location("crwc", os.path.join(os.getcwd(), "bin", "check-refusal-witness-coverage.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for f in sys.argv[1:]:
    sys.stdout.write(m._census_row(os.path.join(os.getcwd(), ".venv", "bin", "python3"), f))
