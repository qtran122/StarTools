'''
Logic module that can
 - TBA


USAGE EXAMPLE:

'''

import os
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# In-editor object layers for nodes & routes
layer_name = None

# config_set = 'mult'	# Either 'set' or 'mult'
config_multiply_value = True	# If True, multiply the cycle_time by a certain factor
								# If False, set the cycle_time directly to a certain number



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
	'''TODO'''
	log.Must('')
	log.Must(f'Multiplying light behavior (start_time and cycle_time), by factor of {new_num}')

	# Scan through all active objectlayers to filter in objects
	list_obj = []
#	list_objectgroup = playdo.GetAllObjectgroup(is_print=False, ignore_inactive_objectgroup=True)
	list_objectgroup = playdo.GetAllObjectgroup(ignore_inactive_objectgroup=True)
	for objectgroup in list_objectgroup:
		# Ignore if has property
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
	'''TODO'''
	# If property is not in object, does nothing and return
	property_value = tiled_utils.GetPropertyFromObject(obj, property_name, False)
	if property_value == None: return

	# Parse the property for the 2 'time values'
	value_split = property_value.split(',')

	# Return if the light behavior does not contain the time-related keyword
	is_light_real = tiled_utils.GetNameFromObject(obj).startswith(real_light_prefix)
	if     is_light_real and value_split[0] != real_light_keyword: return
	if not is_light_real and value_split[0] != fake_light_keyword: return

	# Check where the start_time and cycle_time are
	target_start = -1
	target_cycle = -1
	for index, v in enumerate(value_split):
		if behavior_start in v: target_start = index + 1
		if behavior_cycle in v: target_cycle = index + 1

	# TODO Deprecate - If both are not specified, assume the object is not applicable, so does nothing and return
#	if target_cycle < 0 and target_start < 0: return

	# Update the cycle value
	if target_cycle >= 0:
		value_split[target_cycle] = _ApplyChangeToTime(value_split[target_cycle], new_num)
	else:
		# Exception Case - No cycle is specified, set to be default value of 2
		value_split.append(behavior_cycle)
		value_split.append("2")
		value_split[-1] = _ApplyChangeToTime(value_split[-1], new_num)

	# Update the initial value, do nothing here if not specified
	if target_start >= 0:
		value_split[target_start] = _ApplyChangeToTime(value_split[target_start], new_num)

	# Set new value to property
	new_property = ",".join(value_split)
	tiled_utils.SetPropertyOnObject(obj, property_name, new_property)

	# Logging Purpose
	edited_object.append(0)
	object_name = tiled_utils.GetNameFromObject(obj)
	layer_name  = tiled_utils.GetNameFromObject( tiled_utils.GetParentObject(obj, playdo) )
	log.Info(f'  \"{object_name}\"    \"{layer_name}\"')

	if log.GetVerbosityLevel() != 2: return
#	print_msg += f'  {object_name}    {layer_name}\n'
#	print_msg += f'-----BEF-----\n'
#	print_msg += f'-----AFT-----\n'
#	print_msg += f'-------------\n'
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
'''General Utility, to be relocated?'''

def _Indent(s, min_len):
	'''Return the same string, with consistent spacing added to the end'''
	return ( s + ' ' * (min_len-len(s)) )

def _FormatNumS2TU(num_in_str):
	'''Shortcut, for converting string (coordinates measured in pixels) intoto Tiled units'''
	if num_in_str == None: return ''
	return str(int( round(float(num_in_str))/16 ))





#--------------------------------------------------#










# End of File