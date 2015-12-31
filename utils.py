from os import path, read
import re, traceback

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

