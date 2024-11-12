'''
Command-Line Tool for testing features in isolation.
    Can also be used as template for creating new files
    
USAGE EXAMPLE:
    cd /Users/Jimmy/20-GitHub/StarTools
    python cli_test.py __test --v 0

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.aligner as aligner

#--------------------------------------------------#
'''Variables'''
# Delete section if unneeded



#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and add BB + reef objects to a "_BB" layer.'
arg_help1 = 'Name of the tiled level XML to add BB & reef objects to'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Use a playdo to read/process the XML
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # ...


    # Flush changes to File!
    playdo.Write()



#--------------------------------------------------#
'''Debug Site'''
# Make sure to DELETE afterwards!!!


def disabled_code_tab():
    x = 1

def disabled_code_space():
    x = 1





def template():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Use a playdo to read/process the XML
    pattern_root = file_utils.GetPatternRoot()
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # ...
#    do_the_thing()

    # Flush changes to File!
    playdo.Write()



#--------------------------------------------------#

main()










# End of File