'''
Utility functions for printing and logging

Verbosity level is usually first set in CLI file once during initialisation
Afterwards, you may use log.Info(s), log.Must(s), log.Extra(s) anywhere you need


USAGE EXAMPLE:
    import logic.common.utils_log as log
    log.SetVerbosityLevel(1)
    log.Info('Hello World!')

'''

import os
import logging
import logic.common.file_utils as file_utils

#--------------------------------------------------#
'''Logger Settings'''

DEFAULT_FILENAME = 'logfile.log'
DEFAULT_FORMAT = '%(message)s'   # Without extra indentation
DEFAULT_DIVIDER = '--------------------------------------------------'

FOLDER_PATH = 'reference/log/'



#--------------------------------------------------#
'''Configuration'''

def SetVerbosityLevel(log_lv_num, file_name = DEFAULT_FILENAME, format = DEFAULT_FORMAT ):
    '''Set basic configuration to logger'''
    log_level = logging.WARNING # Default to Warning
    if log_lv_num == 1: log_level = logging.INFO
    elif log_lv_num == 2: log_level = logging.DEBUG

    # Create a custom logger
    logger = logging.getLogger()
    logger.setLevel(log_level) # Set the minimum logging level

    # Create a stream handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(logging.Formatter(format))
    logger.addHandler(console_handler)    # Moved higher since MakeDir() uses logging

    # Create a file handler to log messages to a file
    file_utils.EnsureFolderExists(FOLDER_PATH)
    file_handler = logging.FileHandler(FOLDER_PATH+file_name, 'w')
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(format))
    logger.addHandler(file_handler)

    # Include header strings to logged messages
    _WriteHeaderToLog(log_lv_num)



def _WriteHeaderToLog(log_lv_num):
    print_msg  = '\n' + DEFAULT_DIVIDER                 # Divider before meta data
    print_msg += '\n  ' + os.getcwd()                   # Current OS
    print_msg += '\n  Verbosity = ' + str(log_lv_num)   # Verbosity Level
    print_msg += '\n' + DEFAULT_DIVIDER + '\n'          # Divider between meta data & tool content
    # print_msg += '' # TODO DateTime
    # print_msg += '' # TODO Specification of current cli?
    logging.warning(print_msg)  # Header is logged regardless of verbosity



#--------------------------------------------------#
'''Public Functions'''

def Must(msg):
    '''Logs messages no matter the verbosity level'''
    logging.warning(msg)

def Info(msg):
    '''Logs messages when --v = 1 or 2 (normal level of verbosity)'''
    logging.info(msg)

def Extra(msg):
    '''Logs messages when --v = 2 (extra verbose)'''
    logging.debug(msg)


def GetVerbosityLevel():
    '''Return the current verbosity level'''
    if logging.root.level == logging.INFO: return 1
    elif logging.root.level == logging.DEBUG: return 2
    else: return 0



#--------------------------------------------------#










# End of File