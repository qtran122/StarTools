'''
Command-Line Tool for drawing sentences in tilelayer based on object property.
	
USAGE EXAMPLE:
	python cli_text2tile.py _text2tile --v 1
	clear; python cli_text2tile.py _text2tile --v 1

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.text2tile as main_logic

#--------------------------------------------------#
'''Adjustable Configurations'''

# In-editor layer and object names
layer_name_text      = "_text_notes"
layer_name_export    = "fg_text2tile"
object_name          = "TEXT_TO_TILES"
property_name_string = "txt2tile_content"





# Passing configurations to logic
passed_arguments = (
	layer_name_text, 
	layer_name_export,
	object_name,
	property_name_string
)





#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML'
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
	main_logic.logic(playdo, passed_arguments)

	# Flush changes to File!
	playdo.Write()





#--------------------------------------------------#

main()










# End of File