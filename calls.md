# Library Calls in `src/`

All external library imports used by Python files under `src/`.

## Standard Library

### `argparse`

- `import argparse`
  - lean2pycsl/cli.py
  - pycsl/agents/agent-annotate.py
  - pycsl/agents/agent-infer-invariants.py
  - pycsl/agents/agent-meta-evaluator.py
  - pycsl/agents/agent-meta-monitor.py
  - pycsl/agents/agent-meta-reviewer.py
  - pycsl/agents/agent-reconcile.py
  - pycsl/agents/agent-rocq-proof-writer.py
  - pycsl/agents/agent-script-update.py
  - pycsl/agents/agent-splitter.py
  - pycsl/agents/agent-writer.py
  - pycsl/agents/coordinator.py
  - pycsl/pycsl.py
  - pycsl_bridge/cli.py
  - rocq2pycsl/cli.py
  - self-annotate/src/pycsl.py
  - skill2rag/cli.py

### `ast`

- `import ast`
  - pycsl/ConcurrencyChecker.py
  - pycsl/Module3_Weaver.py
  - pycsl/Module4_SemanticAnalyzer.py
  - pycsl/Module5_IREmitter.py
  - pycsl/agents/agent-splitter.py
  - self-annotate/src/ConcurrencyChecker.py
  - self-annotate/src/Module3_Weaver.py
  - self-annotate/src/Module4_SemanticAnalyzer.py
  - self-annotate/src/Module5_IREmitter.py
- `import ast as _ast`
  - pycsl/pycsl.py
  - self-annotate/src/pycsl.py
- `import ast as _ast_module`
  - pycsl/agents/agent-annotate.py

### `collections`

- `from collections import Counter`
  - pycsl_bridge/reconciler/pipeline.py
- `from collections import defaultdict`
  - pycsl/pycsl.py
  - self-annotate/src/pycsl.py

### `dataclasses`

- `from dataclasses import asdict`
  - skill2rag/indexer.py
- `from dataclasses import dataclass`
  - lean2pycsl/extractor/lex.py
  - lean2pycsl/extractor/selector.py
  - pycsl/Module2_Parser.py
  - pycsl/Module3_Weaver.py
  - pycsl_bridge/canonicalizer/normalize.py
  - pycsl_bridge/linker/manifest.py
  - pycsl_emit/emitter/locator.py
  - pycsl_emit/translator/render.py
  - rocq2pycsl/extractor/lex.py
  - rocq2pycsl/extractor/selector.py
  - self-annotate/src/Module2_Parser.py
  - self-annotate/src/Module3_Weaver.py
- `from dataclasses import dataclass, field`
  - lean2pycsl/cli.py
  - lean2pycsl/extractor/lean_ast.py
  - lean2pycsl/translator/lean.py
  - pycsl/ConcurrencyChecker.py
  - pycsl/Module1_Ingestor.py
  - pycsl/agents/agent-splitter.py
  - pycsl/audit_proof.py
  - pycsl_bridge/cli.py
  - pycsl_bridge/reconciler/pipeline.py
  - pycsl_emit/checker/verdict.py
  - pycsl_emit/config/schema.py
  - pycsl_emit/ir/nodes.py
  - pycsl_emit/translator/names.py
  - rocq2pycsl/cli.py
  - rocq2pycsl/extractor/gallina.py
  - rocq2pycsl/translator/gallina.py
  - self-annotate/src/ConcurrencyChecker.py
  - self-annotate/src/Module1_Ingestor.py
  - skill2rag/chunker.py

### `datetime`

- `from datetime import datetime`
  - pycsl/agents/agent-meta-monitor.py
- `import datetime`
  - pycsl/agents/common.py
  - pycsl/agents/llm_client.py
  - skill2rag/tools/llm_client.py

### `enum`

- `import enum`
  - lean2pycsl/extractor/api.py
  - lean2pycsl/extractor/lean_ast.py
  - pycsl_bridge/reconciler/pipeline.py
  - pycsl_emit/checker/verdict.py
  - pycsl_emit/translator/divides.py
  - rocq2pycsl/extractor/api.py

### `hashlib`

- `import hashlib`
  - pycsl/pycsl.py
  - self-annotate/src/pycsl.py
  - skill2rag/chunker.py

