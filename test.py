from entity import EntityBase

class Test(EntityBase):

     def __init__(self, body, parent=None):
         super(Test, self).__init__(body, parent)

def test(parent=None):
    def f(body):
        t = Test(body, parent)
        if parent:
            parent.add(body.__name__, t)
        return t
    return f
