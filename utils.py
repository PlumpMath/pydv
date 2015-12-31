from os import path
from importlib import find_loader
import re, traceback

included_files = set()

def require(file, caller=None):
    """read in files"""
    if path.isabs(file):
        b = path.basename(file)
        p = path.abspath(path.join(file+'.py'))
    else:
        if caller:
            l = str(traceback.extract_stack()[-2])
        else:
            l = caller[-2]
        r = re.compile('file (\S+),')
        m = r.search(l)
        d = path.dirname(m.group(1))
        b = path.basename(file)
        p = path.abspath(path.join(d, file+'.py'))
    if path.exists(p):
        if p not in included_files:
            included_files.add(p)
            ldr = find_loader(b, p)
            ldr.load_module()
    else:
        raise Exception("cannot find " + file)


def current_dir():
    """return current directory"""
    l = str(traceback.extract_stack()[-2])
    r = re.compile('file (\S+),')
    m = r.search(l)
    d = path.dirname(m.group(1))
    return d