### `importlib`

- `from importlib import util as _importlib_util`
  - pycsl/agents/agent-annotate.py
  - pycsl/agents/agent-infer-invariants.py
  - pycsl/agents/agent-writer.py

### `json`

- `import json`
  - pycsl/Module5_IREmitter.py
  - pycsl/Module6_WhyMLTranspiler.py
  - pycsl/agents/agent-annotate.py
  - pycsl/agents/agent-infer-invariants.py
  - pycsl/agents/agent-meta-evaluator.py
  - pycsl/agents/agent-meta-monitor.py
  - pycsl/agents/agent-meta-reviewer.py
  - pycsl/agents/agent-reconcile.py
  - pycsl/agents/agent-rocq-proof-writer.py
  - pycsl/agents/agent-script-update-mcp.py
  - pycsl/agents/agent-script-update.py
  - pycsl/agents/agent-splitter.py
  - pycsl/agents/agent-writer.py
  - pycsl/agents/common.py
  - pycsl/agents/coordinator.py
  - pycsl/agents/llm_client.py
  - pycsl/agents/schema_validator.py
  - pycsl_emit/ir/json_io.py
  - self-annotate/src/Module5_IREmitter.py
  - self-annotate/src/Module6_WhyMLTranspiler.py
  - skill2rag/embedder.py
  - skill2rag/indexer.py
  - skill2rag/retriever.py
  - skill2rag/tools/llm_client.py
- `import json as _json`
  - lean2pycsl/cli.py
  - pycsl/pycsl.py
  - rocq2pycsl/cli.py
  - self-annotate/src/pycsl.py

### `os`

- `import os`
  - pycsl/agents/agent-rocq-proof-writer.py
  - pycsl/agents/agent-splitter.py
  - pycsl/agents/llm_client.py
  - pycsl/pycsl.py
  - pycsl_emit/checker/pycsl_runner.py
  - pycsl_emit/config/load.py
  - self-annotate/src/pycsl.py
  - skill2rag/embedder.py
  - skill2rag/tools/llm_client.py

### `pathlib`

- `from pathlib import Path`
  - lean2pycsl/cli.py
  - lean2pycsl/extractor/api.py
  - lean2pycsl/extractor/lark_backend.py
  - lean2pycsl/tests/extractor/test_api.py
  - lean2pycsl/tests/test_end_to_end.py
  - pycsl/agents/agent-annotate.py
  - pycsl/agents/agent-infer-invariants.py
  - pycsl/agents/agent-invariant-writer.py
  - pycsl/agents/agent-meta-evaluator.py
  - pycsl/agents/agent-meta-monitor.py
  - pycsl/agents/agent-meta-reviewer.py
  - pycsl/agents/agent-reconcile.py
  - pycsl/agents/agent-rocq-proof-writer.py
  - pycsl/agents/agent-script-update-mcp.py
  - pycsl/agents/agent-script-update.py
  - pycsl/agents/agent-splitter.py
  - pycsl/agents/agent-writer.py
  - pycsl/agents/common.py
  - pycsl/agents/coordinator.py
  - pycsl/agents/llm_client.py
  - pycsl/agents/schema_validator.py
  - pycsl/audit_proof.py
  - pycsl/pycsl.py
  - pycsl_bridge/cli.py
  - pycsl_bridge/linker/manifest.py
  - pycsl_bridge/tests/test_end_to_end.py
  - pycsl_bridge/tests/test_manifest.py
  - pycsl_emit/checker/pycsl_runner.py
  - pycsl_emit/config/load.py
  - pycsl_emit/tests/checker/test_pycsl_runner.py
  - pycsl_emit/tests/test_config.py
  - pycsl_emit/tests/test_end_to_end.py
  - rocq2pycsl/cli.py
  - rocq2pycsl/extractor/api.py
  - rocq2pycsl/extractor/lark_backend.py
  - rocq2pycsl/tests/extractor/test_api.py
  - rocq2pycsl/tests/test_end_to_end.py
  - self-annotate/src/pycsl.py
  - skill2rag/chunker.py
  - skill2rag/indexer.py
  - skill2rag/retriever.py
  - skill2rag/tools/llm_client.py

### `re`

