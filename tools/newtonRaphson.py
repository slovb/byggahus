def dfdx(f, x, h):
    return (f(x+h) - f(x-h)) / (2.0*h)

def find_root(f, x0, h):
    last = x0
    x = x0 + 10.0*h
    for i in range(10):
        last = x
        d = dfdx(f, x, h)
        if 10.0*abs(d) < h: # divide-by-zero protection
            break
        x-= f(x) / d
        if abs(last - x) < h:
            break
    return x
