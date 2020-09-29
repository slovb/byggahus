def dfdx(f, x, h):
    return (f(x+h) - f(x-h)) / (2.0*h)

def find_root(f, x0, h):
    last = x0
    x = x0 + 10.0*h
    while (abs(last - x) > h):
        last = x
        d = dfdx(f, x, h)
        if 10.0*abs(d) < h: # divide-by-zero protection
            return x
        x-= f(x) / d
    return x