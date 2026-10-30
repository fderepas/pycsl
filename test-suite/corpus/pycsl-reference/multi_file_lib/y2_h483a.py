"""Helper for corpus 7670 (route #483): rebinds its own constant through its `__builtins__` MAPPING."""
K = 1
__builtins__['exec']('K = 0')
