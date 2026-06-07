# Pure model for configparser — INI file parser
# Models ConfigParser as section-count tracker.

""" # pycsl"""


#@ class invariant self._sections >= 0
class ConfigParser:
    """Abstract INI parser tracking section count."""

    #@ ensures self._sections == 0
    def __init__(self) -> None:
        self._sections: int = 0

    #@ ensures self._sections == \old(self._sections) + 1
    #@ assigns self._sections
    def add_section(self, name: int) -> None:
        """Add a named section."""
        self._sections = self._sections + 1

    #@ requires self._sections > 0
    #@ ensures self._sections == \old(self._sections) - 1
    #@ assigns self._sections
    def remove_section(self, name: int) -> None:
        """Remove a named section."""
        self._sections = self._sections - 1

    #@ ensures \result == self._sections
    def section_count(self) -> int:
        """Return number of sections."""
        return self._sections

    #@ ensures \result >= 0
    def has_section(self, name: int) -> int:
        """Return 1 if section exists, else 0."""
        if self._sections > 0:
            return 1
        return 0

    #@ ensures \result >= 0
    def get(self, section: int, option: int) -> int:
        """Get option value (modeled as length)."""
        return 0

    #@ assigns self._sections
    def read(self, filename: int) -> None:
        """Read configuration from file."""
        self._sections = self._sections
