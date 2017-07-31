import loggerator

logger = loggerator.getLoggerator('error')


class CliException(Exception):

    def __init__(self, theModule, theMessage, theExcMessage=None, *args, **kwargs):
        logger.error("[{}] {} {}".format(theModule,
                                         '<{}>'.format(theExcMessage) if theExcMessage else '',
                                         theMessage))
        super(CliException, self).__init__(theMessage, *args, **kwargs)
