import loggerator

logger = loggerator.getLoggerator('error')


class CliException(Exception):
    """CliException class is the base class for any exception to be raised by the application.
    """

    def __init__(self, module, message, exc_message=None, *args, **kwargs):
        """CliException class initialization method.

        Args:
            module (str) : Module raising the exception.
            message (str) : Message with the exception information.
            exc_message (str) : System exception that caused this app exception.
        """
        logger.error("[{}] {} {}".format(module,
                                         '<{}>'.format(exc_message) if exc_message else '',
                                         message))
        super(CliException, self).__init__(message, *args, **kwargs)
        self.message = message
