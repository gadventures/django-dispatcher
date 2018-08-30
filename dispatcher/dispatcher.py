import json
import requests
import logging

logger = logging.getLogger(__name__)

class Dispatcher:

    chain = None
    _config_keys = ('chain_type', 'transitions')

    def __init__(self, chain_type, chain_configs, requests_by, **kwargs):
        self.requests_by = requests_by
        self.API_OPTS = kwargs.get('api_opts')
        chain_config = next((
            config
            for config in chain_configs.get('chains')
            if config.get('chain_type') == chain_type
        ), None)

        if chain_config is None:
            raise ValueError('Could not find `chains` key in config')

        for key, val in chain_config.items():
            if key in self._config_keys:
                setattr(self, key, val)

        for key in self._config_keys:
            if getattr(self, key, None) is None:
                raise ValueError('{} is required for the chain config')

    def log_event(self, action, value):
        from .models import MessageChainEvent
        event_log = MessageChainEvent(**{
            'chain': self.chain,
            'action': action,
            'value': value
        })
        event_log.save()

    def get_or_create_chain(self, resource_mappings):
        """
        Args:
            resource_mappings: list of resource_type, resource_id
                [
                    (resource_type1, resource_id1),
                    (resource_type1, resource_id2),
                ]
        """
        from .models import MessageChain, MessageChainResource
        create_chain_args = []
        for r_type, r_id in resource_mappings:

            if not (isinstance(r_type, str) or isinstance(r_id, unicode)):
                raise ValueError('Invalid resource_type. Use str')

            if not (isinstance(r_id, str) or isinstance(r_id, unicode)):
                raise ValueError('Invalid resource_id. Use str')

            chain_items = MessageChainResource.objects.filter(
                resource_type=r_type,
                resource_id=r_id
            )
            chain_item = chain_items and chain_items.first()
            if not chain_items or len(chain_items) > 1:
                create_chain_args.append({
                    'resource_type': r_type,
                    'resource_id': r_id
                })
            elif self.chain and chain_item.chain != self.chain:
                raise ValueError('Multiple chains found')
            else:
                self.chain = chain_item.chain

        if not self.chain and create_chain_args:
            self.chain = MessageChain(
                chain_type=self.chain_type,
                state=self.transitions.keys()[0],
                last_requested_by=self.requests_by,
            )
            self.chain.save()
            for rsc_dict in create_chain_args:
                chain_rsc = MessageChainResource(chain=self.chain, **rsc_dict)
                chain_rsc.save()

        return self

    def find_transition(self):
        errors = []
        for transition in self.transitions[self.chain.state]:
            transition = transition(chain=self.chain)
            if transition.is_valid():
                transition.context = transition.build_context()
                return transition
            else:
                errors += transition.errors
        raise ValueError('No valid transitions found.\n %s' % '\n'.join(errors))

    def send_api_request(self, transition):

        headers = self.API_OPTS.get('headers')
        # for message-specific info in the headers (i.e. unique identifier)
        if callable(headers):
            headers = headers(transition)

        return requests.post(
            self.API_OPTS.get('url'),
            headers=headers,
            data=json.dumps(transition.context)
        )

    def execute_chain(self, dry_run=False, callback=None, callback_kwargs=None, **kwargs):

        try:
            transition = self.find_transition()
        except Exception as e:
            logger.warning(e)
            return False
        else:
            transition = self.find_transition()

        try:
            if dry_run:
                pass
            elif callback:
                cb_kwargs = callback_kwargs or {}
                callback(transition, **cb_kwargs)
            elif self.API_OPTS:
                self.send_api_request(transition)
            else:
                raise ValueError('Nothing is configured to send anywhere.')
        except Exception as e:
            logger.error('Error executing chain: %s', e.message)
        else:
            logger.info('Transitioning to %s', transition)
            if not dry_run:
                self.chain.state = transition.final_state
                self.chain.save()
                self.log_event(
                    action='state_transition',
                    value=self.chain.state
                )
