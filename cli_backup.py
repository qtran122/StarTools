'''
Command-Line Tool for TODO
	
USAGE EXAMPLE:
    cd /Users/Jimmy/20-GitHub/StarTools
	clear; python cli_backup.py z01 --v 2

	python cli_backup.py z01 --v 0
	python cli_backup.py all --v 0 --name ZIP_SPECIFIED_NAME
	python cli_backup.py z01 --rewind --v 0
	python cli_backup.py all --rewind --v 0

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.backup_utils as backup_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play

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
	parser.add_argument('target_lv', type=str, help = arg_help1)
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	parser.add_argument('--rewind',      action='store_true')
	parser.add_argument('--name',        type=str)
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Determine which action to perform
	is_all_levels = args.target_lv.lower() == 'all'
	filename      = args.target_lv    # Unused if is targetting all levels

	# Case 1 - Single target backup
	if not is_all_levels and not args.rewind:
		log.Must(f"Creating backup for level \"{filename}\"")
		log.Must('')
		playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(filename))
		backup_utils.CreateBackup(playdo)
		return

	# Case 2 - Single target restore
	if not is_all_levels and args.rewind:
		log.Must(f"Restoring backup for level \"{filename}\"")
		backup_utils.RestoreBackupViaName(file_utils.GetFullLevelPath(filename))
		return


	# Case 3 - Whole folder backup
	if is_all_levels and not args.rewind:
		log.Must(f"Creating backup for ALL levels")
		backup_utils.CompressAllBackupsIntoZip(args.name)
		return

	# Case 4 - Whole folder restore
	if is_all_levels and args.rewind:
		log.Must(f"Restoring backup for ALL levels")
		backup_utils.DecompressAllBackups()
		return





#--------------------------------------------------#

main()










# End of File