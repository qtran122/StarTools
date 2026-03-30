'''
Logic module that can
 - TBA


USAGE EXAMPLE:
    raw_dict = conflict.CheckConflicts(playdo, _LIST_LIGHTING_OBJ)
    pruned_dict = conflict.PruneConflicts(playdo, conflict_dictionary)
    conflict.FixConflicts(playdo, pruned_dict)
'''

import os
import datetime
import shutil
from pathlib import Path
import logic.common.log_utils as log
import logic.common.file_utils as file_utils

#--------------------------------------------------#
'''Variables'''

# Output
_output_folder1 = "output/"
_output_folder2 = _output_folder1 + "levels/"
_output_file    = _output_folder1 + "_merged.txt"

EXTENSION = '.xml'
SPLIT_CHAR = '-'

MAX_BACKUP_PER_FILE = 4    # Number of backups for any specific level





#--------------------------------------------------#
'''Public Functions'''

def CreateBackup(playdo):
	'''
	 TODO
	 Note that the file backup is BEFORE applying the changes
	'''
	# File name
	folder_path = _GetBackupFolder()
	level_path = playdo.full_file_name
	level_name = file_utils.StripFilename(level_path)
	curr_date = f'{SPLIT_CHAR}{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
	backup_path = f'{folder_path}/{level_name}{curr_date}{EXTENSION}'

	# Copy file
	log.Extra(f' Creating backup at \"{backup_path}\"...')
	shutil.copy2(level_path, backup_path)

	# Delete oldest file if limit is exceeded
	list_backup_lane = _GetBackupList(playdo)
	if len(list_backup_lane) > MAX_BACKUP_PER_FILE:
		oldest_filename = f'{folder_path}/{list_backup_lane[0]}'
		log.Extra(f'  Deleting OLDEST backup at \"{oldest_filename}\"')
		os.remove(oldest_filename)
	log.Extra('')



def RestoreBackup(playdo, restore_newest = True):
	'''TODO'''
	# Check through the folder to find the backups
	list_backup_lane = _GetBackupList(playdo)
	if len(list_backup_lane) <= 0: log.Must(f'ERROR! No backup found!'); return

	# Find the newest / oldest backup available
	folder_path = _GetBackupFolder()
	backup_path = list_backup_lane[-1]
	if not restore_newest: backup_path = list_backup_lane[0]
	backup_path = f'{folder_path}/{backup_path}'

	# Copy backup to real directory
	level_path = playdo.full_file_name
	log.Must(f' Restoring {"NEWEST" if restore_newest else "OLDEST"} backup')
	log.Must(f'  from {backup_path}')
	log.Must(f'  to   {level_path}')
	log.Must('')
	shutil.copy2(backup_path, level_path)



def _GetBackupFolder():
	folder_path = Path( file_utils.GetInputFolder() )
	folder_path = folder_path.parent
	folder_path /= 'backup/'    # This adds the folder to the directory
	return folder_path

def _GetBackupList(playdo):
	'''TODO'''
	# Get variables
	list_backup_lane = []
	folder_path = _GetBackupFolder()
	list_all_backup = os.listdir(folder_path)
	level_path = playdo.full_file_name
	level_name = file_utils.StripFilename(level_path)

	# Check through the folder
#	print('\tDEBUG print unsorted')
	for bu_name in list_all_backup:
		if not EXTENSION in bu_name: continue
		curr_name = bu_name.split(SPLIT_CHAR)[0]
		if curr_name != level_name: continue		
		list_backup_lane.append(bu_name)
#		print(f'\t {bu_name}')
	list_backup_lane = sorted(list_backup_lane)    # Sorted by date
#	print('\tDEBUG\n')
	return list_backup_lane



#--------------------------------------------------#





#--------------------------------------------------#










# End of File