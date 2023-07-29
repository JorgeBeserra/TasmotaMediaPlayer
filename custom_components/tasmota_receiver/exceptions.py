class ReceiverException(Exception):
    pass


class ReceiverUnsupportedException(Exception):
    pass


class ReceiverGroupException(ReceiverException):
    pass


class ReceiverConnectionException(ReceiverException):
    pass


class ReceiverConfigurationException(ReceiverGroupException):
    pass


class ReceiverParamException(ReceiverException):
    pass