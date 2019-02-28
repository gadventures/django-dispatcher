import logging
from django.db import models

logger = logging.getLogger()


class ChainEvent(models.Model):

    chain = models.ForeignKey('dispatcher.Chain', related_name='chain_event')
    date_created = models.DateField(auto_now_add=True)
    action = models.CharField(max_length=30)
    value = models.CharField(max_length=30)
    requested_by = models.CharField(max_length=30)


class ChainResource(models.Model):

    chain = models.ForeignKey('dispatcher.Chain', related_name='resources')
    resource_id = models.CharField(max_length=30)
    resource_type = models.CharField(max_length=30)


class Chain(models.Model):

    state = models.CharField(max_length=30)
    chain_type = models.CharField(max_length=30)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    date_next_update = models.DateField(auto_now=True)
    disabled = models.NullBooleanField()
    is_locked = models.BooleanField(default=False)

    def transition_to(self, new_state):
        self.state = new_state
        self.save()

    @property
    def transitions(self):
        if not self._transitions:
            return NotImplemented
        return self._transitions
    _transitions = None

    @transitions.setter
    def transitions(self, value):
        self._transitions = value

    def log_event(self, action, value, requested_by):
        event_log = ChainEvent(**{
            'chain': self,
            'action': action,
            'value': value,
            'requested_by': requested_by,
        })
        event_log.save()

    def find_transition(self, data):
        errors = []
        for transition in self.transitions[self.state]:
            transition = transition(chain=self)
            if transition.is_valid(data):
                return transition
            else:
                errors += transition.errors
        raise ValueError('No valid transitions found.\n %s' % '\n'.join(errors))

    def execute(self, **kwargs):
        if self.is_locked:
            logger.warning('Chain is locked, exiting early')
            return

        dry_run = kwargs.pop('dry_run', False)
        callback = kwargs.pop('callback', None)
        callback_kwargs = kwargs.pop('callback_kwargs', None)
        requested_by = kwargs.pop('requested_by', None)
        request_data = kwargs.pop('request_data', None)

        self.is_locked = True
        self.save()
        try:
            transition = self.find_transition(request_data)
        except Exception as e:
            logger.warning(e)
            self.is_locked = False
            self.save()
            return

        try:
            if dry_run:
                logger.info('Dry run found, exiting without executing/transitioning')
                pass

            elif getattr(transition, 'callback', None):
                cb_kwargs = callback_kwargs or {}
                logger.debug('Callback found on transition, executing with %s', cb_kwargs)
                transition.callback(**cb_kwargs)

            elif callback:
                cb_kwargs = callback_kwargs or {}
                logger.debug('Callback found, executing with %s', cb_kwargs)
                callback(transition, **cb_kwargs)

            else:
                logger.warning('Nothing configured to happen during execution')

        except Exception as e:
            logger.exception('Error executing chain: %s', e.message)

        else:
            if not dry_run:
                logger.info('Transitioning to %s', transition)
                self.state = transition.final_state
                self.save()
                self.log_event(
                    action='state_transition',
                    value=self.state,
                    requested_by=requested_by,
                )

        self.is_locked = False
        self.save()