- `import re`
  - lean2pycsl/extractor/lark_backend.py
  - lean2pycsl/extractor/lex.py
  - pycsl/agents/agent-annotate.py
  - pycsl/agents/agent-contract-writer.py
  - pycsl/agents/agent-infer-invariants.py
  - pycsl/agents/agent-invariant-writer.py
  - pycsl/agents/agent-meta-monitor.py
  - pycsl/agents/agent-meta-reviewer.py
  - pycsl/agents/agent-reconcile.py
  - pycsl/agents/agent-rocq-proof-writer.py
  - pycsl/agents/agent-script-update.py
  - pycsl/agents/agent-splitter.py
  - pycsl/agents/agent-writer.py
  - pycsl/agents/common.py
  - pycsl/agents/coordinator.py
  - pycsl/agents/llm_client.py
  - pycsl_emit/checker/pycsl_runner.py
  - rocq2pycsl/extractor/lark_backend.py
  - rocq2pycsl/extractor/lex.py
  - rocq2pycsl/extractor/selector.py
  - skill2rag/chunker.py
  - skill2rag/tools/llm_client.py

### `shutil`

- `import shutil`
  - lean2pycsl/extractor/lean_script_backend.py
  - pycsl/agents/agent-splitter.py
  - pycsl/agents/coordinator.py
  - pycsl/pycsl.py
  - pycsl_bridge/tests/test_end_to_end.py
  - rocq2pycsl/extractor/serapi_backend.py
  - self-annotate/src/pycsl.py
- `import shutil as _sh`
  - pycsl/pycsl.py
  - self-annotate/src/pycsl.py

### `subprocess`

- `import subprocess`
  - pycsl/agents/agent-meta-evaluator.py
  - pycsl/agents/agent-rocq-proof-writer.py
  - pycsl/agents/agent-script-update.py
  - pycsl/agents/agent-splitter.py
  - pycsl/agents/coordinator.py
  - pycsl/agents/llm_client.py
  - pycsl/pycsl.py
  - pycsl_emit/checker/pycsl_runner.py
  - self-annotate/src/pycsl.py
  - skill2rag/tools/llm_client.py

### `sys`

- `import sys`
  - lean2pycsl/cli.py
  - pycsl/agents/agent-annotate.py
  - pycsl/agents/agent-infer-invariants.py
  - pycsl/agents/agent-invariant-writer.py
  - pycsl/agents/agent-meta-evaluator.py
  - pycsl/agents/agent-meta-monitor.py
  - pycsl/agents/agent-meta-reviewer.py
  - pycsl/agents/agent-reconcile.py
  - pycsl/agents/agent-rocq-proof-writer.py
  - pycsl/agents/agent-script-update.py
  - pycsl/agents/agent-splitter.py
  - pycsl/agents/agent-writer.py
  - pycsl/agents/common.py
  - pycsl/agents/coordinator.py
  - pycsl/agents/llm_client.py
  - pycsl/agents/schema_validator.py
  - pycsl/audit_proof.py
  - pycsl/pycsl.py
  - pycsl_bridge/cli.py
  - pycsl_emit/checker/pycsl_runner.py
  - rocq2pycsl/cli.py
  - self-annotate/src/pycsl.py
  - skill2rag/cli.py
  - skill2rag/embedder.py
  - skill2rag/indexer.py

### `tempfile`

- `import tempfile`
  - pycsl/agents/agent-rocq-proof-writer.py
  - pycsl/agents/agent-splitter.py
  - pycsl/pycsl.py
  - self-annotate/src/pycsl.py

### `textwrap`

- `import textwrap`
  - lean2pycsl/tests/extractor/test_lark_backend.py
  - lean2pycsl/tests/extractor/test_lex.py
  - pycsl/agents/agent-annotate.py
  - pycsl/agents/agent-splitter.py
  - pycsl_emit/tests/emitter/test_annotator.py
  - pycsl_emit/tests/ir/test_pretty.py
  - pycsl_emit/tests/test_config.py
  - rocq2pycsl/tests/extractor/test_lark_backend.py
  - rocq2pycsl/tests/extractor/test_selector.py

### `time`

- `import time`
  - pycsl/agents/agent-splitter.py

### `tomllib`

