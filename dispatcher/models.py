import traceback
import logging
from datetime import datetime
from django.db import models

from constants import DONE


class ChainEvent(models.Model):

    chain = models.ForeignKey('dispatcher.Chain', related_name='events')
    date_created = models.DateField(auto_now_add=True)
    action = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    requested_by = models.CharField(max_length=100)


class ChainResource(models.Model):

    chain = models.ForeignKey('dispatcher.Chain', related_name='resources')
    resource_id = models.CharField(max_length=30)
    resource_type = models.CharField(max_length=30)

    class Meta:
        unique_together = (('chain', 'resource_id', 'resource_type'), )


class Chain(models.Model):

    state = models.CharField(max_length=100)
    chain_type = models.CharField(max_length=100)
    date_created = models.DateField(auto_now_add=True)
    date_modified = models.DateField(auto_now=True)
    date_next_update = models.DateField(auto_now_add=True, null=True)
    disabled = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)

    dry_run = False
    errors = {}

    def lock(self):
        if self.is_locked is False and not self.dry_run:
            self.is_locked = True
            self.save()

    def unlock(self):
        if self.is_locked and not self.dry_run:
            self.is_locked = False
            self.save()

    def transition_to(self, new_state):
        self.state = new_state
        self.save()

    @property
    def transitions(self):
        if not self._transitions:
            raise NotImplementedError('Could not find transitions on chain')
        return self._transitions
    _transitions = None

    @transitions.setter
    def transitions(self, value):
        self._transitions = value

    def run_results(self, transition):
        self.unlock()
        return {
            'errors': self.errors,
            'dry_run': self.dry_run,
            'transition': transition and transition.to_dict(),
            'chain': {
                'id': self.pk,
                'state': self.state,
            },
        }

    def log_event(self, action, value, requested_by):
        event_log = ChainEvent(**{
            'chain': self,
            'action': action,
            'value': value,
            'requested_by': requested_by,
        })
        event_log.save()

    def find_transition(self, initial_context):
        """
        Find all the possible transitions and validate
        """
        if self.state == DONE:
            # find the transition with final_state==DONE
            return next((
                T(self, initial_context)
                for sublist in self.transitions.values()
                for T in sublist if T.final_state == DONE
            ), None)

        for Transition in self.transitions.get(self.state) or []:
            transition = Transition(self, initial_context)
            if transition.is_valid():
                return transition
            else:
                # why did it not transition
                self.errors.update({str(transition): transition.errors})

    def execute(self, **kwargs):

        # determine whether to actually transition and execute callback
        self.dry_run = kwargs.pop('dry_run', False)

        callback = kwargs.pop('callback', None)
        callback_kwargs = kwargs.pop('callback_kwargs', None)
        requested_by = kwargs.pop('requested_by', None)
        initial_context = kwargs.pop('initial_context', None)

        # this will prevent duplicate runs should any processes take a
        # long time
        if self.is_locked and not self.dry_run:
            logging.warning('Chain is locked, exiting early')
            raise ValueError('Chain is locked, exiting early')

        if self.date_next_update > datetime.today().date():
            logging.warning(
                'Chain is not scheduled to update til %s',
                self.date_next_update
            )
            raise ValueError('Chain not scheduled to update yet')

        self.lock()
        try:
            transition = self.find_transition(initial_context)
        except:
            logging.exception('Error while finding transition: %s', traceback.format_exc())
            self.unlock()
            raise Exception(traceback.format_exc())

        if not transition:
            return self.run_results(transition)

        if self.dry_run:
            logging.info('Dry run found, exiting without executing/transitioning')
            return self.run_results(transition)

        if transition.final_state == DONE:
            self.state = transition.final_state
            return self.run_results(transition)

        try:
            if hasattr(transition, 'callback'):
                cb_kwargs = callback_kwargs or {}
                logging.debug('Callback found on transition, executing with %s', cb_kwargs)
                transition.callback(**cb_kwargs)

            elif callback:
                cb_kwargs = callback_kwargs or {}
                logging.debug('Callback found, executing with %s', cb_kwargs)
                callback(transition, **cb_kwargs)

            else:
                logging.warning('Nothing configured to happen during execution')

            if getattr(transition, 'date_next_update', None):
                self.date_next_update = transition.date_next_update

            self.state = transition.final_state
            self.is_locked = False
            self.save()

            self.log_event(
                action='state_transition',
                value=self.state,
                requested_by=requested_by,
            )

            return self.run_results(transition)

        except:
            logging.exception('Error executing chain: %s', traceback.format_exc())
            self.unlock()
            raise Exception(traceback.format_exc())
