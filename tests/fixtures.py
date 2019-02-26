from dispatcher import Transition

NEW = 'new'

class BaseTransition(Transition):
    def is_valid(self):
        return True

    def build_context(self):
        return {'ok': True}


class T1(BaseTransition):
    final_state = 't1_done'

class T2(BaseTransition):
    final_state = 't2_done'


class T3(BaseTransition):
    final_state = 't3_done'


class T4(BaseTransition):
    final_state = 't4_done'


DISPATCHER_CONFIG = {
    'chains': [
        {
            'chain_type': 'sample_chain',
            'transitions': {
                NEW: [T1, T2],
                T1.final_state: [T3],
                T3.final_state: [T4],
                T2.final_state: [T4],
            }
        }
    ]
}
