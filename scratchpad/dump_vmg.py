import sys, json
sys.path.insert(0, "src/pycsl")
from Module1_Ingestor import Ingestor
from Module2_Parser import Parser
src = open("src/self-annotate/src/Module6_WhyMLTranspiler.py").read()
# Use whatever the pipeline uses to get functions list; try the parser
try:
    ing = Ingestor()
    mod = ing.ingest_source(src, "Module6_WhyMLTranspiler.py")
    print("ingest ok", type(mod))
except Exception as e:
    print("ing err", e)
