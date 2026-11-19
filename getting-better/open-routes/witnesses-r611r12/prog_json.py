import json


#@ ensures \result == True
#@ assigns \nothing
def same() -> bool:
    return json.dumps("a") == json.dumps("a")


if __name__ == "__main__":
    r = same()
    print("result", r, "OK" if r is True else "VIOLATION ensures")
