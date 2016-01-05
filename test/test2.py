@namespace()
def bbb(self):

    @entity(self)
    def foo(self):
        @action(self)
        def build(self):
            yield from cmd("echo foo")

    @entity(self)
    def bar(self):
        self.need(self.parent.foo)
        @action(self)
        def build(self):
            yield from cmd("echo bar")


    @suite(self)
    def zoo(self):

        @test(self)
        def t0(self):
            self.need(self.parent.parent.bar)
            @action(self)
            def run(self):
                yield from self.build_needs()
                yield from cmd("echo t0")
