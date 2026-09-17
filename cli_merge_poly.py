'''
Command-Line Tool for ... TBA
	
USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python cli_merge_poly.py ws1 --v 2
	clear; python cli_merge_poly.py ws1 --convex_only

'''
import argparse
import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import logic.common.backup_utils as backup_utils
import logic.common.level_playdo as play
import logic.standalone.collision as main_logic

#---------------------------------------------------------------------#
#-------------------- [Adjustable Configurations] --------------------#





#------------------------------------------------#
#-------------------- [Main] --------------------#

arg_description = 'Process a tiled level XML and <TBA>'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
	parser.add_argument('filename', type=str, help = arg_help1)
	parser.add_argument('--rewind', action='store_true')
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	parser.add_argument('--convex_only', action='store_true')
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Quick rewind
	if args.rewind:
		log.Must(f"Restoring backup for level \"{args.filename}\"")
		backup_utils.RestoreBackupViaName(file_utils.GetFullLevelPath(args.filename))
		return

	# Use a playdo to read/process the XML
	playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

	# Main Logic
	main_logic.MergePolygonsByType(playdo, args.convex_only)

	# Flush changes to File!
	playdo.Write(make_auto_backup=True)





#--------------------------------------------------#

main()










# End of File