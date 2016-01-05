from os import path, read
import re, traceback
import logging

included_files = set()

ns = globals()

def get_ns():
    return ns

def require(file):
    """read in files"""
    if path.isabs(file):
        p = path.abspath(file)
    else:
        l = str(traceback.extract_stack()[-1][0])
        d = path.dirname(l)
        p = path.abspath(path.join(d, file))
    found = False
    for ext in ['', '.dv', '.py']:
        f = p+ext
        if path.exists(f):
            if f not in included_files:
                included_files.add(f)
                try:
                    fh = open(f)
                    c  = fh.read()
                    o  = compile(c, p, 'exec')
                    exec(o, ns, ns)
                finally:
                    fh.close()
            found = True
            break
    if not found:
        raise Exception("cannot find " + file)

