import json
import requests
import logging
from constants import NEW


class Dispatcher:

    chain = None
    _config_keys = ('chain_type', 'transitions')

    def __init__(self, chain_config):
        self.config = chain_config

    def _get_config(self, chain_type):
        return next((
            _config for _config in self.config.get('chains')
            if _config.get('chain_type') == chain_type
        ), None)


    def _clean_rsc_map(self, rsc_map):
        for r_type, r_id in rsc_map:
            if not (isinstance(r_type, str) or isinstance(r_id, unicode)):
                raise ValueError('Invalid resource_type. Use str')

            if not (isinstance(r_id, str) or isinstance(r_id, unicode)):
                raise ValueError('Invalid resource_id. Use str')

    def get_or_create_resource_chain(self, chain_type, rsc_mappings, can_be_subset=False):
        """
        Args:
            chain_type: type of chain as listed in `self.config`
            rsc_mappings: list of resource_type, resource_id tuple combos
                [
                    (resource_type1, resource_id1),
                    (resource_type1, resource_id2),
                ]
            can_be_subset: the matching algorithm
                Given this rsc map

                 [
                    (rsc_type1, rsc_id1)
                 ]

                And these resources:

                [
                    {
                        'resource_type': 'rsc_type1',
                        'resource_id': 'rsc_id1'
                    },
                    {
                        'resource_type': 'rsc_type2',
                        'resource_id': 'rsc_id2'
                    }
                ]

                if can_be_subset = True
                    the chain will match because chain.resources contains all
                    the resources passed in the rsc_mappings
                if can_be_subset = False
                    the chain will not match because chain.resources contains
                    resources the rsc_map does not contain
        """
        from .models import Chain, ChainResource

        config = self._get_config(chain_type)

        if not config:
            raise ValueError("Couldn't find a configuration for chain_type: %s" % chain_type)

        self._clean_rsc_map(rsc_mappings)

        # this is an attempt at an AND statement with
        # a variety related objects (chain resources)
        # We want to find a chain that has all the resources
        # present (if more resources, we don't care)
        found_chains = {}
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

        # there's a silly thing where tuples, when singular,
        # have a trailing ',', stringifying to '((),)', which
        # is invalid for postgres lookups
        # it only happens when there's only one argument, but it's
        # safe to always remove it
        sql_args = tuple((str(rsc_type), str(rsc_id)) for rsc_type, rsc_id in rsc_mappings)
        sql_args_str = str(sql_args).replace('),)', '))')

        provided_rsc_set = set(rsc_mappings)
        chains = Chain.objects.raw(query % sql_args_str)
        for chain in chains:
            chain_rsc_set = {
                (rsc.resource_type, rsc.resource_id)
                for rsc in chain.resources.all()
            }

            # compare only exactly the specified resources
            logging.info('Resources provided %s | resources found %s', provided_rsc_set, chain_rsc_set)
            logging.info('Exact match %s', chain_rsc_set == provided_rsc_set)
            if can_be_subset is False and chain_rsc_set == provided_rsc_set:
                found_chains.append(chain)

            # the resource provided can be a subset, but all the
            # provided ones have to be present
            logging.info('Subset result %s', not provided_rsc_set - chain_rsc_set)
            if can_be_subset and not provided_rsc_set - chain_rsc_set:
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
