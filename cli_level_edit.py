'''
Command-Line Tool for testing features in isolation.
Can also be used as template for creating new files
	
USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python cli_level_edit.py --v 1
	clear; python /Users/Jimmy/20-GitHub/StarTools/cli_level_edit.py --v 1

'''
import argparse
import toml
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.level_edit as level_edit

#--------------------------------------------------#
'''Adjustable Configurations'''

# In-editor object layers for nodes & routes
curr_toml = 'level_edit-remove_example'
curr_toml = 'level_edit-sample'
EXTENSION = '.toml'

KEY_TARGET = 'TARGET_LEVEL_FILES'
KEY_ACTION = 'ACTION'    # Make sure it's the same in the logic file




#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and <TBA>'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Read TOML
	toml_path = curr_toml
	if not EXTENSION in toml_path: toml_path += EXTENSION
	toml_path = file_utils.GetInputFolder() + toml_path
	dict_config = toml.load(toml_path)

	# Get the list of playdo that needs changing
	list_paths = []
	target_list = dict_config[KEY_TARGET]
	if target_list[0].lower().startswith('all'):
		list_paths = file_utils.GetAllLevelFiles(True)
		target_list = "ALL Levels"
	else:
		for target in target_list:
			list_paths.append(file_utils.GetFullLevelPath(target))

	# Informs user of the main action	
	do_action = dict_config['ACTION']
	action_name = do_action[0]
	log.Must(f'Tool will perform \"{action_name}\" to {target_list}')
	if target_list == "ALL Levels": log.Must(' Note that this tool would not check inside auto-tiling folders')
	log.Info('')

    # Filter objects, then perform the action
	list_playdo = []
	for full_path in list_paths:
		playdo = play.LevelPlayDo(full_path)
		list_obj = level_edit.FilterObjects(playdo, dict_config)
		if len(list_obj) == 0: continue
		level_edit.PerformAction(playdo, list_obj, do_action)
		list_playdo.append(playdo)

	# Confirm actions with the user first before committing to changes
	log.Info('')
	user_input = input(f"  Commit to changes? (Y/N) ")
	if user_input[0].lower() != 'y': log.Info(''); return
	for playdo in list_playdo: playdo.Write()

	log.Info('')
	log.Info(' ~~All Procedures Completed~~')
	log.Info('')




#--------------------------------------------------#

main()










# End of File