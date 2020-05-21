class OiError(Exception):
    """Base exception for OpenIrrigation"""
    pass


class ZoneRegistrationException(OiError):
    """Raised when registering a new zone type fails"""
    pass
