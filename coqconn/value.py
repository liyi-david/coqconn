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

    def to_element(self, e):
        return "<%s val=\"%s\" />" % (self.__class__.__name__.lower(), self.val)

    def __repr__(self):
        return "%s(%s)" % (self.__class__.__name__.lower(), self.val)


class State_id(SingletonValue):
    pass

