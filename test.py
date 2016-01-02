from entity import EntityBase
from namespace import Namespace

class Suite(Namespace):

    tests = {}
    suites = {}

    def __init__(self, body, parent=None):
        super(Suite, self).__init__(body, parent)

def suite(parent=None):
    def f(body):
        s = Suite(body, parent)
        if parent:
            if type(parent) == Suite:
                Suite.suites[s.fullname] = s
            if type(parent) == Namespace:
                Namespace.suites[s.fullname] = s
            parent.add(body.__name__, s)
        return s
    return f

class Test(EntityBase):

     def __init__(self, body, parent=None):
         super(Test, self).__init__(body, parent)

def test(parent=None):
    def f(body):
        t = Test(body, parent)
        if parent:
            if type(parent) == Suite:
                parent.add(body.__name__, t)
                Suite.tests[t.fullname] = t
            else:
                raise Exception('attempt to define test {} in non-suite {}'.format(body.__name__, parent))
        return t
    return f
