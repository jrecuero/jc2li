import loggerator

logger = loggerator.getLoggerator('error')


class CliException(Exception):
    """CliException class is the base class for any exception to be raised by the application.
    """

    def __init__(self, theModule, theMessage, theExcMessage=None, *args, **kwargs):
        """CliException class initialization method.

        Args:
            theModule (str) : Module raising the exception.
            theMessage (str) : Message with the exception information.
            theExcMessage (str) : System exception that caused this app exception.
        """
        logger.error("[{}] {} {}".format(theModule,
                                         '<{}>'.format(theExcMessage) if theExcMessage else '',
                                         theMessage))
        super(CliException, self).__init__(theMessage, *args, **kwargs)
        self.message = theMessage
