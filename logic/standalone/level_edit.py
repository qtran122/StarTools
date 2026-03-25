'''
Logic module that can
 - TBA

USAGE EXAMPLE:
    raw_dict = conflict.CheckConflicts(playdo, _LIST_LIGHTING_OBJ)
    pruned_dict = conflict.PruneConflicts(playdo, conflict_dictionary)
    conflict.FixConflicts(playdo, pruned_dict)
'''

import os
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils
import logic.common.file_utils as file_utils

#--------------------------------------------------#
'''Variables'''

# Valid keys
KEY_ACTIVE    = 'TARGET_ACTIVE_OBJECT_LAYERS_ONLY'
KEY_I_NAME    = 'TARGET_OBJECTS_WITH_NAME'
KEY_I_PROP    = 'TARGET_OBJECTS_WITH_PROPERTY'
KEY_I_PARENT  = 'TARGET_OBJECTGROUP_WITH_THESE_WORDS'

KEY_E_NAME    = 'IGNORE_FILTER_OBJ_NAME'
KEY_E_PARENT  = 'IGNORE_OBJECTGROUP_WITH_THESE_WORDS'

# Keys for Actions
KEY_ACTION         = 'ACTION'    # Make sure it's the same in the CLI file
ACTION_REMOVE_PROP = 'REMOVE_PROPERTY'
VALUE_PROPERTY = [ACTION_REMOVE_PROP, 'RENAME_LHS'] # If the Key is this, include the 2nd arg as property


NAMELESS = 'NAMELESS' # For when we want to specify nameless objects

has_printed_criteria = []





#--------------------------------------------------#
'''Public Functions'''

def FilterObjects(playdo, dict_config):
	'''
	 TODO
	'''
	# Checking the Inclusion and Exclusion Rules
	exclude_inactive_objectgroup = False
	exclude_name_list = []
	include_name_list = []
	exclude_parent_list = []
	include_parent_list = []
	include_prop_list = []
	for key, value in dict_config.items():
		if key == KEY_ACTIVE and value.lower() == 'true': exclude_inactive_objectgroup = True
		if key == KEY_E_NAME: exclude_name_list = value
		if key == KEY_I_NAME: include_name_list = value
		if key == KEY_I_PROP: include_prop_list = value
		if key == KEY_E_PARENT: exclude_parent_list = value
		if key == KEY_I_PARENT: include_parent_list = value
	for key, value in dict_config.items():
		if key == KEY_ACTION:
			if value[0] in VALUE_PROPERTY:
				for prop in value[1:]: include_prop_list.append(prop)

	# Only log all the rules in the first time
	if len(has_printed_criteria) == 0:
		log.Extra('')
		log.Must('-----')
		log.Must(f' Action : {dict_config[KEY_ACTION]}')

		log.Extra('')
		log.Must(' Checking Inclusion Rules...')
		log.Must(                                 f'  Include non-active objects      : {not exclude_inactive_objectgroup}')
		if len(include_name_list)   > 0: log.Must(f'  Include Objects with Name       : {include_name_list}')
		if len(include_prop_list)   > 0: log.Must(f'  Include Objects with Property   : {include_prop_list}')
		if len(include_parent_list) > 0: log.Must(f'  Include Objects whose Layer has : {include_parent_list}')

		log.Extra('')
		log.Must(' Checking Exclusion Rules...')
		has_ex = False
		if len(exclude_name_list)   > 0: has_ex = True; log.Must(f'  Exclude Objects with Name       : {exclude_name_list}')
		if len(exclude_parent_list) > 0: has_ex = True; log.Must(f'  Exclude Objects whose Layer has : {exclude_parent_list}')
		if not has_ex: log.Must(f'  No object will be excluded')

		log.Must('-----\n')
		has_printed_criteria.append("x")

	# Fetch all objects from playdo, then log the total number
	list_obj = []
	all_obj = playdo.GetAllObjects(False)
	for obj in all_obj:
		# Get variables
		obj_name = obj.get('name')
		parent_name = tiled_utils.GetParentObject(obj, playdo).get('name')
		has_property = False

		# Check name
		if include_name_list != []:
			if obj_name in include_name_list: dummy()
			elif NAMELESS in include_name_list and obj_name == None: dummy()
			else: continue
		if obj_name in exclude_name_list: continue
		if NAMELESS in exclude_name_list and obj_name == None: continue

		# Check property
		if include_prop_list != []:
			has_property = False
			for property in include_prop_list:
				property_value = tiled_utils.GetPropertyFromObject(obj, property, True)
				if property_value != None: has_property = True
			if has_property == False: continue

		# Check parent name
		if include_parent_list != []:
			if not any(substring in parent_name for substring in include_parent_list): continue
		if any(substring in parent_name for substring in exclude_parent_list): continue
#		if parent_name in exclude_parent_list: continue

		# The objects that pass all checks would be appended to list
		list_obj.append(obj)

	# Summary log
	filtered_num = len(list_obj)
	full_num = len(all_obj)
	if filtered_num != 0:
		log.Info('')
		level_name = file_utils.StripFilename(playdo.full_file_name)
		if log.GetVerbosityLevel() >= 1:
			log.Must(f' {filtered_num} of {full_num} objects match filter criteria in \"{level_name}\"')
		else:
			log.Must(f' {level_name}:    \t{filtered_num} matches')
#	else:
#		log.Must(f' None of the {full_num} objects match filter criteria in \"{name}\"')

	return list_obj





#--------------------------------------------------#
'''Actions'''

def PerformAction(playdo, list_obj, do_action):
	'''
	 TODO
	'''
	count = 1
	do_print = ( log.GetVerbosityLevel() >= 1 )
	for obj in list_obj:
		# Do action
		if do_action[0] == ACTION_REMOVE_PROP:
			for property in do_action[1:]:
				tiled_utils.RemovePropertyFromObject(obj, property)


		# Skip setting the Print string if not necessary
		if not do_print: continue

		# Get variables
		obj_name = obj.get('name')
		parent_name = tiled_utils.GetParentObject(obj, playdo).get('name')

		# Set the string
		count_str = ' '
		if count < 10: count_str += ' '
		count_str += f'{count})'
		msg = f'  {count_str}  \"{parent_name}\"  \t\"{obj_name}\"'
		log.Info(msg)
		count += 1





#--------------------------------------------------#
'''Utility'''

def dummy():
	'''An Empty function that does nothing'''
	x=1



#--------------------------------------------------#










# End of File