- `import tomllib`
  - pycsl_bridge/linker/manifest.py
  - pycsl_emit/config/load.py

### `typing`

- `from typing import Any`
  - pycsl/agents/agent-reconcile.py
  - pycsl/agents/agent-script-update-mcp.py
  - pycsl_bridge/reconciler/pipeline.py
  - pycsl_bridge/tests/reconciler/test_pipeline.py
  - pycsl_emit/ir/json_io.py
- `from typing import Any, Dict, List, Optional, Set`
  - pycsl/ConcurrencyChecker.py
  - self-annotate/src/ConcurrencyChecker.py
- `from typing import Any, Dict, List, Optional, Set, Tuple`
  - pycsl/Module5_IREmitter.py
  - pycsl/pycsl.py
  - self-annotate/src/Module5_IREmitter.py
  - self-annotate/src/pycsl.py
- `from typing import Any, Dict, List, Optional, TypedDict`
  - pycsl/ir_schema.py
  - self-annotate/src/ir_schema.py
- `from typing import Any, Iterable`
  - pycsl_emit/ir_dump.py
- `from typing import Any, Mapping`
  - pycsl_emit/config/load.py
  - pycsl_emit/config/schema.py
- `from typing import Any, Sequence`
  - pycsl_bridge/cli.py
- `from typing import Any, Union`
  - pycsl/agents/common.py
  - pycsl/agents/llm_client.py
  - skill2rag/tools/llm_client.py
- `from typing import Callable`
  - pycsl/agents/agent-annotate.py
- `from typing import Callable, Dict, List, Optional, Set, Any`
  - pycsl/Module4_SemanticAnalyzer.py
  - self-annotate/src/Module4_SemanticAnalyzer.py
- `from typing import Dict, Any, Optional, Set, List, Tuple`
  - pycsl/Module6_WhyMLTranspiler.py
  - self-annotate/src/Module6_WhyMLTranspiler.py
- `from typing import Iterable`
  - lean2pycsl/cli.py
  - lean2pycsl/extractor/selector.py
  - lean2pycsl/translator/lean.py
  - rocq2pycsl/cli.py
  - rocq2pycsl/extractor/selector.py
  - rocq2pycsl/translator/gallina.py
- `from typing import Iterable, Sequence`
  - pycsl_emit/emitter/annotator.py
- `from typing import Iterator`
  - pycsl_emit/translator/render.py
- `from typing import List`
  - skill2rag/chunker.py
  - skill2rag/embedder.py
  - skill2rag/indexer.py
  - skill2rag/retriever.py
- `from typing import List, Dict, Any, Tuple`
  - pycsl/Module3_Weaver.py
  - self-annotate/src/Module3_Weaver.py
- `from typing import List, Optional`
  - pycsl/Module1_Ingestor.py
  - self-annotate/src/Module1_Ingestor.py
- `from typing import List, Optional, Set`
  - pycsl/audit_proof.py
- `from typing import List, Union, Any, Optional`
  - pycsl/Module2_Parser.py
  - self-annotate/src/Module2_Parser.py
- `from typing import Mapping`
  - pycsl_emit/translator/names.py
- `from typing import Optional`
  - pycsl/agents/agent-meta-evaluator.py
  - pycsl/agents/agent-meta-monitor.py
  - pycsl/agents/agent-script-update.py
  - pycsl/agents/agent-splitter.py
  - pycsl/agents/coordinator.py
  - pycsl/agents/schema_validator.py
  - pycsl_emit/checker/verdict.py
  - pycsl_emit/emitter/locator.py
- `from typing import Sequence`
  - pycsl_emit/checker/pycsl_runner.py
- `from typing import Union`
  - lean2pycsl/extractor/lean_ast.py
  - pycsl_emit/ir/nodes.py
  - pycsl_emit/ir/pretty.py
  - rocq2pycsl/extractor/gallina.py

### `unicodedata`

- `import unicodedata`
  - pycsl/Module6_WhyMLTranspiler.py
  - self-annotate/src/Module6_WhyMLTranspiler.py

### `urllib`

- `import urllib.error`
  - skill2rag/embedder.py
- `import urllib.request`
  - pycsl/agents/llm_client.py
  - skill2rag/embedder.py
  - skill2rag/tools/llm_client.py

### `warnings`

