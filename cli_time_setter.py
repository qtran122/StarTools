'''
Command-Line Tool for editing properties of selected object types
More specifically, the start_time & cycle_time would be multiplied by a float

USAGE EXAMPLE:  # The following has multiply factor of 1.2
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python cli_time_setter.py z01 1.2 --fake_lights
	clear; python cli_time_setter.py z01 1.2 --real_lights
	clear; python cli_time_setter.py z01 1.2 --all_lights
	clear; python cli_time_setter.py z01 1.2 --rewind

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

arg_description = 'Process a tiled level XML and apply multiplier to start_/cycle_time in light objects property'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
	parser.add_argument('filename', type=str, help = arg_help1)
	parser.add_argument('--rewind', action='store_true')
	parser.add_argument('new_num', type=float)
	parser.add_argument('--fake_lights', action='store_true')
	parser.add_argument('--real_lights', action='store_true')
	parser.add_argument('--all_lights',  action='store_true')
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
	do_fl = args.fake_lights or args.all_lights
	do_rl = args.real_lights or args.all_lights
	if (not do_fl) and (not do_rl):
		log.Must("\nERROR! It is not specified whether to modify fake or real light objects!")
		log.Must("  Please add one of the following tags in the command:")
		log.Must("    --fake_lights")
		log.Must("    --real_lights")
		log.Must("    --all_lights")
		log.Must("")
		return
	if args.new_num == 1:
		log.Must("\nERROR! Please specify a multiplier greater than 0 and is not 1!")
		return
	has_change = time_setter.logic(playdo, args.new_num, do_fl, do_rl)

	# Flush changes to File!
	if not has_change: return    # Do not apply edit if no change has been made
	playdo.Write(make_auto_backup=True)





#--------------------------------------------------#

main()










# End of File