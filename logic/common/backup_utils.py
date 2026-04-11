'''
Logic module for creating and restoring level files as backup


USAGE EXAMPLE:
    playdo.Write(make_auto_backup=True)		# Creates backup
    backup_utils.RestoreBackup(playdo)		# Restores backup
'''

import os
import datetime
import shutil
import zipfile
from pathlib import Path
import logic.common.log_utils as log
import logic.common.file_utils as file_utils

#--------------------------------------------------#
'''Variables'''

LV_EXTENSION = '.xml'
SPLIT_CHAR = '-'
MAX_BACKUP_PER_FILE = 4    # Number of backups for any specific level / ZIP of all levels

ALL_BACKUP_NAMES = 'all_levels'
ZIP_EXTENSION = '.zip'
ZIP_PREFIX = f'{ALL_BACKUP_NAMES}{SPLIT_CHAR}20' # Backups made in year 20xx




#--------------------------------------------------#
'''Public Functions'''

def CreateBackup(playdo):
	'''
	 Creates a file backup BEFORE applying the changes to playdo
	 This is called within playdo.Write(), but only when make_auto_backup is True
	'''
	# File name
	folder_path = _GetBackupFolder()
	level_path = playdo.full_file_name
	level_name = file_utils.StripFilename(level_path)
	curr_date = f'{SPLIT_CHAR}{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
	backup_path = f'{folder_path}/{level_name}{curr_date}{LV_EXTENSION}'

	# Copy file
	log.Extra(f' Creating backup at \"{backup_path}\"...')
	shutil.copy2(level_path, backup_path)

	# Delete oldest file if limit is exceeded
	list_backup_lane = _GetBackupList(level_path)
	if len(list_backup_lane) > MAX_BACKUP_PER_FILE:
		oldest_filename = f'{folder_path}/{list_backup_lane[0]}'
		log.Extra(f'  Deleting OLDEST backup at \"{oldest_filename}\"')
		os.remove(oldest_filename)
	log.Extra('')



def RestoreBackup(playdo, restore_newest = True):
	'''
	 Restores the backup level, from tool folder to the real level folder.
	 The newest file is restored by default, this means
	  the file is reverted to right before the previous command.
	'''
	# Check through the folder to find the backups
	level_path = playdo.full_file_name
	RestoreBackupViaName(level_path, restore_newest)

def RestoreBackupViaName(level_path, restore_newest = True):
	'''Use filepath as input, without going through the whole playdo'''
	list_backup_lane = _GetBackupList(level_path)
	if len(list_backup_lane) <= 0: log.Must(f'ERROR! No backup found!'); return

	# Find the newest / oldest backup available
	folder_path = _GetBackupFolder()
	backup_path = list_backup_lane[-1]
	if not restore_newest: backup_path = list_backup_lane[0]
	backup_path = f'{folder_path}/{backup_path}'

	# Copy backup to real directory
	log.Must(f' Restoring {"NEWEST" if restore_newest else "OLDEST"} backup')
	log.Must(f'  from {backup_path}')
	log.Must(f'  to   {level_path}')
	log.Must('')
	shutil.copy2(backup_path, level_path)





#--------------------------------------------------#
'''ZIP-ing Functions'''

def CompressAllBackupsIntoZip(specified_name):
	'''TODO'''
	list_filepath = file_utils.GetAllLevelFiles(True)
	folder_path = _GetBackupFolder().name
	zip_name = f'{ALL_BACKUP_NAMES}{SPLIT_CHAR}{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
	if specified_name == None: specified_name = ''
	else:                      specified_name = f' ({specified_name})'
	full_name = f'{folder_path}/{zip_name}{specified_name}{ZIP_EXTENSION}'
	log.Must(f" at \"{full_name}\"")
	with zipfile.ZipFile(full_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
		for filename in list_filepath:
			name_without_directory = f'{file_utils.StripFilename(filename)}{LV_EXTENSION}'
			log.Extra(f'  {name_without_directory}')
#			zipf.write(filename)
			zipf.write(filename, arcname=name_without_directory)

	# Delete oldest file if limit is exceeded
	list_zip = _GetZipList()
	if len(list_zip) > MAX_BACKUP_PER_FILE:
		oldest_filename = f'{folder_path}/{list_zip[0]}'
		log.Must(f'Deleting OLDEST backup at \"{oldest_filename}\"')
		os.remove(oldest_filename)

	log.Must('')



def DecompressAllBackups(restore_newest = True):
	'''
	 TODO
	'''
	# Read all ZIP
	list_zip = _GetZipList()
	if len(list_zip) <= 0: log.Must(f'ERROR! No backup found!'); return

	# Find the newest / oldest backup available
	folder_path = _GetBackupFolder()
	backup_path = list_zip[-1]
	if not restore_newest: backup_path = list_zip[0]
	backup_path = f'{folder_path}/{backup_path}'
	log.Must(f' at \"{backup_path}\"')

	# Extract directly to the root folder
	level_root_folder = file_utils.GetLevelRoot()
	with zipfile.ZipFile(backup_path, 'r') as zip_ref:
		zip_ref.extractall(level_root_folder)
	log.Info('')





#--------------------------------------------------#
'''Utility Functions'''

def _GetBackupFolder():
	'''Returns the path of the folder, where the backup files are kept inside the tool folder'''
	folder_path = Path( file_utils.GetInputFolder() )
	folder_path = folder_path.parent
	folder_path /= 'backup/'    # This adds the folder to the directory
	return folder_path

def _GetBackupList(level_path):
	'''
	 Returns a list of paths, leading to the backups of levels with same name as the input playdo
	  List is SORTED from oldest to newest, meaning [0] is the oldest
	'''
	# Get variables
	list_backup_lane = []
	folder_path = _GetBackupFolder()
	list_all_backup = os.listdir(folder_path)
	level_name = file_utils.StripFilename(level_path)

	# Check through the folder to filter out non-XML
	for bu_name in list_all_backup:
		if not LV_EXTENSION in bu_name: continue
		curr_name = bu_name.split(SPLIT_CHAR)[0]    # Format is "{name}-{YYMMDD}_{hhmmss}.xml"
		if curr_name != level_name: continue
		list_backup_lane.append(bu_name)
	list_backup_lane = sorted(list_backup_lane)    # Sorted by date & time
	return list_backup_lane

def _GetZipList():
	'''TODO'''
	# Get variables
	list_backup_lane = []
	folder_path = _GetBackupFolder()
	list_all_backup = os.listdir(folder_path)

	# Check through the folder to filter out non-ZIP
	for bu_name in list_all_backup:
		if not ZIP_EXTENSION in bu_name: continue
		log.Extra(f' {bu_name}')
		if not bu_name.startswith(ZIP_PREFIX):
			log.Must(f'\nERROR! File \"{bu_name}\" does not match current naming convention!')
			log.Must(' Please delete all the old ZIPs generated from previous tool versions\n')
			return []
		list_backup_lane.append(bu_name)
	list_backup_lane = sorted(list_backup_lane)    # Sorted by date & time
	return list_backup_lane




#--------------------------------------------------#





#--------------------------------------------------#










# End of File