#!/usr/bin/env python

""" loggerator.py contains the loggerator utility to be used for logging debug,
warning, errors and other information from applications.


:author:    Jose Carlos Recuero
:version:   0.1
:since:     08/13/2014

"""

__docformat__ = 'restructuredtext en'

#------------------------------------------------------------------------------
#  _                            _
# (_)_ __ ___  _ __   ___  _ __| |_ ___
# | | '_ ` _ \| '_ \ / _ \| '__| __/ __|
# | | | | | | | |_) | (_) | |  | |_\__ \
# |_|_| |_| |_| .__/ \___/|_|   \__|___/
#             |_|
#------------------------------------------------------------------------------
#
# import std python modules
#
import os
import sys
import logging
import logging.config

#
# import dbase python modules
#


#------------------------------------------------------------------------------
#
#   ___ ___  _ __  ___| |_ __ _ _ __ | |_ ___
#  / __/ _ \| '_ \/ __| __/ _` | '_ \| __/ __|
# | (_| (_) | | | \__ \ || (_| | | | | |_\__ \
#  \___\___/|_| |_|___/\__\__,_|_| |_|\__|___/
#
#------------------------------------------------------------------------------
#

COL_RESET       = "\x1b[0m"
"""
    :type: string

    Clears all colors and styles (to white on black).
"""

BOLD_ON         = "\x1b[1m"
"""
    :type: string

    Bold on.
"""

ITALICS_ON      = "\x1b[3m"
"""
    :type: string

    Italics on.
"""

UNDERLINE_ON    = "\x1b[4m"
"""
    :type: string

    Underline on.
"""

INVERSE_ON      = "\x1b[7m"
"""
    :type: string

    Inverse on, reverses foreground & background colors.
"""

STRIKETHRGH_ON  = "\x1b[9m"
"""
    :type: string

    Strikethrough on.
"""

BOLD_OFF        = "\x1b[22m"
"""
    :type: string

    Bold off.
"""

ITALICS_OFF     = "\x1b[23m"
"""
    :type: string

    Italics off.
"""

UNDERLINE_OFF   = "\x1b[24m"
"""
    :type: string

    Underline off.
"""

INVERSE_OFF     = "\x1b[27m"
"""
    :type: string

    Inverse off.
"""

STRIKETHRGH_OFF = "\x1b[29m"
"""
    :type: string

    Strikethrough off.
"""


# Foreground colors are in form of 3x, background are 4x
FG_BLACK    = "\x1b[30m"
"""
    :type: string

    Set foreground color to black.
"""

FG_RED      = "\x1b[31m"
"""
    :type: string

    Set foreground color to red.
"""

FG_GREEN    = "\x1b[32m"
"""
    :type: string

    Set foreground color to green.
"""

FG_YELLOW   = "\x1b[33m"
"""
    :type: string

    Set foreground color to yellow.
"""

FG_BLUE     = "\x1b[34m"
"""
    :type: string

    Set foreground color to blue.
"""

FG_MAGENTA  = "\x1b[35m"
"""
    :type: string

    Set foreground color to magenta (purple).
"""

FG_CYAN     = "\x1b[36m"
"""
    :type: string

    Set foreground color to cyan.
"""

FG_WHITE    = "\x1b[37m"
"""
    :type: string

    Set foreground color to white.
"""

FG_DEFAULT  = "\x1b[39m"
"""
    :type: string

    Set foreground color to default (white).
"""


BG_BLACK    = "\x1b[40m"
"""
    :type: string

    Set background color to black.
"""

BG_RED      = "\x1b[41m"
"""
    :type: string

    Set background color to red.
"""

BG_GREEN    = "\x1b[42m"
"""
    :type: string

    Set background color to green.
"""

BG_YELLOW   = "\x1b[43m"
"""
    :type: string

    Set background color to yellow.
"""

BG_BLUE     = "\x1b[44m"
"""
    :type: string

    Set background color to blue.
"""

BG_MAGENTA  = "\x1b[45m"
"""
    :type: string

    Set background color to magenta (purple).
"""

BG_CYAN     = "\x1b[46m"
"""
    :type: string

    Set background color to cyan.
"""

BG_WHITE    = "\x1b[47m"
"""
    :type: string

    Set background color to white.
"""

BG_DEFAULT  = "\x1b[49m"
"""
    :type: string

    Set background color to default (black).
"""


_loggerDB = {}
"""
    :type: dict

    This module variable dictionary stores all Logger instance created, where
    the key for every instance is the component name. When the same component
    request a logger, it returns the already created instance.
"""

TRACE_LEVEL = 25
DISPLAY_LEVEL = 24


