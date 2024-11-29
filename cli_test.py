'''
Command-Line Tool template when new tools are being created.
Can also be used to test features in isolation.
    
USAGE EXAMPLE:
    python cli_test.py __test --v 0

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.pattern.pattern_matcher as PM
#    import logic.standalone.x as x

#--------------------------------------------------#
'''Variables'''
# Delete section if unneeded



#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and <TBA>'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Use a playdo to read/process the XML
    pattern_root = file_utils.GetPatternRoot()
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # Main Logic
#    do_the_thing()

    # Flush changes to File!
    playdo.Write()



#--------------------------------------------------#
'''Debug Site'''
# Make sure to DELETE afterwards!!!


def disabled_code_tab():
    x = 1

def disabled_code_space():
    x = 1



def logging_test():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Use a playdo to read/process the XML
    pattern_root = file_utils.GetPatternRoot()
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))


    # Logging test 1
    msg0 = 'v0: REQUIRED level of info'
    msg1 = 'v1: Normal level of info'
    msg2 = 'v2: Extra level of info'
    log.Must(msg0)
    log.Info(msg1)
    log.Extra(msg2)


    # Logging test 2
    msg_multi = ['Line 1', 'Line 2']
    log.Must(msg_multi)


    # Logging test 3
    msg_multi2 = [1, 2]
    msg_multi3 = [[1, 2, 3], [4, 5, 6]]
    log.Must(msg_multi2)
    log.Must(msg_multi3)
#    log.print_2d(msg_multi3)





#--------------------------------------------------#

# logging_test()
main()










# End of File