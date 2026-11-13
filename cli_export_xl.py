'''
Command-Line Tool for reading a simplified map XML, then creates a XLSX file at desktop
The new XLSX contains the coloring data from the XML, and can then be imported into Google Sheet
	
USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python cli_export_xl.py
'''
import argparse
import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.standalone.export_xlsx as main_logic

#---------------------------------------------------------------------#
#-------------------- [Adjustable Configurations] --------------------#

# In-editor object layers for nodes & routes
level_name_input = "map_simplified.xml"
filepath_output  =  "/Users/Jimmy/Desktop/whale_map.xlsx"      # TY's path
filepath_output  = r"C:\Users\qtran\Desktop\whale_map.xlsx"    # Quang's path





#------------------------------------------------#
#-------------------- [Main] --------------------#

arg_description = 'Process a tiled level XML and <TBA>'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Use a playdo to read/process the XML
	playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(level_name_input))
	main_logic.logic(playdo, filepath_output)





#--------------------------------------------------#

main()










# End of File