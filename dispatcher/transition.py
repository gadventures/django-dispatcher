
class Transition:

    errors = []
    chain = None

    def __init__(self, chain):
        self.chain = chain
        self.resources = dict([
            (rsc.resource_type, rsc.resource_id)
            for rsc in chain.chain_resources.all()
        ])

    def __repr__(self):
        return '<{}: {}>'.format(
            self.__class__.__name__,
            self.final_state
        )

    @property
    def final_state(self):
        return NotImplemented

    @property
    def context(self):
        return NotImplemented

    def build_context(self):
        return NotImplemented

    def is_valid(self):
        return NotImplemented
