
class Namespace:

    suites = {}

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
            if type(parent) == Namespace:
                 parent.add(body.__name__, comp)
            else:
                 raise Exception('attempt to define component {} in non-component {}'.format(body.__name__, parent))
        return comp
    return f 

