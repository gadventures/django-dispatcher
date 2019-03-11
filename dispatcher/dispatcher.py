import json
import requests
import logging
from constants import NEW

logger = logging.getLogger(__name__)


class Dispatcher:

    chain = None
    _config_keys = ('chain_type', 'transitions')

    def __init__(self, chain_configs):
        self.configs = chain_configs

    def _clean_rsc_map(self, rsc_map):
        for r_type, r_id in rsc_map:
            if not (isinstance(r_type, str) or isinstance(r_id, unicode)):
                raise ValueError('Invalid resource_type. Use str')

            if not (isinstance(r_id, str) or isinstance(r_id, unicode)):
                raise ValueError('Invalid resource_id. Use str')

    def get_or_create_resource_chain(self, chain_type, rsc_mappings, can_be_subset=False):
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

        self._clean_rsc_map(rsc_mappings)

        # this is an attempt at an AND statement with
        # a variety related objects (chain resources)
        # We want to find a chain that has all the resources
        # present (if more resources, we don't care)
        found_chains = {}
        sql_args = tuple((str(rsc_type), str(rsc_id)) for rsc_type, rsc_id in rsc_mappings)
        query = """
        SELECT
            DISTINCT chain.*
        FROM
            dispatcher_chain chain,
            dispatcher_chainresource rsc
        WHERE
            chain.id = rsc.chain_id AND
            (rsc.resource_type, rsc.resource_id) IN %s
        """
        found_chains = []
        chains = Chain.objects.raw(query % str(sql_args))
        for chain in chains:
            rsc_mapping = {
                (rsc.resource_type, rsc.resource_id)
                for rsc in chain.resources.all()
            }
            matched = rsc_mapping & set(rsc_mappings)

            # compare only exactly the specified resources
            if can_be_subset is False and len(matched) == len(rsc_mappings):
                found_chains.append(chain)

            # the resource provided can be a subset, but all the
            # provided ones have to be present
            if can_be_subset and len(matched) >= len(rsc_mappings):
                found_chains.append(chain)

        if len(found_chains) > 1:
            raise ValueError('More than 1 chain found with %s', rsc_mappings)

        elif found_chains:
            chain = found_chains[0]

        else:
            chain = Chain(
                chain_type=chain_type,
                state=NEW,
            )
            chain.save()
            for r_type, r_id in rsc_mappings:
                chain_rsc = ChainResource(
                    chain=chain,
                    resource_type=r_type,
                    resource_id=r_id,
                )
                chain_rsc.save()

        chain.transitions = config.get('transitions')

        return chain
