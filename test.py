from entity import EntityBase
from namespace import Namespace

class Suite(Namespace):

     def __init__(self, body, parent=None):
         super(Suite, self).__init__(body, parent)

def suite(parent=None):
    def f(body):
        s = Suite(body, parent)
        if parent:
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
            else:
                raise Exception('attempt to define test {} in non-suite {}'.format(body.__name__, parent))
        return t
    return f
