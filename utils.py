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
        b = path.basename(file)
        p = path.abspath(path.join(file+'.py'))
    else:
        l = str(traceback.extract_stack()[-1][0])
        #r = re.compile('file (\S+),')
        #m = r.search(l)
        d = path.dirname(l) #m.group(1))
        b = path.basename(file)
        p = path.abspath(path.join(d, file+'.py'))
    if path.exists(p):
        if p not in included_files:
            included_files.add(p)
            #ldr = find_loader(b, p)
            #ldr.load_module()
            f = open(p)
            c = f.read()
            o = compile(c, p, 'exec')
            exec(o, ns, ns)
    else:
        raise Exception("cannot find " + file)

def get_level(level):
    mapping = {'1' : logging.DEBUG,
               '2' : logging.INFO,
               '3' : logging.WARNING,
               '4' : logging.ERROR,
               '5' : logging.CRITICAL}
    if level in mapping:
        return mapping[level]
    else:
        raise Exception('unsupported verbose level ' + level)

