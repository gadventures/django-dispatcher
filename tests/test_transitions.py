import mock
from django.test import TestCase
from django.conf import settings
from dispatcher import Dispatcher
from tests.fixtures import (
    NEW,
    T1, T2, T3, T4,
)

dispatcher_config = {'chains': [{
    'chain_type': 'sample_chain',
    'transitions': {
        NEW: [T1, T2],
        T1.final_state: [T3],
        T2.final_state: [T4],
    }
}]}


class TransitionTest(TestCase):

    def test_basic_transitions(self):
        """
        Given these transitions:

            NEW: [T1, T2],
            T1.final_state: [T3],
            T2.final_state: [T4],

        Determine a full chain's progression and that the callback is called
        when a transition is validated (they always validate at this point)
        """
        dispatcher = Dispatcher(dispatcher_config)
        rsc_map = [
            ('rsc1', '123'),
            ('rsc2', '456'),
        ]
        chain = dispatcher.get_or_create_chain_from_resources('sample_chain', rsc_map)
        self.assertEqual(chain.state, NEW)

        # State is NEW, should transition to the first available transition
        cb1 = mock.Mock()
        chain.execute(callback=cb1)
        self.assertEqual(chain.state, T1.final_state)
        cb1.assert_called_once()

        # State is t1_done, should transition to t3_done
        # as per `T1.final_state: [T3]`
        cb2 = mock.Mock()
        chain.execute(callback=cb2)
        self.assertEqual(chain.state, T3.final_state)
        cb2.assert_called_once()

        # State is t3_done, should not transition, therefore should not call
        # the callback
        cb3 = mock.Mock()
        chain.execute(callback=cb3)
        self.assertEqual(chain.state, T3.final_state)
        cb3.assert_not_called()

    def test_skipped_transition(self):
        """
        Given these transitions:

            NEW: [T1, T2],
            T1.final_state: [T3],
            T2.final_state: [T4],

        Determine a full chain's progression and that the callback is called
        when a transition is validated (they always validate at this point)
        """
        # reinitialize where T1 never validates and always skips to T2
        T1.is_valid = lambda x: False
        T2.is_valid = lambda x: True
        dispatcher_config['chains'][0]['transitions'] = {
            NEW: [T1, T2],
            T1.final_state: [T3],
            T2.final_state: [T4],
        }

        dispatcher = Dispatcher(dispatcher_config)
        rsc_map = [
            ('rsc1', '123'),
            ('rsc2', '456'),
        ]
        chain = dispatcher.get_or_create_chain_from_resources('sample_chain', rsc_map)
        self.assertEqual(chain.state, NEW)

        # State is NEW, should transition to the first available transition,
        # which in this case is T2
        cb1 = mock.Mock()
        chain.execute(callback=cb1)
        self.assertEqual(chain.state, T2.final_state)
        cb1.assert_called_once()

        # State is t2_done, should transition to t4_done and the callback should be called
        cb1 = mock.Mock()
        chain.execute(callback=cb1)
        self.assertEqual(chain.state, T4.final_state)
        cb1.assert_called_once()

        # State is t2_done, should transition to t4_done and the callback should be called
        cb1 = mock.Mock()
        chain.execute(callback=cb1)
        self.assertEqual(chain.state, T4.final_state)
        cb1.assert_not_called()

    def test_never_transitions(self):
        """
        Given these transitions:

            NEW: [T1, T2],
            T1.final_state: [T3],
            T2.final_state: [T4],

        Determine a full chain's progression and that the callback is called
        when a transition is validated (they always validate at this point)
        """
        # reinitialize where T1 never validates and always skips to T2
        T1.is_valid = lambda x: False
        T2.is_valid = lambda x: False
        dispatcher_config['chains'][0]['transitions'] = {
            NEW: [T1, T2],
            T1.final_state: [T3],
            T2.final_state: [T4],
        }

        dispatcher = Dispatcher(dispatcher_config)
        rsc_map = [
            ('rsc1', '123'),
            ('rsc2', '456'),
        ]
        chain = dispatcher.get_or_create_chain_from_resources('sample_chain', rsc_map)
        self.assertEqual(chain.state, NEW)

        # State is NEW, should transition to the first available transition,
        # which in this case is T2
        cb1 = mock.Mock()
        chain.execute(callback=cb1)
        self.assertEqual(chain.state, NEW)
        cb1.assert_not_called()
