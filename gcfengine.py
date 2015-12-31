
class GCFEngine:

    imp = None

    @classmethod
    def set_imp(cls, imp):
        cls.imp = imp

    @classmethod
    def spawn_agent(cls, agent_id):
        cls.imp.spawn_agent(agent_id)

    @classmethod
    def kill_agent(cls, agent_id):
        cls.imp.kill_agent(agent_id)