#------------------------------------------------------------------------------
#            _                     _   _
#  ___ _   _| |__  _ __ ___  _   _| |_(_)_ __   ___  ___
# / __| | | | '_ \| '__/ _ \| | | | __| | '_ \ / _ \/ __|
# \__ \ |_| | |_) | | | (_) | |_| | |_| | | | |  __/\__ \
# |___/\__,_|_.__/|_|  \___/ \__,_|\__|_|_| |_|\___||___/
#
#------------------------------------------------------------------------------
#

# ===========================================================================
def getLoggerator(name, color=(BOLD_ON + FG_BLACK)):
    """Returns the loggerator for a given component.

    It create a new loggerator to a component, if there is not any instance for
    that component. If there is an instance, it is returned.

    :type name: string
    :param name: Component name. It is used to assign a loggerator instance.

    :type color: string
    :param color: Color to display the component name.

    :rtype: loggerator instance.
    :return: Create a new loggerator instance if there is not anyone for the
        given component, or return the one previously created.
    """
    if name not in _loggerDB:
        _loggerDB[name] = Loggerator(name, color)
    return _loggerDB[name]


#------------------------------------------------------------------------------
#       _                     _       __ _       _ _   _
#   ___| | __ _ ___ ___    __| | ___ / _(_)_ __ (_) |_(_) ___  _ __  ___
#  / __| |/ _` / __/ __|  / _` |/ _ \ |_| | '_ \| | __| |/ _ \| '_ \/ __|
# | (__| | (_| \__ \__ \ | (_| |  __/  _| | | | | | |_| | (_) | | | \__ \
#  \___|_|\__,_|___/___/  \__,_|\___|_| |_|_| |_|_|\__|_|\___/|_| |_|___/
#
#------------------------------------------------------------------------------
#

#
# =============================================================================
#
class ContextFilter(logging.Filter):

    def filter(self, record):
        fr = sys._getframe(8)
        msg = '{0}::{1}::{2}'.format(os.path.basename(fr.f_code.co_filename),
                                     fr.f_code.co_name,
                                     fr.f_lineno)
        record.titular = msg
        if record.levelno == TRACE_LEVEL:
            record.levelname = 'TRACE'
        elif record.levelno == DISPLAY_LEVEL:
            record.levelname = 'DISPLAY'
        return True


