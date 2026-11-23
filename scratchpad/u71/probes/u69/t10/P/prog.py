import zu692.b
import zu692.c
setattr(zu692, "b", zu692.c)


#@ ensures \result == 1
def g() -> int:
    return zu692.b.one()


print("result", g())
