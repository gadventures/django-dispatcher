import mock
from django.test import TestCase
from django.conf import settings
from dispatcher import Dispatcher
from tests.fixtures import (
    DISPATCHER_CONFIG,
    NEW,
    T1, T2, T3, T4,
)

dispatcher = Dispatcher(DISPATCHER_CONFIG)

class DispatcherTest(TestCase):

    def test_get_chain(self):
        rsc_map = [
            ('rsc1', '123'),
            ('rsc2', '456'),
        ]
        chain1 = dispatcher.get_or_create_chain('sample_chain', rsc_map)
        self.assertEqual(len(chain1.resources.all()), 2)

        chain2 = dispatcher.get_or_create_chain('sample_chain', rsc_map)
        self.assertEqual(chain1, chain2)

        rsc_map.append(('rsc3', '789'))
        chain3 = dispatcher.get_or_create_chain('sample_chain', rsc_map)
        self.assertEqual(chain1, chain3)

    def test_basic_transitions(self):
        rsc_map = [
            ('rsc1', '123'),
            ('rsc2', '456'),
        ]
        chain = dispatcher.get_or_create_chain('sample_chain', rsc_map)
        self.assertEqual(chain.state, NEW)

        chain.execute(callback=lambda x: x)
        self.assertEqual(chain.state, T1.final_state)

        chain.execute(callback=lambda x: x)
        self.assertEqual(chain.state, T3.final_state)
