class Transition:

    errors = []
    chain = None

    def __init__(self, chain, request_data):
        self.chain = chain
        self.context = request_data

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
