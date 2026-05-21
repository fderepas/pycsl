"""PyCSL mock for Python's turtle module — An educational framework for simple graphics applications."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def forward(distance: int) -> int:
    """Mock: :param distance: a number (integer or float) Move the turtle forward by the specified *distance*, in the direction the t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def back(distance: int) -> int:
    """Mock: :param distance: a number Move the turtle backward by *distance*, opposite to the direction the turtle is headed.  Do no..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def right(angle: int) -> int:
    """Mock: :param angle: a number (integer or float) Turn turtle right by *angle* units.  (Units are by default degrees, but can be..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def left(angle: int) -> int:
    """Mock: :param angle: a number (integer or float) Turn turtle left by *angle* units.  (Units are by default degrees, but can be ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def goto(x: int, y: int) -> int:
    """Mock: :param x: a number or a pair/vector of numbers :param y: a number or ``None`` If *y* is ``None``, *x* must be a pair of ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def teleport(x: int, y: int, fill_gap: int) -> int:
    """Mock: :param x: a number or ``None`` :param y: a number or ``None`` :param fill_gap: a boolean Move turtle to an absolute posi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setx(x: int) -> int:
    """Mock: :param x: a number (integer or float) Set the turtle's first coordinate to *x*, leave second coordinate unchanged. .. do..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sety(y: int) -> int:
    """Mock: :param y: a number (integer or float) Set the turtle's second coordinate to *y*, leave first coordinate unchanged. .. do..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def setheading(to_angle: int) -> int:
    """Mock: :param to_angle: a number (integer or float) Set the orientation of the turtle to *to_angle*.  Here are some common dire..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def home() -> int:
    """Mock: Move turtle to the origin -- coordinates (0,0) -- and set its heading to its start-orientation (which depends on the mod..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def circle(radius: int, extent: int, steps: int) -> int:
    """Mock: :param radius: a number :param extent: a number (or ``None``) :param steps: an integer (or ``None``) Draw a circle with ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def dot() -> int:
    """Mock: :param size: an integer >= 1 (if given) :param color: a colorstring or a numeric color tuple Draw a circular dot with di..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def stamp() -> int:
    """Mock: Stamp a copy of the turtle shape onto the canvas at the current turtle position.  Return a stamp_id for that stamp, whic..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def clearstamp(stampid: int) -> int:
    """Mock: :param stampid: an integer, must be return value of previous :func:`stamp` call Delete stamp with given *stampid*. .. do..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def clearstamps(n: int) -> int:
    """Mock: :param n: an integer (or ``None``) Delete all or first/last *n* of turtle's stamps.  If *n* is ``None``, delete all stam..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def undo() -> int:
    """Mock: Undo (repeatedly) the last turtle action(s).  Number of available undo actions is determined by the size of the undobuff..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def speed(speed: int) -> int:
    """Mock: :param speed: an integer in the range 0..10 or a speedstring (see below) Set the turtle's speed to an integer value in t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def position() -> int:
    """Mock: Return the turtle's current location (x,y) (as a :class:`Vec2D` vector). .. doctest:: :skipif: _tkinter is None >>> turt..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def towards(x: int, y: int) -> int:
    """Mock: :param x: a number or a pair/vector of numbers or a turtle instance :param y: a number if *x* is a number, else ``None``..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def xcor() -> int:
    """Mock: Return the turtle's x coordinate. .. doctest:: :skipif: _tkinter is None >>> turtle.home() >>> turtle.left(50) >>> turtl..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ycor() -> int:
    """Mock: Return the turtle's y coordinate. .. doctest:: :skipif: _tkinter is None >>> turtle.home() >>> turtle.left(60) >>> turtl..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def heading() -> int:
    """Mock: Return the turtle's current heading (value depends on the turtle mode, see :func:`mode`). .. doctest:: :skipif: _tkinter..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def distance(x: int, y: int) -> int:
    """Mock: :param x: a number or a pair/vector of numbers or a turtle instance :param y: a number if *x* is a number, else ``None``..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def degrees(fullcircle: int) -> int:
    """Mock: :param fullcircle: a number Set angle measurement units, i.e. set number of 'degrees' for a full circle. Default value i..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def radians() -> int:
    """Mock: Set the angle measurement units to radians.  Equivalent to ``degrees(2*math.pi)``. .. doctest:: :skipif: _tkinter is Non..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pendown() -> int:
    """Mock: Pull the pen down -- drawing when moving."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def penup() -> int:
    """Mock: Pull the pen up -- no drawing when moving."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pensize(width: int) -> int:
    """Mock: :param width: a positive number Set the line thickness to *width* or return it.  If resizemode is set to 'auto' and turt..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pen(pen: int) -> int:
    """Mock: :param pen: a dictionary with some or all of the below listed keys :param pendict: one or more keyword-arguments with th..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isdown() -> int:
    """Mock: Return ``True`` if pen is down, ``False`` if it's up. .. doctest:: :skipif: _tkinter is None >>> turtle.penup() >>> turt..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pencolor() -> int:
    """Mock: Return or set the pencolor. Four input formats are allowed: ``pencolor()`` Return the current pencolor as color specific..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fillcolor() -> int:
    """Mock: Return or set the fillcolor. Four input formats are allowed: ``fillcolor()`` Return the current fillcolor as color speci..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def color() -> int:
    """Mock: Return or set pencolor and fillcolor. Several input formats are allowed.  They use 0 to 3 arguments as follows: ``color(..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def filling() -> int:
    """Mock: Return fillstate (``True`` if filling, ``False`` else). .. doctest:: :skipif: _tkinter is None >>> turtle.begin_fill() >..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def fill() -> int:
    """Mock: Fill the shape drawn in the ``with turtle.fill():`` block. .. doctest:: :skipif: _tkinter is None >>> turtle.color('blac..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def begin_fill() -> int:
    """Mock: To be called just before drawing a shape to be filled."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def end_fill() -> int:
    """Mock: Fill the shape drawn after the last call to :func:`begin_fill`. Whether or not overlap regions for self-intersecting pol..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def reset() -> int:
    """Mock: Delete the turtle's drawings from the screen, re-center the turtle and set variables to the default values. .. doctest::..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def clear() -> int:
    """Mock: Delete the turtle's drawings from the screen.  Do not move turtle.  State and position of the turtle as well as drawings..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def write(arg: int, move: int, align: int, font: int) -> int:
    """Mock: :param arg: object to be written to the TurtleScreen :param move: True/False :param align: one of the strings 'left', 'c..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def hideturtle() -> int:
    """Mock: Make the turtle invisible.  It's a good idea to do this while you're in the middle of doing some complex drawing, becaus..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def showturtle() -> int:
    """Mock: Make the turtle visible. .. doctest:: :skipif: _tkinter is None >>> turtle.showturtle()"""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def isvisible() -> int:
    """Mock: Return ``True`` if the Turtle is shown, ``False`` if it's hidden. >>> turtle.hideturtle() >>> turtle.isvisible() False >..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shape(name: int) -> int:
    """Mock: :param name: a string which is a valid shapename Set turtle shape to shape with given *name* or, if name is not given, r..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def resizemode(rmode: int) -> int:
    """Mock: :param rmode: one of the strings 'auto', 'user', 'noresize' Set resizemode to one of the values: 'auto', 'user', 'noresi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shapesize(stretch_wid: int, stretch_len: int, outline: int) -> int:
    """Mock: :param stretch_wid: positive number :param stretch_len: positive number :param outline: positive number Return or set th..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shearfactor(shear: int) -> int:
    """Mock: :param shear: number (optional) Set or return the current shearfactor. Shear the turtleshape according to the given shea..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tilt(angle: int) -> int:
    """Mock: :param angle: a number Rotate the turtleshape by *angle* from its current tilt-angle, but do *not* change the turtle's h..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tiltangle(angle: int) -> int:
    """Mock: :param angle: a number (optional) Set or return the current tilt-angle. If angle is given, rotate the turtleshape to poi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shapetransform(t11: int, t12: int, t21: int, t22: int) -> int:
    """Mock: :param t11: a number (optional) :param t12: a number (optional) :param t21: a number (optional) :param t12: a number (op..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_shapepoly() -> int:
    """Mock: Return the current shape polygon as tuple of coordinate pairs. This can be used to define a new shape or components of a..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def onrelease(fun_: int, btn: int, add: int) -> int:
    """Mock: :param fun: a function with two arguments which will be called with the coordinates of the clicked point on the canvas :..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ondrag(fun_: int, btn: int, add: int) -> int:
    """Mock: :param fun: a function with two arguments which will be called with the coordinates of the clicked point on the canvas :..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def poly() -> int:
    """Mock: Record the vertices of a polygon drawn in the ``with turtle.poly():`` block. The first and last vertices will be connect..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def begin_poly() -> int:
    """Mock: Start recording the vertices of a polygon.  Current turtle position is first vertex of polygon."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def end_poly() -> int:
    """Mock: Stop recording the vertices of a polygon.  Current turtle position is last vertex of polygon.  This will be connected wi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_poly() -> int:
    """Mock: Return the last recorded polygon. .. doctest:: :skipif: _tkinter is None >>> turtle.home() >>> turtle.begin_poly() >>> t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def clone() -> int:
    """Mock: Create and return a clone of the turtle with same position, heading and turtle properties. .. doctest:: :skipif: _tkinte..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getturtle() -> int:
    """Mock: Return the Turtle object itself.  Only reasonable use: as a function to return the 'anonymous turtle': .. doctest:: :ski..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getscreen() -> int:
    """Mock: Return the :class:`TurtleScreen` object the turtle is drawing on. TurtleScreen methods can then be called for that objec..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setundobuffer(size: int) -> int:
    """Mock: :param size: an integer or ``None`` Set or disable undobuffer.  If *size* is an integer, an empty undobuffer of given si..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def undobufferentries() -> int:
    """Mock: Return number of entries in the undobuffer. .. doctest:: :skipif: _tkinter is None >>> while undobufferentries(): ...   ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def bgcolor() -> int:
    """Mock: Return or set the background color of the TurtleScreen. Four input formats are allowed: ``bgcolor()`` Return the current..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def bgpic(picname: int) -> int:
    """Mock: :param picname: a string, name of an image file (PNG, GIF, PGM, and PPM) or ``'nopic'``, or ``None`` Set background imag..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def clearscreen() -> int:
    """Mock: Delete all drawings and all turtles from the TurtleScreen.  Reset the now empty TurtleScreen to its initial state: white..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def resetscreen() -> int:
    """Mock: Reset all Turtles on the Screen to their initial state."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def screensize(canvwidth: int, canvheight: int, bg: int) -> int:
    """Mock: :param canvwidth: positive integer, new width of canvas in pixels :param canvheight: positive integer, new height of can..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setworldcoordinates(llx: int, lly: int, urx: int, ury: int) -> int:
    """Mock: :param llx: a number, x-coordinate of lower left corner of canvas :param lly: a number, y-coordinate of lower left corne..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def no_animation() -> int:
    """Mock: Temporarily disable turtle animation. The code written inside the ``no_animation`` block will not be animated; once the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def delay(delay: int) -> int:
    """Mock: :param delay: positive integer Set or return the drawing *delay* in milliseconds.  (This is approximately the time inter..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def tracer(n: int, delay: int) -> int:
    """Mock: :param n: nonnegative integer :param delay: nonnegative integer Turn turtle animation on/off and set delay for update dr..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def update() -> int:
    """Mock: Perform a TurtleScreen update. To be used when tracer is turned off."""
    return 0

#@ \trusted
#@ ensures \result == 0
def listen(xdummy: int, ydummy: int) -> int:
    """Mock: Set focus on TurtleScreen (in order to collect key-events).  Dummy arguments are provided in order to be able to pass :f..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def onkey(fun_: int, key: int) -> int:
    """Mock: :param fun: a function with no arguments or ``None`` :param key: a string: key (e.g. 'a') or key-symbol (e.g. 'space') B..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def onkeypress(fun_: int, key: int) -> int:
    """Mock: :param fun: a function with no arguments or ``None`` :param key: a string: key (e.g. 'a') or key-symbol (e.g. 'space') B..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def onclick(fun_: int, btn: int, add: int) -> int:
    """Mock: :param fun: a function with two arguments which will be called with the coordinates of the clicked point on the canvas :..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ontimer(fun_: int, t: int) -> int:
    """Mock: :param fun: a function with no arguments :param t: a number >= 0 Install a timer that calls *fun* after *t* milliseconds..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def mainloop() -> int:
    """Mock: Starts event loop - calling Tkinter's mainloop function. Must be the last statement in a turtle graphics program. Must *..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def textinput(title: int, prompt: int) -> int:
    """Mock: :param title: string :param prompt: string Pop up a dialog window for input of a string. Parameter title is the title of..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def numinput(title: int, prompt: int, default: int, minval: int, maxval: int) -> int:
    """Mock: :param title: string :param prompt: string :param default: number (optional) :param minval: number (optional) :param max..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def mode(mode: int) -> int:
    """Mock: :param mode: one of the strings 'standard', 'logo' or 'world' Set turtle mode ('standard', 'logo' or 'world') and perfor..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def colormode(cmode: int) -> int:
    """Mock: :param cmode: one of the values 1.0 or 255 Return the colormode or set it to 1.0 or 255.  Subsequently *r*, *g*, *b* val..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getcanvas() -> int:
    """Mock: Return the Canvas of this TurtleScreen.  Useful for insiders who know what to do with a Tkinter Canvas. .. doctest:: :sk..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getshapes() -> int:
    """Mock: Return a list of names of all currently available turtle shapes. .. doctest:: :skipif: _tkinter is None >>> screen.getsh..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def register_shape(name: int, shape: int) -> int:
    """Mock: There are four different ways to call this function: (1) *name* is the name of an image file (PNG, GIF, PGM, and PPM) an..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def turtles() -> int:
    """Mock: Return the list of turtles on the screen. .. doctest:: :skipif: _tkinter is None >>> for turtle in screen.turtles(): ......"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def window_height() -> int:
    """Mock: Return the height of the turtle window. :: >>> screen.window_height() 480"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def window_width() -> int:
    """Mock: Return the width of the turtle window. :: >>> screen.window_width() 640"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def bye() -> int:
    """Mock: Shut the turtlegraphics window."""
    return 0

#@ \trusted
#@ ensures \result == 0
def exitonclick() -> int:
    """Mock: Bind ``bye()`` method to mouse clicks on the Screen. If the value 'using_IDLE' in the configuration dictionary is ``Fals..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def save(filename: int, overwrite: int) -> int:
    """Mock: Save the current turtle drawing (and turtles) as a PostScript file. :param filename: the path of the saved PostScript fi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setup(width: int, height: int, startx: int, starty: int) -> int:
    """Mock: Set the size and position of the main window.  Default values of arguments are stored in the configuration dictionary an..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def title(titlestring: int) -> int:
    """Mock: :param titlestring: a string that is shown in the titlebar of the turtle graphics window Set title of turtle window to *..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def write_docstringdict(filename: int) -> int:
    """Mock: :param filename: a string, used as filename Create and write docstring-dictionary to a Python script with the given file..."""
    return 0
