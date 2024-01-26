''' Command-Line Tool for testing features in isolation.
    
    <SUMMARY>
     ...

    <USAGE>

cd /Users/Jimmy/20-GitHub/StarTools
python cli_test.py __test.xml --v 0


'''
import argparse
import logging
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.pattern.pattern_matcher as PM

#--------------------------------------------------#
'''Main'''

def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description='Process a tiled level XML and add BB + reef objects to a "_BB" layer.')
    parser.add_argument('filename', type=str, help='Name of the tiled level XML to add BB & reef objects to')
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
    args = parser.parse_args()


    # Set logger configurations
    # TODO also generate txt file for logging?
    logger = logging.getLogger()
    if args.v == 0: logger.setLevel(logging.CRITICAL)
    if args.v == 1: logger.setLevel(logging.INFO)
    if args.v == 2: logger.setLevel(logging.DEBUG)


    # File-specific functions
    x = 1
#    y = 1
    logging.debug('\t---Detailed---')
    logging.info('\t---Normal---')


    # Indicate all procedures have been executed successfully
    logger.setLevel(logging.INFO)
    logging.info('\tcli_collide ran successfully!')

main()



#--------------------------------------------------#
'''Trash Site'''

def disabled_code():
    '''
         0 NOTSET
        10 DEBUG
        20 INFO
        30 WARNING
        40 ERROR
        50 CRITICAL
    '''



    '''
    if args.v == 0: logging.basicConfig(level=logging.INFO)
    if args.v == 1: logging.basicConfig(level=logging.WARNING)
    if args.v == 2: logging.basicConfig(level=logging.DEBUG)
    '''


#    print(args.v)


    # Use a playdo to read/process the XML
    pattern_root = file_utils.GetPatternRoot()
    playdo = play.LevelPlayDo(file_utils.GetLevelRoot() + args.filename)


    # Flush changes to File!
    playdo.Write()







#--------------------------------------------------#










# End of File