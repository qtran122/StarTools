'''
Command-Line Tool for testing features in isolation.
Can also be used as template for creating new files
	
USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python cli_time_setter.py z01 1.2 --fake_light --v 2
	clear; python cli_time_setter.py z01 1.2 --real_light --v 2
	clear; python cli_time_setter.py z01 1.2 --all_light --v 2

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.backup_utils as backup_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.time_setter as time_setter

#--------------------------------------------------#
'''Adjustable Configurations'''





#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and <TBA>'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
	parser.add_argument('filename', type=str, help = arg_help1)
	parser.add_argument('--rewind', action='store_true') # TODO
	parser.add_argument('new_num', type=float, help = arg_help1)
	parser.add_argument('--fake_light', action='store_true')
	parser.add_argument('--real_light', action='store_true')
	parser.add_argument('--all_light',  action='store_true')
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
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
	do_fl = args.fake_light or args.all_light
	do_rl = args.real_light or args.all_light
	if (not do_fl) and (not do_rl):
		log.Must("\nERROR! It is not specified whether to modify fake or real light objects!")
		log.Must("  Please add one of the following tags in the command:")
		log.Must("    --fake_light")
		log.Must("    --real_light")
		log.Must("    --all_light")
		log.Must("")
		return
	has_change = time_setter.logic(playdo, args.new_num, do_fl, do_rl)

	# Flush changes to File!
	if not has_change: return    # Do not apply edit if no change has been made
	playdo.Write(make_auto_backup=True)





#--------------------------------------------------#

main()










# End of File