from xml.etree import ElementTree

class Value:
    @classmethod
    def from_element(cls, e):
        assert cls == Value, "from_element method must be overwritten in %s" % str(cls)
        for name, subcls in globals().items():
            if name.lower() == e.tag and isinstance(subcls, type) and issubclass(subcls, Value):
                return subcls.from_element(e)

        assert False, "unhandled value tag %s." % e.tag

    def to_element(self):
        assert False, "to_element method must be overwritten in %s" % str(self)


class SingletonValue(Value):
    """
    SingletonValue intends to parse the value elements who do not contain
    children, but only have a `val` field, for example

        <state_id val="1" />

    """
    @classmethod
    def from_element(cls, e):
        return cls(e.attrib['val'])

    def __init__(self, val):
        self.val = val

    def to_element(self):
        return ElementTree.Element(self.__class__.__name__.lower(), { 'val' : self.val })

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__.lower(), self.val)


class State_id(SingletonValue):
    pass

class Bool(SingletonValue):
    pass

class SingletonTextValue(Value):
    @classmethod
    def from_element(cls, e):
        return cls(e.text)

    def __init__(self, s):
        self.s = s

    def to_element(self):
        elem = ElementTree.Element(self.__class__.__name__.lower())
        elem.text = self.s
        return elem


class String(SingletonTextValue):
    pass

class Int(SingletonTextValue):
    pass

class Unit(Value):
    @classmethod
    def from_element(cls, e):
        return cls()

class Union(Value):
    @classmethod
    def from_element(cls, e):
        return cls(
                e.attrib['val'],
                *[Value.from_element(r) for r in e]
                )

    def __init__(self, val, *recs):
        assert len(recs) == 1, "a union does not support multiple records"
        self.val = val
        self.rec = recs[0]


class Pair(Value):
    @classmethod
    def from_element(cls, e):
        assert len(e.getchildren()) == 2
        return cls(
                Value.from_element(e[0]),
                Value.from_element(e[1])
                )

    def __init__(self, fst, snd):
        self.fst = fst
        self.snd = snd

    def to_element(self):
        e = ElementTree.Element(self.__class__.__name__.lower())
        e.extend([self.fst.to_element(), self.snd.to_element()])
        return e
