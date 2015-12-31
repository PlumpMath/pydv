class Scheduler:
    
    running_q  = set()
    sleeping_q = set()

    current = None

    @classmethod
    def add(cls, v):
        cls.running_q.add(v)

    @classmethod
    def sleep(cls):
        v = cls.current
        cls.sleeping_q.add(v)
        yield

    @classmethod
    def wake(cls, v):
        if v in cls.sleeping_q:
            cls.sleeping_q.remove(v)
        cls.running_q.add(v)

    @classmethod
    def run(cls):
        while len(cls.running_q) > 0:
            v = cls.running_q.pop()
            v.resume()

