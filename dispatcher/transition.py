class Transition:

    chain = None
    _errors = None

    def __init__(self, chain, initial_context):
        self.chain = chain
        self.context = initial_context

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
    def errors(self):
        """
        This needs to be here because otherwise the errors
        keep piling on top of each other
        i.e.
        t1: self.errors.append('error 1') -> ['error 1']
        t2: self.errors.append('error 2') -> ['error 1', 'error 2']
        Lazy loading like this prevents this weird bug
        """
        if self._errors is None:
            self._errors = []
        return self._errors

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
