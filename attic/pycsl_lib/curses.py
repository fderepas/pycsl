"""PyCSL mock for Python's curses module — An interface to the curses library, providing portable."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def assume_default_colors(fg: int, bg: int) -> int:
    """Mock: Allow use of default values for colors on terminals supporting this feature. Use this to support transparency in your ap..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def baudrate() -> int:
    """Mock: Return the output speed of the terminal in bits per second.  On software terminal emulators it will have a fixed high va..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def beep() -> int:
    """Mock: Emit a short attention sound."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def can_change_color() -> int:
    """Mock: Return ``True`` or ``False``, depending on whether the programmer can change the colors displayed by the terminal."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def cbreak() -> int:
    """Mock: Enter cbreak mode.  In cbreak mode (sometimes called 'rare' mode) normal tty line buffering is turned off and characters..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def color_content(color_number: int) -> int:
    """Mock: Return the intensity of the red, green, and blue (RGB) components in the color *color_number*, which must be between ``0..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def color_pair(pair_number: int) -> int:
    """Mock: Return the attribute value for displaying text in the specified color pair. Only the first 256 color pairs are supported..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def curs_set(visibility: int) -> int:
    """Mock: Set the cursor state.  *visibility* can be set to ``0``, ``1``, or ``2``, for invisible, normal, or very visible.  If th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def def_prog_mode() -> int:
    """Mock: Save the current terminal mode as the 'program' mode, the mode when the running program is using curses.  (Its counterpa..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def def_shell_mode() -> int:
    """Mock: Save the current terminal mode as the 'shell' mode, the mode when the running program is not using curses.  (Its counter..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def delay_output(ms: int) -> int:
    """Mock: Insert an *ms* millisecond pause in output."""
    return 0

#@ \trusted
#@ ensures \result == 0
def doupdate() -> int:
    """Mock: Update the physical screen.  The curses library keeps two data structures, one representing the current physical screen ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def echo() -> int:
    """Mock: Enter echo mode.  In echo mode, each character input is echoed to the screen as it is entered."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def endwin() -> int:
    """Mock: De-initialize the library, and return terminal to normal status."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def erasechar() -> int:
    """Mock: Return the user's current erase character as a one-byte bytes object.  Under Unix operating systems this is a property o..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def filter() -> int:
    """Mock: The :func:`.filter` routine, if used, must be called before :func:`initscr` is called.  The effect is that, during those..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def flash() -> int:
    """Mock: Flash the screen.  That is, change it to reverse-video and then change it back in a short interval.  Some people prefer ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def flushinp() -> int:
    """Mock: Flush all input buffers.  This throws away any  typeahead  that  has been typed by the user and has not yet been process..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def getmouse() -> int:
    """Mock: After :meth:`~window.getch` returns :const:`KEY_MOUSE` to signal a mouse event, this method should be called to retrieve..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getsyx() -> int:
    """Mock: Return the current coordinates of the virtual screen cursor as a tuple ``(y, x)``.  If :meth:`leaveok <window.leaveok>` ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getwin(file: int) -> int:
    """Mock: Read window related data stored in the file by an earlier :func:`window.putwin` call. The routine then creates and initi..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def has_colors() -> int:
    """Mock: Return ``True`` if the terminal can display colors; otherwise, return ``False``."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def has_extended_color_support() -> int:
    """Mock: Return ``True`` if the module supports extended colors; otherwise, return ``False``. Extended color support allows more ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def has_ic() -> int:
    """Mock: Return ``True`` if the terminal has insert- and delete-character capabilities. This function is included for historical ..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def has_il() -> int:
    """Mock: Return ``True`` if the terminal has insert- and delete-line capabilities, or can simulate  them  using scrolling regions..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def has_key(ch: int) -> int:
    """Mock: Take a key value *ch*, and return ``True`` if the current terminal type recognizes a key with that value."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def halfdelay(tenths: int) -> int:
    """Mock: Used for half-delay mode, which is similar to cbreak mode in that characters typed by the user are immediately available..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def init_color(color_number: int, r: int, g: int, b: int) -> int:
    """Mock: Change the definition of a color, taking the number of the color to be changed followed by three RGB values (for the amo..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def init_pair(pair_number: int, fg: int, bg: int) -> int:
    """Mock: Change the definition of a color-pair.  It takes three arguments: the number of the color-pair to be changed, the foregr..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def initscr() -> int:
    """Mock: Initialize the library. Return a :ref:`window <curses-window-objects>` object which represents the whole screen. .. note..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_term_resized(nlines: int, ncols: int) -> int:
    """Mock: Return ``True`` if :func:`resize_term` would modify the window structure, ``False`` otherwise."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isendwin() -> int:
    """Mock: Return ``True`` if :func:`endwin` has been called (that is, the  curses library has been deinitialized)."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def keyname(k: int) -> int:
    """Mock: Return the name of the key numbered *k* as a bytes object.  The name of a key generating printable ASCII character is th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def killchar() -> int:
    """Mock: Return the user's current line kill character as a one-byte bytes object. Under Unix operating systems this is a propert..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def longname() -> int:
    """Mock: Return a bytes object containing the terminfo long name field describing the current terminal.  The maximum length of a ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def meta(flag: int) -> int:
    """Mock: If *flag* is ``True``, allow 8-bit characters to be input.  If *flag* is ``False``,  allow only 7-bit chars."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mouseinterval(interval: int) -> int:
    """Mock: Set the maximum time in milliseconds that can elapse between press and release events in order for them to be recognized..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mousemask(mousemask: int) -> int:
    """Mock: Set the mouse events to be reported, and return a tuple ``(availmask, oldmask)``.   *availmask* indicates which of the s..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def napms(ms: int) -> int:
    """Mock: Sleep for *ms* milliseconds."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def newpad(nlines: int, ncols: int) -> int:
    """Mock: Create and return a pointer to a new pad data structure with the given number of lines and columns.  Return a pad as a w..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def newwin(nlines: int, ncols: int) -> int:
    """Mock: Return a new :ref:`window <curses-window-objects>`, whose left-upper corner is at  ``(begin_y, begin_x)``, and whose hei..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nl() -> int:
    """Mock: Enter newline mode.  This mode translates the return key into newline on input, and translates newline into return and l..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nocbreak() -> int:
    """Mock: Leave cbreak mode.  Return to normal 'cooked' mode with line buffering."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def noecho() -> int:
    """Mock: Leave echo mode.  Echoing of input characters is turned off."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nonl() -> int:
    """Mock: Leave newline mode.  Disable translation of return into newline on input, and disable low-level translation of newline i..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def noqiflush() -> int:
    """Mock: When the :func:`!noqiflush` routine is used, normal flush of input and output queues associated with the ``INTR``, ``QUI..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def noraw() -> int:
    """Mock: Leave raw mode. Return to normal 'cooked' mode with line buffering."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pair_content(pair_number: int) -> int:
    """Mock: Return a tuple ``(fg, bg)`` containing the colors for the requested color pair. The value of *pair_number* must be betwe..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pair_number(attr: int) -> int:
    """Mock: Return the number of the color-pair set by the attribute value *attr*. :func:`color_pair` is the counterpart to this fun..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def putp(str: int) -> int:
    """Mock: Equivalent to ``tputs(str, 1, putchar)``; emit the value of a specified terminfo capability for the current terminal.  N..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def qiflush(flag: int) -> int:
    """Mock: If *flag* is ``False``, the effect is the same as calling :func:`noqiflush`. If *flag* is ``True``, or no argument is pr..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def raw() -> int:
    """Mock: Enter raw mode.  In raw mode, normal line buffering and  processing of interrupt, quit, suspend, and flow control keys a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def reset_prog_mode() -> int:
    """Mock: Restore the  terminal  to 'program' mode, as previously saved  by :func:`def_prog_mode`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def reset_shell_mode() -> int:
    """Mock: Restore the  terminal  to 'shell' mode, as previously saved  by :func:`def_shell_mode`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def resetty() -> int:
    """Mock: Restore the state of the terminal modes to what it was at the last call to :func:`savetty`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def resize_term(nlines: int, ncols: int) -> int:
    """Mock: Backend function used by :func:`resizeterm`, performing most of the work; when resizing the windows, :func:`resize_term`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def resizeterm(nlines: int, ncols: int) -> int:
    """Mock: Resize the standard and current windows to the specified dimensions, and adjusts other bookkeeping data used by the curs..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def savetty() -> int:
    """Mock: Save the current state of the terminal modes in a buffer, usable by :func:`resetty`."""
    return 0

#@ \trusted
#@ ensures \result == 0
def get_escdelay() -> int:
    """Mock: Retrieves the value set by :func:`set_escdelay`. .. versionadded:: 3.9"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_escdelay(ms: int) -> int:
    """Mock: Sets the number of milliseconds to wait after reading an escape character, to distinguish between an individual escape c..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def get_tabsize() -> int:
    """Mock: Retrieves the value set by :func:`set_tabsize`. .. versionadded:: 3.9"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def set_tabsize(size: int) -> int:
    """Mock: Sets the number of columns used by the curses library when converting a tab character to spaces as it adds the tab to a ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setsyx(y: int, x: int) -> int:
    """Mock: Set the virtual screen cursor to *y*, *x*. If *y* and *x* are both ``-1``, then :meth:`leaveok <window.leaveok>` is set ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setupterm(term: int, fd: int) -> int:
    """Mock: Initialize the terminal.  *term* is a string giving the terminal name, or ``None``; if omitted or ``None``, the value of..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def start_color() -> int:
    """Mock: Must be called if the programmer wants to use colors, and before any other color manipulation routine is called.  It is ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def termattrs() -> int:
    """Mock: Return a logical OR of all video attributes supported by the terminal.  This information is useful when a curses program..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def termname() -> int:
    """Mock: Return the value of the environment variable :envvar:`TERM`, as a bytes object, truncated to 14 characters."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tigetflag(capname: int) -> int:
    """Mock: Return the value of the Boolean capability corresponding to the terminfo capability name *capname* as an integer.  Retur..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tigetnum(capname: int) -> int:
    """Mock: Return the value of the numeric capability corresponding to the terminfo capability name *capname* as an integer.  Retur..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tigetstr(capname: int) -> int:
    """Mock: Return the value of the string capability corresponding to the terminfo capability name *capname* as a bytes object.  Re..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tparm(str: int, ___: int) -> int:
    """Mock: Instantiate the bytes object *str* with the supplied parameters, where *str* should be a parameterized string obtained f..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def typeahead(fd: int) -> int:
    """Mock: Specify that the file descriptor *fd* be used for typeahead checking.  If *fd* is ``-1``, then no typeahead checking is ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unctrl(ch: int) -> int:
    """Mock: Return a bytes object which is a printable representation of the character *ch*. Control characters are represented as a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ungetch(ch: int) -> int:
    """Mock: Push *ch* so the next :meth:`~window.getch` will return it. .. note:: Only one *ch* can be pushed before :meth:`!getch` ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def update_lines_cols() -> int:
    """Mock: Update the :const:`LINES` and :const:`COLS` module variables. Useful for detecting manual screen resize. .. versionadded..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def unget_wch(ch: int) -> int:
    """Mock: Push *ch* so the next :meth:`~window.get_wch` will return it. .. note:: Only one *ch* can be pushed before :meth:`!get_w..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def ungetmouse(id: int, x: int, y: int, z: int, bstate: int) -> int:
    """Mock: Push a :const:`KEY_MOUSE` event onto the input queue, associating the given state data with it."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def use_env(flag: int) -> int:
    """Mock: If used, this function should be called before :func:`initscr` or newterm are called.  When *flag* is ``False``, the val..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def use_default_colors() -> int:
    """Mock: Equivalent to ``assume_default_colors(-1, -1)``."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def wrapper(func: int) -> int:
    """Mock: Initialize curses and call another callable object, *func*, which should be the rest of your curses-using application.  ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def rectangle(win: int, uly: int, ulx: int, lry: int, lrx: int) -> int:
    """Mock: Draw a rectangle.  The first argument must be a window object; the remaining arguments are coordinates relative to that ..."""
    return 0
