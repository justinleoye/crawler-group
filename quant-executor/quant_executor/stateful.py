from pyutils import *

from quant_executor import Executor, context

class StatefulExecutor(Executor):
    def __init__(self, state_saver=None):
        if state_saver is None:
            state_saver = context.get_state_saver()
        self.state_saver = state_saver

    def execute_with_state(job, state):
        #return updated state after execute
        return state

    def setup(self, job):
        #return initial state after setup
        return {}

    def before_execute(self, job):
        pass

    def after_execute(self, job):
        pass

    def get_state_by_id(self, state_id):
        return self.state_saver.get(state_id)

    def get_state_id(self, job):
        stateful = job.get('stateful')==True
        state_id = job.get('state_id')
        if not stateful:
            return None
        else:
            return state_id

    def get_state(self, job):
        restart =  job.get('restart')
        stateful = job.get('stateful')==True
        state_id = job.get('state_id')
        if not restart and stateful:
            return self.get_state_by_id(state_id)
        else:
            return None
    
    def put_state(self, job, state):
        if state is None:
            return
        stateful = job.get('stateful')==True
        state_id = job.get('state_id')
        if stateful:
            self.put_state_by_id(state_id, state)

    def put_state_by_id(self, state_id, state):
        self.state_saver[state_id] = state

    def execute(self, job):
        self.before_execute(job)

        state = self.get_state(job)
        if state is None:
            DEBUG("setup executor")
            state = self.setup(job)
        
        new_state = self.execute_with_state(job, state)
        #new_state==None means new state already saved
        self.put_state(job, new_state)

        self.after_execute(job)

