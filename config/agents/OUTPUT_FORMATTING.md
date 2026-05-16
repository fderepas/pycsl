# Output Formatting Enhancements

## Summary
Added strict output formatting requirements and markdown fence extraction to ensure LLM responses are properly captured.

## Changes Made

### 1. agent-annotate.md
- Updated to require output in markdown code fences: ` ```python ` and ` ``` `
- Changed prompt from generic instruction to specific fence requirement

### 2. agent-annotate.py
- **Added imports**: `import re`
- **Added `extract_code_block()` function**: Extracts code between markdown fences
  - Matches `\`\`\`python ... \`\`\`` pattern
  - Falls back to generic `\`\`\` ... \`\`\`` pattern if needed
  - Returns original text if no fences found
- **Updated prompt**: Added "Just output the python code between \"\`\`\`python\" and \"\`\`\`\"."
- **Updated output handling**: Calls `extract_code_block(generated_code, "python")` on LLM response

### 3. agent-reconcile.md
- Updated to require output in markdown code fences: ` ```json ` and ` ``` `
- Changed constraints to specify JSON fence requirement

### 4. agent-reconcile.py
- **Added imports**: `import re`
- **Added `extract_code_block()` function**: Same logic as agent-annotate.py but language-agnostic
- **Updated prompt**: Added "Just output the JSON between \"\`\`\`json\" and \"\`\`\`\"."
- **Updated output handling**: Calls `extract_code_block(llm_response, "json")` before JSON parsing

## Extraction Logic

The `extract_code_block(text, language)` function:

1. Tries to match language-specific fences: `` `\`\`{language}\n(.*?)\n\`\`\`` ``
2. Falls back to generic fences: `` `\`\`\`\n(.*?)\n\`\`\`` ``
3. Returns original text if no fences found (for plain output)

### Regex Patterns

**Language-specific** (e.g., for "python"):
```
```python
(.*?)
```
```

**Generic**:
```
```
(.*?)
```
```

## Benefits

1. **Robust extraction**: Handles both fenced and unfenced LLM responses
2. **Strict prompting**: Instructs LLMs to use markdown fences
3. **Fallback handling**: Works even if LLM partially ignores instructions
4. **Clean output**: Removes markdown formatting from final files
5. **Language-specific**: Python code vs JSON handled appropriately

## Testing

Both agents compile without syntax errors:
```bash
✓ Both agents compile successfully
```

## Files Modified

- `/ai/PyCSL/agents/agent-annotate.md`
- `/ai/PyCSL/agents/agent-annotate.py`
- `/ai/PyCSL/agents/agent-reconcile.md`
- `/ai/PyCSL/agents/agent-reconcile.py`
