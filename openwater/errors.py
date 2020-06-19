class OWError(Exception):
    """Base exception for OpenIrrigation"""

    pass


class ProgramException(OWError):
    """Raised by a running program"""

    pass


class ProgramValidationException(ProgramException):
    """ Invalid program data, raised during save"""

    def __init__(self, msg, errors):
        super().__init__(msg)
        self.errors = errors


class ZoneException(OWError):
    """Raised by a zone"""

    pass


class ZoneRegistrationException(OWError):
    """Raised when registering a new zone type fails"""

    pass


class ZoneValidationException(OWError):
    def __init__(self, msg, errors):
        super().__init__(msg)
        self.errors = errors


class PluginException(OWError):
    """Raised by plugin loader/registry"""

    pass
