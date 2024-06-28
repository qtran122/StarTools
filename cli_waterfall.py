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

DEFAULT_SORT = "fg_tiles,15"




#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and generate object layers with waterfalls'
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

    # Main Logic - Process
#    waterfall.SetDefaultValues(DEFAULT_SORT, DEFAULT_COLOR)
    list_meta_data = waterfall.GetMetaDataFromBlockout(playdo)
    list_waterfall = waterfall.ScanForWaterFalls(list_meta_data)
    waterfall.CreateWaterfalls(playdo, list_meta_data, list_waterfall)

    # Flush changes to File!
    playdo.Write()



#--------------------------------------------------#

main()










# End of File