#
# =============================================================================
#
class Loggerator(object):
    """Loggerator class is used to log information for a given component.

    Component name is given when Loggerator instance is created, and it will
    be reused.

    :type loggerator: logging instance
    :ivar loggerator: logging instance, which will be used to log messages.
    """

    # =========================================================================
    def __init__(self, name, color, out=sys.stdout, fname='cmd.log'):
        """Loggerator class constructor.

        Create a Loggerator instance for the component with the given name and
        using given color.

        :todo:
            New parameter with the log filename should be added. If the
            parameter is present, then log information will be sent to
            the logfile instead of to the display.

        :type name: string
        :param name: Name of the component for logging information.

        :type color: string
        :param color: String containing the color to display the component name
            in all logs.

        :type out: stdout
        :param out: standard output

        :type fname: string
        :param fname: filename for the log file
        """
        self.loggerator = logging.getLogger(name[0:15].center(16, '*'))
        self.loggerator.setLevel(logging.DEBUG)

        formatString = '%(asctime)s ' + color + '%(name)-16s ' +\
                       COL_RESET + '[%(levelname)-8s] [%(titular)-32s] %(message)s'
        formatter = logging.Formatter(formatString)

        fileHandler = logging.FileHandler(fname)
        fileHandler.setFormatter(formatter)
        self.loggerator.addHandler(fileHandler)
        self.loggerator.addFilter(ContextFilter())

        # consoleHandler = logging.StreamHandler()
        # consoleHandler.setFormatter(formatter)
        # self.loggerator.addHandler(consoleHandler)

        self.defaultColor = {}
        self.defaultColor['debug']   = (('FG', 'GREEN'), )
        self.defaultColor['info']    = (('FG', 'BLUE'), )
        self.defaultColor['trace']   = (('FG', 'MAGENTA'), )
        self.defaultColor['display']   = (('FG', 'YELLOW'), )
        self.defaultColor['warning'] = (('FG', 'RED'), )
        self.defaultColor['error']   = (('FG', 'WHITE'), ('BG', 'RED'))
        self.out = out

    # =========================================================================
    def display(self, message):
        """Display a message in the default standard output provided.

        Args:
            message (str) : string with the message to be displayed.

        Returns:
            None
        """
        self._extendedLog(message, 'display')
        self.out.write(str(message))
        self.out.write('\n')

    # =========================================================================
    def _filterLevel(self, level):
        if level in ['debug', 'info', 'warning', 'error']:
            return level
        elif level == 'trace':
            return TRACE_LEVEL
        elif level == 'display':
            return DISPLAY_LEVEL
        else:
            return logging.NOTSET

    # =========================================================================
    def _setColor(self, color):
        """ Set the color based on input list.

        It takes an input parameter, which could be a list or a string.
        If the parameter is a string, it is supposed to set as a foreground
        color.
        If the parameter is a list, it is supposed to set the foreground and/or
        background color.

        :type color: list, str
        :param color: foregorund color, or list with fore/background color.

        :rtype: str
        :return: string to be used as color for log message.
        """
        if isinstance(color, str):
            color = (('FG', color), )
        return eval('+'.join(map(lambda x: '%s_%s' % (x[0], x[1]), color)))

    # =========================================================================
    def _log(self, message, level, color=None, *args, **kwargs):
        """ Log a message with the given color.

        It logs the given message with the given color.

        :type message: string
        :param message: Debug message to be logged.

        :type color: list, str
        :param color: foregorund color, or list with fore/background color.

        :type args: list
        :param args: List of parameters.

        :type kwargs: dict
        :param kwargs: Dictionary of parameters
        """
        color = self._setColor(color)
        formattedMessage = '%s%s%s' % (color, message, COL_RESET)
        function = getattr(self.loggerator, level, None)
        if function:
            function(formattedMessage, *args, **kwargs)
        else:
            level = self._filterLevel(level)
            self.loggerator.log(level, formattedMessage, *args, **kwargs)

    # =========================================================================
    def getLoggerator(self):
        """Return the loggerator.

        :rtype: logging
        :return: Return the logging instance used for the current loggerator.
        """
        return self.loggerator

    # =========================================================================
    def _extendedLog(self, message, level, **kwargs):
        """Debug log.

        It logs a debug message.

        :type message: string
        :param message: Debug message to be logged.

        :type args: list
        :param args: List of parameters.

        :type kwargs: dict
        :param kwargs: Dictionary of parameters
        """
        color = kwargs.get('color', None)
        mode = kwargs.pop('mode', 'FG')
        extended = kwargs.pop('extended', None)
        if extended:
            useColor = extended
        elif color:
            useColor = ((mode, color), )
        else:
            useColor = self.defaultColor[level]
        kwargs['color'] = useColor
        self._log(message, level, **kwargs)

    # =========================================================================
    def debug(self, message, color=None, mode='FG', *args, **kwargs):
        """Debug log.

        It logs a debug message.

        :type message: string
        :param message: Debug message to be logged.

        :type color: list, str
        :param color: foregorund color, or list with fore/background color.

        :type args: list
        :param args: List of parameters.

        :type kwargs: dict
        :param kwargs: Dictionary of parameters
        """
        self._extendedLog(message, 'debug', color=color, mode=mode, *args, **kwargs)

    # =========================================================================
    def info(self, message, color=None, mode='FG', *args, **kwargs):
        """Information log.

        It logs an information message.

        :type message: string
        :param message: Information message to be logged.

        :type color: list, str
        :param color: foregorund color, or list with fore/background color.

        :type args: list
        :param args: List of parameters.

        :type kwargs: dict
        :param kwargs: Dictionary of parameters
        """
        self._extendedLog(message, 'info', color=color, mode=mode, *args, **kwargs)

    # =========================================================================
    def trace(self, message, color=None, mode='FG', *args, **kwargs):
        """Trace log.

        It logs a trace message.

        :type message: string
        :param message: Trace message to be logged.

        :type color: list, str
        :param color: foregorund color, or list with fore/background color.

        :type args: list
        :param args: List of parameters.

        :type kwargs: dict
        :param kwargs: Dictionary of parameters
        """
        self._extendedLog(message, 'trace', color=color, mode=mode, *args, **kwargs)

    # =========================================================================
    def warning(self, message, color=None, mode='FG', *args, **kwargs):
        """Warning log.

        It logs a warning message.

        :type message: string
        :param message: Warning message to be logged.

        :type color: list, str
        :param color: foregorund color, or list with fore/background color.

        :type args: list
        :param args: List of parameters.

        :type kwargs: dict
        :param kwargs: Dictionary of parameters
        """
        self._extendedLog(message, 'warning', color=color, mode=mode, *args, **kwargs)

    # =========================================================================
    def error(self, message, color=None, mode='FG', *args, **kwargs):
        """Error log.

        It logs an error message.

        :type message: string
        :param message: Error message to be logged.

        :type color: list, str
        :param color: foregorund color, or list with fore/background color.

        :type args: list
        :param args: List of parameters.

        :type kwargs: dict
        :param kwargs: Dictionary of parameters
        """
        self._extendedLog(message, 'error', color=color, mode=mode, *args, **kwargs)


#------------------------------------------------------------------------------
#                  _
#  _ __ ___   __ _(_)_ __
# | '_ ` _ \ / _` | | '_ \
# | | | | | | (_| | | | | |
# |_| |_| |_|\__,_|_|_| |_|
#
#------------------------------------------------------------------------------
#

if __name__ == "__main__":
    lg = Loggerator('test', FG_RED)
    lg.debug('testing')
