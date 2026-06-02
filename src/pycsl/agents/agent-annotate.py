import argparse
import ast as _ast_module
import json
import re
import sys
from pathlib import Path
from typing import Callable
from llm_client import llm_generate, log
from common import retrieve_skill_chunks, extract_code_block


# Make this script's dir (…/agents) importable so the agent_annotate
# package and sibling modules resolve under direct execution and importlib.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_annotate.guards import *  # noqa: E402,F401,F403

# Fixed queries used to always retrieve critical skill sections regardless of input code.
_ESSENTIAL_QUERIES = [
    "Required on every function requires ensures assigns loop invariant loop variant",
    "Forbidden in contract expressions NEVER use operators quantifiers",
    "Class support method annotation rules class invariant Level 2 Level 3",
    "class invariant preserve maintain precondition method requires amount >= 0 NEVER requires 1 == 1",
]

class GuardPipeline:
    """Composable post-processing pipeline for LLM-generated Python code.

    Each guard is a str→str transform applied in sequence.  Centralising calls
    here gives a single place to add error handling, tracing, or rollback.
    """

    def __init__(self, code: str) -> None:
        self.code = code

    def apply(self, name: str, transform: Callable[[str], str]) -> None:
        self.code = transform(self.code)




# ---------------------------------------------------------------------------
# Guard functions (promoted from main() for module-level testability)
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Annotate Python programs with logical pre and post conditions.")
    parser.add_argument('--in', dest='in_file_name', required=True, help="Path to the input program to annotate.")
    parser.add_argument('--out', dest='out_file_name', required=True, help="Path to the generated annotated program.")
    args = parser.parse_args()

    script_dir = Path(__file__).parent.resolve()
    project_root = script_dir.parent.parent.parent  # src/pycsl/agents -> project root
    config_path = project_root / "config" / "agents-config.json"
    
    # Set a default project_directory for initial logging before the config is parsed
    project_directory = str(project_root)

    if not config_path.exists():
        log(project_directory, AGENT_NAME, f"Error: Configuration file not found at {config_path}")
        sys.exit(1)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        log(project_directory, AGENT_NAME, f"Error parsing {config_path}: {e}")
        sys.exit(1)

    project_directory = config.get("project-directory", project_directory)
    model = config.get("model")
    skill_annotator_name = config.get("skill-annotate")
    memory_model = config.get("memory-model", "hoare")
    rag_index_name = config.get("rag-index")
    rag_top_k = config.get("rag-top-k", 10)

    if not model:
        log(project_directory, AGENT_NAME, "Error: 'model' field is missing in agents-config.json")
        sys.exit(1)
    if not skill_annotator_name:
        log(project_directory, AGENT_NAME, "Error: 'skill-annotate' field is missing in agents-config.json")
        sys.exit(1)

    skill_annotator_path = Path(skill_annotator_name)
    if not skill_annotator_path.is_absolute():
        skill_annotator_path = project_root / skill_annotator_path

    if not skill_annotator_path.exists():
        log(project_directory, AGENT_NAME, f"Error: Skill annotator file not found at {skill_annotator_path}")
        sys.exit(1)

    log(project_directory, AGENT_NAME, f"Memory model: {memory_model}")

    in_file_path = Path(args.in_file_name)
    if not in_file_path.exists():
        log(project_directory, AGENT_NAME, f"Error: Input file not found at {in_file_path}")
        sys.exit(1)

    try:
        with open(in_file_path, 'r', encoding='utf-8') as f:
            input_code = f.read()
    except Exception as e:
        log(project_directory, AGENT_NAME, f"Error reading input file {in_file_path}: {e}")
        sys.exit(1)

    # Count annotatable functions to decide: splitter path vs direct LLM path.
    # Multi-function files benefit from bottom-up per-function annotation via the
    # splitter+writer agents; single-function files use the original monolithic call.
    _use_splitter = False
    try:
        _tree = _ast_module.parse(input_code)
        _func_count = 0
        for _node in _ast_module.iter_child_nodes(_tree):
            if isinstance(_node, _ast_module.FunctionDef):
                if not (_node.name.startswith('__') and _node.name.endswith('__')):
                    _func_count += 1
            elif isinstance(_node, _ast_module.ClassDef):
                for _child in _ast_module.iter_child_nodes(_node):
                    if isinstance(_child, _ast_module.FunctionDef):
                        if not (_child.name.startswith('__') and _child.name.endswith('__')):
                            _func_count += 1
        _use_splitter = _func_count > 1
    except SyntaxError:
        pass  # if the file can't parse, fall through to direct LLM path

    if _use_splitter:
        log(project_directory, AGENT_NAME,
            f"Multi-function file ({_func_count} functions), using splitter+writer pipeline")
        try:
            from importlib import util as _importlib_util
            _splitter_path = Path(__file__).parent / "agent-splitter.py"
            _spec = _importlib_util.spec_from_file_location("agent_splitter", _splitter_path)
            _splitter_mod = _importlib_util.module_from_spec(_spec)
            _spec.loader.exec_module(_splitter_mod)
            generated_code = _splitter_mod.run_splitter(
                input_path=in_file_path,
                output_path=Path(args.out_file_name),
                config_path=config_path,
                project_root=project_root,
                memory_model=memory_model,
                project_directory=project_directory,
            )
        except Exception as e:
            log(project_directory, AGENT_NAME,
                f"Splitter failed ({e}), falling back to direct LLM annotation")
            _use_splitter = False

    if not _use_splitter:
        # Original monolithic LLM path: load skill, build prompt, call LLM once.
        # Try RAG retrieval first; fall back to full skill file if unavailable
        skill_content = None
        if rag_index_name:
            rag_index_path = Path(rag_index_name)
            if not rag_index_path.is_absolute():
                rag_index_path = project_root / rag_index_path
            _code_query = input_code[:800]
            _func_sigs = re.findall(r'^[ \t]*(?:class|def)\s+[^\n]+', input_code, re.MULTILINE)
            if _func_sigs:
                _code_query += "\n" + "\n".join(_func_sigs[:5])
            skill_content = retrieve_skill_chunks(
                index_path=rag_index_path,
                main_query=_code_query,
                top_k=rag_top_k,
                project_root=project_root,
                essential_queries=_ESSENTIAL_QUERIES,
            )
            if skill_content:
                log(project_directory, AGENT_NAME, "Using RAG-retrieved skill chunks")

        if skill_content is None:
            log(project_directory, AGENT_NAME, "Using full skill file (RAG index unavailable)")
            try:
                with open(skill_annotator_path, 'r', encoding='utf-8') as f:
                    skill_content = f.read()
            except Exception as e:
                log(project_directory, AGENT_NAME, f"Error reading skill file {skill_annotator_path}: {e}")
                sys.exit(1)

        _model_notes = {
            "hoare": (
                "Use standard value-semantic arrays (`array int`). "
                "No `\\valid`, `\\separated`, or `\\assigns arr[lo..hi]` needed. "
                "Use `#@ assigns \\nothing` for pure functions."
            ),
            "typed": (
                "Arrays are heap-allocated (`loc` type). "
                "Use `#@ requires \\valid(arr, n)` to assert array validity. "
                "Use `#@ requires \\separated(a, na, b, nb)` when arrays must not alias. "
                "Use `#@ assigns arr[0..n]` (with `..`) as the frame condition for in-place mutations. "
                "Use `\\old(arr[i])` in ensures clauses to refer to the pre-state value of `arr[i]`. "
                "Use `#@ label L` immediately before a statement to mark a program point, "
                "then `\\at(arr[i], L)` in contracts to reference the array state at that point."
            ),
            "store": (
                "Same as typed model: arrays are heap-allocated. "
                "Use `#@ requires \\valid(arr, n)`, `#@ requires \\separated(a, na, b, nb)`, "
                "`#@ assigns arr[0..n]`, `\\old(arr[i])`, `#@ label L`, and `\\at(arr[i], L)` "
                "as needed for heap-aware contracts."
            ),
        }
        _memory_model_context = (
            f"\n\n# ACTIVE MEMORY MODEL: {memory_model.upper()}\n"
            f"The pipeline is configured to use the `{memory_model}` memory model. "
            + _model_notes.get(memory_model, _model_notes["hoare"])
        )
        prompt = f"{skill_content}{_memory_model_context}\n\nJust output the python code between \"```python\" and \"```\".\n\n{input_code}"

        try:
            generated_code = llm_generate(prompt=prompt, system="", agent_id=AGENT_NAME, model=model)
        except Exception as e:
            log(project_directory, AGENT_NAME, f"Error calling LLM: {e}")
            sys.exit(1)

        # Extract code from markdown fences if present
        generated_code = extract_code_block(generated_code, "python")

    pipeline = GuardPipeline(generated_code)

    pipeline.apply("inject-recursive-variants",
                   lambda c: _inject_recursive_variants(c, project_directory))
    pipeline.apply("strip-division",
                   lambda c: re.sub(r'(?<![:/])/(?!/)', '//', c))
    pipeline.apply("strip-raise",
                   lambda c: re.sub(r'^[ \t]*raise\b[^\n]*\n?', '', c, flags=re.MULTILINE))
    pipeline.apply("ensure-function-contracts", _ensure_function_contracts)
    pipeline.apply("strip-return-none",
                   lambda c: re.sub(r'\breturn\s+None\b', 'return', c))
    pipeline.apply("none-sentinel",
                   lambda c: re.sub(r'\b(\w+)\s+is\s+None\b', r'\1 < 0',
                                    re.sub(r'\b(\w+)\s*=\s*None\b', r'\1 = -1', c)))
    pipeline.apply("strip-math-pi", _guard_strip_math_pi)
    pipeline.apply("str-params-rewrite", _guard_str_params_rewrite)
    pipeline.apply("string-subscripts",
                   lambda c: re.sub(r"(\b\w+)\['[^']*'\]", r'\1[0]',
                                    re.sub(r'(\b\w+)\["[^"]*"\]', r'\1[0]', c)))
    pipeline.apply("dict-get",
                   lambda c: re.sub(r'\b\w+\.get\(\s*\w+\s*,\s*(\d+)\s*\)', r'\1', c))
    pipeline.apply("sorted-set",
                   lambda c: re.sub(r'\bset\(\s*(\w+)\s*\)', r'\1',
                                    re.sub(r'\bsorted\(\s*(\w+)\s*\)', r'\1',
                                           re.sub(r'\bsorted\(\s*set\(\s*(\w+)\s*\)\s*\)', r'\1', c))))
    pipeline.apply("inject-trusted-dict-assign", _inject_trusted_for_dict_subscript_assignment)
    pipeline.apply("modulo-in-invariant",
                   lambda c: re.sub(r'(#@\s*loop invariant\s+\w+)\s*%\s*\d+\s*==\s*\d+',
                                    r'\1 >= 3', c))
    pipeline.apply("bool-constants-in-contracts", _guard_bool_constants_in_contracts)
    pipeline.apply("floordiv-in-contracts", _guard_floordiv_in_contracts)
    pipeline.apply("len-to-length",
                   lambda c: re.sub(
                       r'(#@\s*(?:requires|ensures|loop invariant)\b[^\n]*)(?<!\\)\blen\s*\(\s*(\w+)\s*\)',
                       r'\1\\length(\2)', c))
    pipeline.apply("strengthen-ensures", _strengthen_ensures)
    pipeline.apply("strip-nonlinear-conservation", _strip_nonlinear_conservation_invariant)
    pipeline.apply("weaken-offset-start-invariant", _weaken_offset_start_loop_invariant)
    pipeline.apply("strengthen-loop-counter", _strengthen_loop_counter_invariant)
    pipeline.apply("inject-offset-lower-bound", _inject_offset_lower_bound_invariant)
    pipeline.apply("tighten-pred-access", _tighten_lower_bound_for_pred_access)
    pipeline.apply("strip-unprovable-additive", _strip_unprovable_additive_invariants)
    pipeline.apply("strengthen-binary-search", _strengthen_binary_search_invariants)
    pipeline.apply("requires-length-trivial",
                   lambda c: re.sub(
                       r'([ \t]*#@\s*requires\s+)\\length\s*\(\s*\w+\s*\)\s*>=\s*0\s*$',
                       r'\g<1>1 == 1', c, flags=re.MULTILINE))
    pipeline.apply("split-two-pointer", _split_two_pointer_compound_invariant)
    pipeline.apply("list-params", _guard_list_params)
    pipeline.apply("fix-list-return-type", _fix_list_return_type)
    pipeline.apply("remove-spurious-old-length", _remove_spurious_old_length_plus1)
    pipeline.apply("str-length-neutralize", _guard_str_length_neutralize)
    pipeline.apply("downgrade-result-len-return", _downgrade_result_ge1_for_len_return)
    pipeline.apply("downgrade-result-sum", _downgrade_result_ge1_for_sum)
    pipeline.apply("rename-val", _guard_rename_val)
    pipeline.apply("rename-goal", _guard_rename_goal)
    pipeline.apply("rename-match", _guard_rename_match)
    pipeline.apply("rename-result", _guard_rename_result)
    pipeline.apply("strip-default-args", _strip_default_args)
    pipeline.apply("assigns-normalize-slice",
                   lambda c: re.sub(r'(#@\s*assigns\s+\w+)\[\s*\.\.', r'\g<1>[0..', c,
                                    flags=re.MULTILINE))
    pipeline.apply("assigns-strip-assignment",
                   lambda c: re.sub(r'(#@\s*assigns\b[^\n]*?)=.*$', r'\1', c,
                                    flags=re.MULTILINE))
    pipeline.apply("obj-syntax-rewrite",
                   lambda c: re.sub(
                       r'(#@[^\n]*)\bobj_(\w+)\b',
                       lambda m: m.group(1) + 'self.' + m.group(2).lstrip('_') if m.group(2).startswith('_')
                                 else m.group(1) + 'self._' + m.group(2),
                       c, flags=re.MULTILINE))
    pipeline.apply("bare-invariant-normalize",
                   lambda c: re.sub(
                       r'(#@[ \t]+)(?!class\s)(?!loop\s)invariant([ \t]+self\.)',
                       r'\1class invariant\2', c, flags=re.MULTILINE))
    pipeline.apply("strip-class-invariant-unsupported", _guard_strip_class_invariant_unsupported)
    pipeline.apply("check-class-invariant-guards", _check_class_invariant_guards)
    pipeline.apply("collapse-annotation-blank-lines",
                   lambda c: re.sub(
                       r'((?:^[ \t]*#@[^\n]*\n)+)\n+([ \t]*(?:def|class)\s)',
                       r'\1\2', c, flags=re.MULTILINE))
    pipeline.apply("collapse-label-blank-lines",
                   lambda c: re.sub(r'(^[ \t]*#@\s*label\s+\w+[^\n]*\n)\n+', r'\1', c,
                                    flags=re.MULTILINE))
    pipeline.apply("normalize-valid-separated", _guard_normalize_valid_separated)
    pipeline.apply("string-literal-comparisons", _guard_string_literal_comparisons)
    pipeline.apply("requires-bare-ident",
                   lambda c: re.sub(r'(#@\s*requires\s+)([A-Za-z_]\w*)\s*$',
                                    r'\g<1>\g<2> > 0', c, flags=re.MULTILINE))
    pipeline.apply("length-self-attr", _guard_length_self_attr)
    pipeline.apply("truncated-contracts", _guard_truncated_contracts)
    pipeline.apply("ensures-invalid", _guard_ensures_invalid)
    pipeline.apply("assigns-bare-ident",
                   lambda c: re.sub(
                       r'(#@\s*assigns\s+)(?!\\nothing\b)(?!self\.)([A-Za-z_]\w*)\s*$',
                       r'\g<1>\\nothing', c, flags=re.MULTILINE))
    pipeline.apply("fix-empty-conditional-bodies", _fix_empty_conditional_bodies)
    pipeline.apply("isinstance-hasattr",
                   lambda c: re.sub(r'\bhasattr\s*\([^)]*\)', 'True',
                                    re.sub(r'\bisinstance\s*\([^)]*\)', 'True', c)))
    pipeline.apply("strip-external-type-bodies", _strip_external_type_bodies)
    pipeline.apply("inject-n-bound-requires", _inject_n_bound_requires)
    pipeline.apply("ensures-length-arithmetic-2", _guard_ensures_length_arithmetic)
    pipeline.apply("remove-array-typed-variant", _remove_array_typed_variant)
    pipeline.apply("fix-mismatched-loop-bound", _fix_mismatched_loop_bound_invariant)
    pipeline.apply("dedup-contract-blocks", _dedup_contract_blocks)
    pipeline.apply("rewrite-return-in-while", _rewrite_return_in_if_inside_while)
    pipeline.apply("fix-bare-len-sentinel", _fix_bare_len_sentinel)
    pipeline.apply("fix-const-return-after-flag", _fix_const_return_after_flag_loop)
    pipeline.apply("fix-bool-flag-conditions", _fix_bool_flag_conditions)
    pipeline.apply("fix-annotation-indentation", _fix_annotation_indentation)
    pipeline.apply("body-preservation", _guard_body_preservation(input_code))

    generated_code = pipeline.code

    # Guard: libcst (Module1_Ingestor) assigns all comment/blank lines at the
    # very top of a file to Module.header rather than to the first statement's
    # leading_lines.  When the annotated output starts with '#@' annotations
    # immediately (no preceding Python statement), Module1 cannot find them in
    # the first FunctionDef's (or ClassDef's) leading_lines and the contracts
    # are silently dropped from the WhyML output.  Inserting a sentinel
    # no-op expression statement as the very first line ensures the '#@' block
    # ends up in the node's leading_lines instead of Module.header, so
    # Module1 correctly extracts and attaches contracts for every function and
    # class invariant.
    first_nonblank = next(
        (l for l in generated_code.splitlines() if l.strip()), ""
    )
    if first_nonblank.strip().startswith("#@"):
        generated_code = '""  # pycsl\n' + generated_code

    out_file_path = Path(args.out_file_name)
    try:
        out_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_file_path, 'w', encoding='utf-8') as f:
            f.write(generated_code)
        log(project_directory, AGENT_NAME, f"Successfully saved annotated code to {out_file_path}")
    except Exception as e:
        log(project_directory, AGENT_NAME, f"Error writing output file {out_file_path}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
    
