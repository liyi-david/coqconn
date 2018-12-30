from xml.etree import ElementTree
from abc import abstractclassmethod

from .value import Pair, String, Bool, Int


class Call:
    def __init__(self):
        self.conn = None

    def to_element(self):
        call_name = self.__class__.__name__
        assert call_name != 'Call', 'cannot serialize an abstract call'

        elem = ElementTree.Element('call', { 'val' : call_name})
        elem.extend([self.element_children()])

        return elem

    def to_string(self):
        return ElementTree.tostring(self.to_element())


class Add(Call):
    def __init__(self, code):
        Call.__init__(self)

        self.code = code

    def element_children(self):
        return Pair(
                Pair(
                    # s, the code to add
                    String(self.code),
                    # edit_id, an integer which is SUPPOSED to be equal to state_id
                    Int(self.conn.state_id.val)
                    ),
                Pair(
                    # state id
                    self.conn.state_id,
                    # verbose or not
                    Bool("true")
                    )
                ).to_element()
