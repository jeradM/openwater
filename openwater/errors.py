class OWError(Exception):
    """Base exception for OpenIrrigation"""

    pass


class ProgramException(OWError):
    """Raised by a running program"""

    pass


class ZoneException(OWError):
    """Raised by a zone"""

    pass


class ZoneRegistrationException(OWError):
    """Raised when registering a new zone type fails"""

    pass


class PluginException(OWError):
    """Raised by plugin loader/registry"""

    pass
