'''
Command-Line Tool for setting the _sort2 property values
This includes:
 - Converting old _sort to new _sort2
 - Adjusting _sort2 to not conflict with each other
 - Renaming tilelayer to include suffix of the sort values
	
USAGE EXAMPLE:
	python cli_sort2_setter.py _sort --v 0
	python cli_sort2_setter.py --v 0

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.common.log_utils as log
import logic.standalone.sort2_setter as main_logic

#--------------------------------------------------#
'''Adjustable Configurations'''

# Debug - Will be removed at the end
# level_name = "_sort 3-old"





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

	# Scan through each level in folder directory
	# TODO replace with a loop to scan through all levels in a folder
	has_error = False
	if True:
		level_name = args.filename
		playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(level_name))

		has_error = main_logic.ErrorCheckSortOrder(playdo)
		if has_error: return

		has_error = main_logic.RenameTilelayer(playdo)
		if has_error: return

		playdo.Write()

	# TODO replace object property ref here?





#--------------------------------------------------#

main()










# End of File