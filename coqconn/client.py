from .conn import CoqConnection, CoqConnectionError
from .call import Add

class CoqClient:

    def __init__(self, coqtop=None, args=[], timeout=2):
        self.conn = CoqConnection.connect(coqtop, args, timeout)

    def add(self, str_coqcode):
        self.conn.call(Add())
        self.conn.read_until(lambda _ : False)
