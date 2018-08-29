
class Transition:

    errors = []

    def __init__(self, resources):
        self.resources = resources

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
