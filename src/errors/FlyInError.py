class FlyInError(ValueError):
    """Base exception for Fly-in.

    All project-specific exceptions inherit from this class so callers can
    catch a single common base type.
    """
    pass
