"""PyCSL mock for Python's tkinter.messagebox module — Various types of alert dialogs."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def showinfo(title: int, message: int) -> int:
    """Mock: Creates and displays an information message box with the specified title and message."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def showwarning(title: int, message: int) -> int:
    """Mock: Creates and displays a warning message box with the specified title and message."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def showerror(title: int, message: int) -> int:
    """Mock: Creates and displays an error message box with the specified title and message."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def askquestion(title: int, message: int, type_: int) -> int:
    """Mock: Ask a question. By default shows buttons :data:`YES` and :data:`NO`. Returns the symbolic name of the selected button."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def askokcancel(title: int, message: int) -> int:
    """Mock: Ask if operation should proceed. Shows buttons :data:`OK` and :data:`CANCEL`. Returns ``True`` if the answer is ok and `..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def askretrycancel(title: int, message: int) -> int:
    """Mock: Ask if operation should be retried. Shows buttons :data:`RETRY` and :data:`CANCEL`. Return ``True`` if the answer is yes..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def askyesno(title: int, message: int) -> int:
    """Mock: Ask a question. Shows buttons :data:`YES` and :data:`NO`. Returns ``True`` if the answer is yes and ``False`` otherwise."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def askyesnocancel(title: int, message: int) -> int:
    """Mock: Ask a question. Shows buttons :data:`YES`, :data:`NO` and :data:`CANCEL`. Return ``True`` if the answer is yes, ``None``..."""
    return 0
