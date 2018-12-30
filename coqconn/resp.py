from xml.etree import ElementTree

from .value import Value

class ResponseParsingError(Exception):
    pass


def parse_responses(str_elements):
    """
    in the ideal case, str_elements is a string that contains
    a set of valid xml elements, but it is not a proper xml
    string since they are not encapsulated in a root element
    """

    # encapsulate all received messages
    str_elements = "<root>" + str_elements + "</root>"
    xml = ElementTree.fromstring(str_elements)

    return list(map(Response.from_element, xml))


class Response:

    def is_feedback(self):
        return isinstance(self, Feedback)

    @classmethod
    def from_element(cls, e):
        if e.tag == "feedback":
            return Feedback.from_element(e)
        else:
            assert False, 'unhandled xml element tag %s.' % e.tag



class Feedback(Response):

    def __init__(self, state_id):
        self.state_id = state_id

    @classmethod
    def from_element(cls, e):
        assert e[0].tag == 'state_id', 'invalid feedback element that does not starts with a state_id'
        return cls(Value.from_element(e[0]))
