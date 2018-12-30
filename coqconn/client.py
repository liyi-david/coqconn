from .conn import CoqConnection, CoqConnectionError
from .call import Add

class CoqClient:

    def __init__(self, coqtop=None, args=[], timeout=2):
        self.conn = CoqConnection.connect(coqtop, args, timeout)

    def add(self, code):
        self.conn.call(Add(code))
        resps = self.conn.read_until(lambda resps: resps[-1].is_value())

        v = resps[-1]
        if v.succeed():
            self.conn.state_id = v.data.fst
        else:
            pass
