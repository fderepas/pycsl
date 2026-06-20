# Pure model for platform — system identification
# Functions return strings describing the platform.


#@ assigns \nothing
def system() -> str:
    """Return the system/OS name (e.g. 'Linux')."""
    return "Linux"


#@ assigns \nothing
def node() -> str:
    """Return the computer's network name."""
    return ""


#@ assigns \nothing
def release() -> str:
    """Return the system's release (e.g. kernel version)."""
    return ""


#@ assigns \nothing
def version() -> str:
    """Return the system's release version."""
    return ""


#@ assigns \nothing
def machine() -> str:
    """Return the machine type (e.g. 'x86_64')."""
    return "x86_64"


#@ assigns \nothing
def processor() -> str:
    """Return the (real) processor name."""
    return ""


#@ assigns \nothing
def python_version() -> str:
    """Return the Python version as string '3.x.y'."""
    return "3.14.0"


#@ ensures \result >= 0
#@ assigns \nothing
def architecture() -> int:
    """Return architecture bits (e.g. 64)."""
    return 64


#@ assigns \nothing
def platform_string() -> str:
    """Return a single string identifying the platform."""
    return "Linux-x86_64"
