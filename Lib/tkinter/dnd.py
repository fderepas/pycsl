"""PyCSL mock for Python's tkinter.dnd module — Tkinter drag-and-drop interface."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def dnd_start(source: int, event: int) -> int:
    """Mock: Factory function for drag-and-drop process."""
    return 0
