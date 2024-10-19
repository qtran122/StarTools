'''
Command-Line Tool template when new tools are being created.
Can also be used to test features in isolation.
    
USAGE EXAMPLE:
    python cli_scroll.py _scroll --v 2

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.pattern.pattern_matcher as PM
import logic.standalone.scroll_adder as scroll_adder

#--------------------------------------------------#
'''Variables'''
# Delete section if unneeded

input_layer = '_scroll'			# PREFIX of the tilelayer, scroll values specified here
					# e.g. _scroll, _scroll_0.1, _scroll_0.1_-0.2
output_layer = '_bg/fx'
default_values = (0, 0, 0, 0)		# scroll_x, scroll_y, add_x, add_y



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
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # Main Logic
    scroll_adder.AddScroll(playdo, input_layer, output_layer, default_values)

    # Flush changes to File!
    playdo.Write()



#--------------------------------------------------#

main()










# End of File