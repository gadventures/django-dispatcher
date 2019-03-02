import json
import requests
import logging

logger = logging.getLogger(__name__)


class Dispatcher:

    chain = None
    _config_keys = ('chain_type', 'transitions')

    def __init__(self, chain_configs):
        self.configs = chain_configs

    def get_or_create_chains_from_resources(self, chain_type, rsc_mappings):
        """
        Args:
            rsc_mappings: list of resource_type, resource_id
                [
                    (resource_type1, resource_id1),
                    (resource_type1, resource_id2),
                ]
        """
        from .models import Chain, ChainResource

        config = next((
            _config for _config in self.configs.get('chains')
            if _config.get('chain_type') == chain_type
        ), None)

        if not config:
            raise ValueError("Couldn't find a configuration for chain_type: %s" % chain_type)

        create_chain_args = []
        chains = []
        for r_type, r_id in rsc_mappings:

            if not (isinstance(r_type, str) or isinstance(r_id, unicode)):
                raise ValueError('Invalid resource_type. Use str')

            if not (isinstance(r_id, str) or isinstance(r_id, unicode)):
                raise ValueError('Invalid resource_id. Use str')

            chain_items = ChainResource.objects.filter(
                resource_type=r_type,
                resource_id=r_id,
                chain__chain_type=chain_type,
            )
            if chain_items:
                chains += [ci.chain for ci in chain_items]

        if not chains and create_chain_args:
            chain = Chain(
                chain_type=chain_type,
                state=config.get('transitions').keys()[0],
            )
            chain.save()
            for rsc_dict in create_chain_args:
                chain_rsc = ChainResource(chain=chain, **rsc_dict)
                chain_rsc.save()
            chains.append(chain)

        for chain in chains:
            chain.transitions = config.get('transitions')

        return chains
