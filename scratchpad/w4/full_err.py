import sys, os, re, subprocess
sys.path.insert(0, os.path.join(os.getcwd(), "bin"))
import importlib.util
spec = importlib.util.spec_from_file_location("probe", "bin/probe-conversion-candidates.py")
m = importlib.util.module_from_spec(spec)
# we only want its porting helper; simpler: replicate by calling the tool with a debug env
