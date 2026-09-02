import sys, json
sys.path.insert(0, "src/pycsl")
from Module1_Ingestor import Ingestor
from Module2_Parser import Parser
from Module3_Weaver import Weaver
from Module4_SemanticAnalyzer import SemanticAnalyzer
from Module5_IREmitter import IREmitter
src_path = "src/self-annotate/src/module6_whyml/preamble.py"
# Try to reuse the pipeline the CLI uses. Fall back: import pycsl driver.
import importlib
