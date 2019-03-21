import mock
from django.test import TestCase
from django.conf import settings
from dispatcher.dispatcher import Dispatcher
from dispatcher.models import ChainResource
from dispatcher.constants import NEW, DONE
from tests.fixtures import (
    T1, T2, T3, T4
)

dispatcher_config = {'chains': [{
    'chain_type': 'sample_chain',
    'transitions': {
        NEW: [T1, T2],
        T1.final_state: [T3],
        T2.final_state: [T4],
    }
}]}


class DispatcherTest(TestCase):

    def test_get_chain(self):

        dispatcher = Dispatcher({'chains': [{
            'chain_type': 'sample_chain',
            'transitions': {
                NEW: [T1, T2],
                T1.final_state: [T3],
                T2.final_state: [T4],
            }
        }]})
        rsc_map = [
            ('rsc1', '123'),
            ('rsc2', '456'),
        ]
        chain1 = dispatcher.get_or_create_resource_chain('sample_chain', rsc_map)
        self.assertEqual(len(chain1.resources.all()), 2)

        chain2 = dispatcher.get_or_create_resource_chain('sample_chain', rsc_map)
        self.assertEqual(chain1, chain2)

        # if there are more resources on the chain, but only 2 are specified in the
        # rsc_map, ignore the unmentioned resources and do an AND statement on the
        # specified resources
        ChainResource.objects.create(chain=chain2, resource_type='rsc2', resource_id='101')
        chain2 = dispatcher.get_or_create_resource_chain('sample_chain', rsc_map)
        self.assertEqual(chain1, chain2)

        # Add an additional resource lookup. This new lookup should create a new chain
        rsc_map.append(('rsc3', '789'))
        chain3 = dispatcher.get_or_create_resource_chain('sample_chain', rsc_map)
        self.assertNotEqual(chain1, chain3)

        # Since the resource was created on chain1, now the same lookup will work
        # as it has all three matching resources
        ChainResource.objects.create(chain=chain1, resource_type='rsc3', resource_id='789')
        chain4 = dispatcher.get_or_create_resource_chain('sample_chain', rsc_map)
        self.assertEqual(chain1, chain4)
