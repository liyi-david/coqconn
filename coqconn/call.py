from xml.etree import ElementTree
from abc import abstractclassmethod


class Call:
    def __init__(self):
        self.conn = None

    def to_element(self):
        call_name = self.__class__.__name__
        assert call_name != 'Call', 'cannot serialize an abstract call'

        elem = ElementTree.Element('call', { 'val' : call_name})
        elem.extend(self.element_children())

        return elem

    def to_string(self):
        return ElementTree.tostring(self.to_element())


class Add(Call):
    def __init__(self, code):
        Call.__init__(self)

        self.code = code

    def element_children(self):
        return []
