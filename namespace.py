
class Namespace:

    def __init__(self, body, parent=None):
        self.name = body.__name__
        self.fullname = self.name
        if parent:
            self.fullname = str(parent) + '.' + self.name
        self.body = body
        self.parent = parent
        self.initialized = False

    def __call__(self):
        self.initialize()
        return self

    def __str__(self):
        return self.fullname

    def initialize(self):
        if not self.initialized:
            self.initialized = True
            self.body(self)

    def add(self, name, body):
        self.__dict__[name] = body
        return body

def component(parent=None):
    def f(body):
        comp = Namespace(body, parent)
        if parent:
            parent.add(body.__name__, comp)
        return comp
    return f 

def suite(parent=None):
    def f(body):
        s = Namespace(body, parent)
        if parent:
            parent.add(body.__name__, s)
        return s
    return f
