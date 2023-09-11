class InvalidSchoolCodeError(Exception):
    """
    Raised whenever the client cannot establish a connection with the
    attempted school portal, or, the school portal has been taken offline.
    """

    pass


class HandshakeError(Exception):
    """
    Raised whenever the client cannot authenticate into the app.
    """

    pass