- `import warnings`
  - pycsl/Module3_Weaver.py
  - self-annotate/src/Module3_Weaver.py

## Third-Party Libraries

### `jsonschema`

- `import jsonschema`
  - pycsl/agents/schema_validator.py

### `lark`

- `from lark import Lark, Token, Transformer, UnexpectedInput, v_args`
  - lean2pycsl/extractor/lark_backend.py
  - rocq2pycsl/extractor/lark_backend.py
- `from lark import Lark, Transformer, v_args`
  - pycsl/Module2_Parser.py
  - self-annotate/src/Module2_Parser.py
- `from lark.exceptions import LarkError`
  - pycsl/Module2_Parser.py
  - self-annotate/src/Module2_Parser.py

### `libcst`

- `from libcst.metadata import PositionProvider`
  - pycsl/Module1_Ingestor.py
  - self-annotate/src/Module1_Ingestor.py
- `import libcst as cst`
  - pycsl/Module1_Ingestor.py
  - pycsl_emit/emitter/annotator.py
  - pycsl_emit/emitter/locator.py
  - pycsl_emit/tests/emitter/test_annotator.py
  - self-annotate/src/Module1_Ingestor.py

### `mcp`

- `from mcp.server.fastmcp import FastMCP`
  - pycsl/agents/agent-script-update-mcp.py

### `numpy`

- `import numpy as np`
  - skill2rag/retriever.py

### `pytest`

- `import pytest`
  - lean2pycsl/tests/extractor/test_api.py
  - lean2pycsl/tests/extractor/test_selector.py
  - lean2pycsl/tests/test_end_to_end.py
  - lean2pycsl/tests/translator/test_lean.py
  - pycsl_bridge/tests/canonicalizer/test_normalize.py
  - pycsl_bridge/tests/reconciler/test_pipeline.py
  - pycsl_bridge/tests/test_end_to_end.py
  - pycsl_emit/tests/checker/test_pycsl_runner.py
  - pycsl_emit/tests/emitter/test_annotator.py
  - pycsl_emit/tests/ir/test_json_io.py
  - pycsl_emit/tests/test_config.py
  - pycsl_emit/tests/test_end_to_end.py
  - pycsl_emit/tests/translator/test_render.py
  - rocq2pycsl/tests/extractor/test_api.py
  - rocq2pycsl/tests/extractor/test_selector.py
  - rocq2pycsl/tests/test_end_to_end.py
  - rocq2pycsl/tests/translator/test_gallina.py

### `tomli_w`

- `import tomli_w`
  - pycsl_bridge/linker/manifest.py

## Summary

| Category | Library | Import Count | File Count |
|----------|---------|-------------|------------|
| stdlib | `argparse` | 1 | 17 |
| stdlib | `ast` | 3 | 12 |
| stdlib | `collections` | 2 | 3 |
| stdlib | `dataclasses` | 3 | 32 |
| stdlib | `datetime` | 2 | 4 |
| stdlib | `enum` | 1 | 6 |
| stdlib | `hashlib` | 1 | 3 |
| stdlib | `importlib` | 1 | 3 |
| stdlib | `json` | 2 | 28 |
| stdlib | `os` | 1 | 9 |
| stdlib | `pathlib` | 1 | 42 |
| stdlib | `re` | 1 | 22 |
| stdlib | `shutil` | 2 | 7 |
| stdlib | `subprocess` | 1 | 10 |
| stdlib | `sys` | 1 | 25 |
| stdlib | `tempfile` | 1 | 4 |
| stdlib | `textwrap` | 1 | 9 |
| stdlib | `time` | 1 | 1 |
| stdlib | `tomllib` | 1 | 2 |
| stdlib | `typing` | 23 | 58 |
| stdlib | `unicodedata` | 1 | 2 |
| stdlib | `urllib` | 2 | 3 |
| stdlib | `warnings` | 1 | 2 |
| third-party | `jsonschema` | 1 | 1 |
| third-party | `lark` | 3 | 4 |
| third-party | `libcst` | 2 | 5 |
| third-party | `mcp` | 1 | 1 |
| third-party | `numpy` | 1 | 1 |
| third-party | `pytest` | 1 | 17 |
| third-party | `tomli_w` | 1 | 1 |
