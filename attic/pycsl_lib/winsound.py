"""PyCSL mock for Python's winsound module — Access to the sound-playing machinery for Windows."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def Beep(frequency: int, duration: int) -> int:
    """Mock: Beep the PC's speaker. The *frequency* parameter specifies frequency, in hertz, of the sound, and must be in the range 3..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def PlaySound(sound: int, flags: int) -> int:
    """Mock: Call the underlying :c:func:`!PlaySound` function from the Platform API.  The *sound* parameter may be a filename, a sys..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def MessageBeep(type_: int) -> int:
    """Mock: Call the underlying :c:func:`!MessageBeep` function from the Platform API.  This plays a sound as specified in the regis..."""
    return 0
