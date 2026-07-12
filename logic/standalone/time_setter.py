'''
Logic module for cli_time_setter.

USAGE EXAMPLE:
	time_setter.logic(playdo, args.new_num, do_fl, do_rl)

'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# In-editor object layers for nodes & routes
layer_name = None

# config_set = 'mult'	# Either 'set' or 'mult'
config_multiply_value = True	# If True, multiply the cycle_time by a certain factor
								# If False, set the cycle_time directly to a certain number (unused)



# Passing configurations to logic
ignore_layer_with_property = 'do_not_retime'

property_name  = 'behavior'
behavior_start = 'start_time'
behavior_cycle = 'cycle_time'

real_light_prefix = 'light_'
fake_light_prefix = 'AT'
real_light_keyword = 'UNDULATE_INTENSITY'
fake_light_keyword = 'UNDULATE_COLOR'

edited_object = []





#--------------------------------------------------#
'''Public Functions'''

def logic(playdo, new_num, do_fake_light, do_real_light):
	'''Main Logic'''
	log.Must('')
	log.Must(f'Multiplying light behavior (start_time and cycle_time), by factor of {new_num}')

	# Scan through all active objectlayers to filter in objects
	list_obj = []
#	list_objectgroup = playdo.GetAllObjectgroup(is_print=False, ignore_inactive_objectgroup=True)
	list_objectgroup = playdo.GetAllObjectgroup(ignore_inactive_objectgroup=True)
	for objectgroup in list_objectgroup:
		# Ignore the whole layer if it has the "do_not_retime" property
		if tiled_utils.GetPropertyFromObject(objectgroup, ignore_layer_with_property, True) != None: continue
		for obj in objectgroup:
			obj_name = tiled_utils.GetNameFromObject(obj)
			if do_fake_light and obj_name.startswith(fake_light_prefix): list_obj.append(obj)
			if do_real_light and obj_name.startswith(real_light_prefix): list_obj.append(obj)

	# Main Logic - Check through each object's property
	has_change = False
	for obj in list_obj: _UpdateObjectsCycleTime(obj, new_num, playdo)
	has_change = ( edited_object != [] )
	log.Must(f' {len(edited_object)} objects have been changed')
	return has_change





#--------------------------------------------------#
'''Public Functions'''

def _UpdateObjectsCycleTime(obj, new_num, playdo):
	'''
	 This applies change to each individual object
	  - Does nothing if object has no "behavior" property
	  - Does nothing if property does not contain the keyword
	  - If object has no assigned start_time, set to 0 before multiplying
	  - If object has no assigned cycle_time, set to 2 before multiplying
	'''
	# If property is not in object, does nothing and return
	property_value = tiled_utils.GetPropertyFromObject(obj, property_name, False)
	if property_value == None: return

	# Parse the property for the 2 'time values'
	value_split = property_value.split(',')

	# Return if the light behavior does not contain the time-related keyword
	is_light_real = tiled_utils.GetNameFromObject(obj).startswith(real_light_prefix)
	if     is_light_real and value_split[0] != real_light_keyword: return
	if not is_light_real and value_split[0] != fake_light_keyword: return

	# Check where in the property is the start_time and cycle_time specified at
	target_start = -1
	target_cycle = -1
	for index, v in enumerate(value_split):
		if behavior_start in v: target_start = index + 1
		if behavior_cycle in v: target_cycle = index + 1

	# Update the cycle_time value
	if target_cycle >= 0:
		value_split[target_cycle] = _ApplyChangeToTime(value_split[target_cycle], new_num)
	else:
		# Special Case - No cycle is specified, set to be default value of 2
		value_split.append(behavior_cycle)
		value_split.append("2")
		value_split[-1] = _ApplyChangeToTime(value_split[-1], new_num)

	# Update the start_time value, do nothing here if not specified
	if target_start >= 0:
		value_split[target_start] = _ApplyChangeToTime(value_split[target_start], new_num)

	# Replace the property with the new value
	new_property = ",".join(value_split)
	tiled_utils.SetPropertyOnObject(obj, property_name, new_property)

	# Logging Purpose
	edited_object.append(0)
	object_name = tiled_utils.GetNameFromObject(obj)
	layer_name  = tiled_utils.GetNameFromObject( tiled_utils.GetParentObject(obj, playdo) )
	log.Info(f'  \"{object_name}\"    \"{layer_name}\"')

	if log.GetVerbosityLevel() != 2: return
	print_msg = ''
	print_msg += f'    {property_value}\n'
	print_msg += f' -> {new_property}\n'
	log.Extra(print_msg)



def _ApplyChangeToTime(old_value, new_num):
	'''
	 Return the new value as string, after reading the time value as string and applying the change
	  - Rounded to 2 decimal places automatically
	  - Changed into int automatically if there is no decimal places after rounding
	'''
	parsed_value = float(old_value)
	if config_multiply_value: parsed_value *= new_num
	else:                     parsed_value  = new_num
	parsed_value = round(parsed_value, 2)
	if parsed_value == int(parsed_value): parsed_value = int(parsed_value)
	new_value = str(parsed_value)
	return new_value





#--------------------------------------------------#










# End of File