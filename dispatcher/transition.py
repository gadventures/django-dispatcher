class Transition:

    def __init__(self, chain, initial_context=None):
        self.chain = chain
        self.errors = []
        self.context = dict(
            initial_context or {},
            **getattr(self, 'initial_context', {}),
        )

    def __str__(self):
        return '<{}>'.format(
            self.__class__.__name__,
        )

    def __repr__(self):
        return '<{}: {}>'.format(
            self.__class__.__name__,
            self.final_state
        )

    @property
    def final_state(self):
        raise NotImplementedError('Transition has no `final_state` attr')

    def is_valid(self):
        raise NotImplementedError('%s has no `is_valid` function' % self)

    def to_dict(self):
        return {
            'errors': self.errors,
            'context': self.context,
            'final_state': self.final_state,
        }
