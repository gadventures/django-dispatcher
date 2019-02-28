from dispatcher import Transition

NEW = 'new'

class BaseTransition(Transition):
    def is_valid(self, data):
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
