'''
Command-Line Tool for TODO
	
USAGE EXAMPLE:
    cd /Users/Jimmy/20-GitHub/StarTools
	clear; python cli_backup.py z01 --v 2

	python cli_backup.py --single z01 --v 2
	python cli_backup.py --rewind z01 --v 2
	python cli_backup.py --all --v 2
	python cli_backup.py --restore_all --v 2
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
#	parser.add_argument('filename', type=str, help = arg_help1)
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	parser.add_argument('--single',      type=str)
	parser.add_argument('--rewind',      type=str)
	parser.add_argument('--all',         action='store_true')
	parser.add_argument('--restore_all', action='store_true')
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Print ERROR if there is conflicting arguments
	count_action = 0
	if args.single:      count_action += 1
	if args.rewind:      count_action += 1
	if args.all:         count_action += 1
	if args.restore_all: count_action += 1
	if count_action != 1:
		log.Must('ERROR! Make sure to perform exactly ONE action at a time!!\n')
		return

	# Case 1 - Single target backup
	if args.single != None:
		filename = args.single
		log.Must(f"Creating backup for level \"{filename}\"")
		playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(filename))
		backup_utils.CreateBackup(playdo)
		log.Must('')
		return

	# Case 2 - Single target restore
	if args.rewind != None:
		filename = args.rewind
		log.Must(f"Restoring backup for level \"{filename}\"")
		backup_utils.RestoreBackupViaName(file_utils.GetFullLevelPath(filename))
		return


	# Case 3 - Whole folder backup
	if args.all:
		log.Must(f"Creating backup for ALL levels")
		list_paths = file_utils.GetAllLevelFiles(True)
		backup_utils.CompressAllBackupsIntoZip(list_paths)
		return

	# Case 4 - Whole folder restore
	if args.restore_all:
		log.Must(f"Restoring backup for ALL levels")
		backup_utils.DecompressAllBackups()
		return





#--------------------------------------------------#

main()










# End of File