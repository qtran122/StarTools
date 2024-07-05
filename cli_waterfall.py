'''
Command-Line Tool for creating new waterfalls, based on input tiles.
    
USAGE EXAMPLE:
    python cli_waterfall.py __test --v 2

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.waterfall as waterfall

#--------------------------------------------------#
'''Variables'''

WATERFALL_TEMPLATE = "patterns/waterfalls"




#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and generate object layers with waterfalls'
arg_filename = 'Name of the tiled level XML'
arg_verbosity = 'Controls the amount of info displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_filename)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_verbosity)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Read the waterfall template
    pattern_root = file_utils.GetPatternRoot()
    waterfall_template = None	# load the template from WATERFALL_TEMPLATE
#    if waterfall_template == None : return

    # Use a playdo to read/process the XML
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # Main Logic - Process
    list_waterfall = waterfall.ScanForWaterFalls(playdo)
    waterfall.CreateWaterfalls(waterfall_template, playdo, list_waterfall)

    # Flush changes to File!
#    playdo.Write()



#--------------------------------------------------#

main()










# End of File