import sys
sys.path.insert(0, 'src/pycsl')
from module1_ingestor import Ingestor
from Module2_Parser import Parser
from Module3_Weaver import Weaver
import importlib
# Use the pipeline to get IR functions. Simpler: call the analyzer up to Module5.
