'''
Command-Line Tool for creating waterfalls, based on input tiles and its tilelayer name.
    
USAGE EXAMPLE:
    python cli_waterfall.py _waterfall_example --v 2

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.waterfall as waterfall

#--------------------------------------------------#
'''Variables'''

WATERFALL_TEMPLATE = "waterfalls.xml"




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
    template_filepath = file_utils.GetTemplateRoot() + WATERFALL_TEMPLATE
    playdo_template = play.LevelPlayDo(template_filepath)
    if playdo_template == None : return

    # Use a playdo to read/process the XML
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # Main Logic - Process
    list_waterfall = waterfall.ScanForWaterFalls(playdo)
    waterfall.CreateWaterfalls(playdo_template, playdo, list_waterfall)

    # Flush changes to File!
    log.Extra("")
    playdo.Write()



#--------------------------------------------------#

main()










# End of File