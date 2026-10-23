import sys, json
sys.path.insert(0, "src/pycsl")
sys.argv = ["pycsl.py", "src/self-annotate/src/module6_whyml/preamble.py", "--import-path", "src/pycsl", "--dump-ir"]
# Instead, ingest directly via Module1..Module5
from Module1_Ingestor import Ingestor
from Module2_Parser import Parser
from Module3_Weaver import Weaver
from Module4_SemanticAnalyzer import SemanticAnalyzer
from Module5_IREmitter import IREmitter
