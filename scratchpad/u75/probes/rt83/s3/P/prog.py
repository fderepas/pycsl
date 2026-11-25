import zv83s3.b
import code

code.InteractiveInterpreter().runsource("import zv83s3, zv83s3.c; zv83s3.b = zv83s3.c")


#@ ensures \result == 1
def g() -> int:
    return zv83s3.b.one()


print("result", g())
