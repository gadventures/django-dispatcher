import mock
from django.test import TestCase
from django.conf import settings
from dispatcher import Dispatcher
from tests.fixtures import (
    NEW, T1, T2, T3, T4,
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
        dispatcher = Dispatcher(dispatcher_config)
        rsc_map = [
            ('rsc1', '123'),
            ('rsc2', '456'),
        ]
        chain1 = dispatcher.get_or_create_chain_from_resources('sample_chain', rsc_map)
        self.assertEqual(len(chain1.resources.all()), 2)

        chain2 = dispatcher.get_or_create_chain_from_resources('sample_chain', rsc_map)
        self.assertEqual(chain1, chain2)

        rsc_map.append(('rsc3', '789'))
        chain3 = dispatcher.get_or_create_chain_from_resources('sample_chain', rsc_map)
        self.assertEqual(chain1, chain3)
