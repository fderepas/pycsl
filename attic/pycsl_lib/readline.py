"""PyCSL mock for Python's readline module — GNU readline support for Python."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def parse_and_bind(string: int) -> int:
    """Mock: Execute the init line provided in the *string* argument. This calls :c:func:`!rl_parse_and_bind` in the underlying libra..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def read_init_file(filename: int) -> int:
    """Mock: Execute a readline initialization file. The default filename is the last filename used. This calls :c:func:`!rl_read_ini..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_line_buffer() -> int:
    """Mock: Return the current contents of the line buffer (:c:data:`!rl_line_buffer` in the underlying library)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def insert_text(string: int) -> int:
    """Mock: Insert text into the line buffer at the cursor position.  This calls :c:func:`!rl_insert_text` in the underlying library..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def redisplay() -> int:
    """Mock: Change what's displayed on the screen to reflect the current contents of the line buffer.  This calls :c:func:`!rl_redis..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def read_history_file(filename: int) -> int:
    """Mock: Load a readline history file, and append it to the history list. The default filename is :file:`~/.history`.  This calls..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def write_history_file(filename: int) -> int:
    """Mock: Save the history list to a readline history file, overwriting any existing file.  The default filename is :file:`~/.hist..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def append_history_file(nelements: int, filename: int) -> int:
    """Mock: Append the last *nelements* items of history to a file.  The default filename is :file:`~/.history`.  The file must alre..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_history_length() -> int:
    """Mock: Set or return the desired number of lines to save in the history file. The :func:`write_history_file` function uses this..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def clear_history() -> int:
    """Mock: Clear the current history.  This calls :c:func:`!clear_history` in the underlying library.  The Python function only exi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_current_history_length() -> int:
    """Mock: Return the number of items currently in the history.  (This is different from :func:`get_history_length`, which returns ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_history_item(index: int) -> int:
    """Mock: Return the current contents of history item at *index*.  The item index is one-based.  This calls :c:func:`!history_get`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def remove_history_item(pos: int) -> int:
    """Mock: Remove history item specified by its position from the history. The position is zero-based.  This calls :c:func:`!remove..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def replace_history_item(pos: int, line: int) -> int:
    """Mock: Replace history item specified by its position with *line*. The position is zero-based.  This calls :c:func:`!replace_hi..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def add_history(line: int) -> int:
    """Mock: Append *line* to the history buffer, as if it was the last line typed. This calls :c:func:`!add_history` in the underlyi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_auto_history(enabled: int) -> int:
    """Mock: Enable or disable automatic calls to :c:func:`!add_history` when reading input via readline.  The *enabled* argument sho..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_startup_hook(function_: int) -> int:
    """Mock: Set or remove the function invoked by the :c:data:`!rl_startup_hook` callback of the underlying library.  If *function* ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_pre_input_hook(function_: int) -> int:
    """Mock: Set or remove the function invoked by the :c:data:`!rl_pre_input_hook` callback of the underlying library.  If *function..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def get_pre_input_hook() -> int:
    """Mock: Get the current pre-input hook function, or ``None`` if no pre-input hook function has been set.  This function only exi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_completer(function_: int) -> int:
    """Mock: Set or remove the completer function.  If *function* is specified, it will be used as the new completer function; if omi..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def get_completer() -> int:
    """Mock: Get the completer function, or ``None`` if no completer function has been set."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_completion_type() -> int:
    """Mock: Get the type of completion being attempted.  This returns the :c:data:`!rl_completion_type` variable in the underlying l..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_begidx() -> int:
    """Mock: Get the beginning or ending index of the completion scope. These indexes are the *start* and *end* arguments passed to t..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_completer_delims(string: int) -> int:
    """Mock: Set or get the word delimiters for completion.  These determine the start of the word to be considered for completion (t..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def set_completion_display_matches_hook(function_: int) -> int:
    """Mock: Set or remove the completion display function.  If *function* is specified, it will be used as the new completion displa..."""
    return 0
