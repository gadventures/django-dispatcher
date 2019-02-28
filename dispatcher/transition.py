class Transition:

    errors = []
    chain = None

    def __init__(self, chain):
        self.chain = chain
        self.resources = dict([
            (rsc.resource_type, rsc.resource_id)
            for rsc in chain.resources.all()
        ])

    def __str__(self):
        return '<{}: {}>'.format(
            self.__class__.__name__,
            self.final_state
        )

    def __repr__(self):
        return '<{}: {}>'.format(
            self.__class__.__name__,
            self.final_state
        )

    @property
    def final_state(self):
        return NotImplemented

    def is_valid(self):
        return NotImplemented
