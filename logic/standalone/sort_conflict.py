'''
Logic module that can
 - Check conflicts in objects sort value
 - Print the conflicted objects with various properties
 - (TODO) Prune the list of conflicts with only the relevant results
 - (TODO) Fix the sort values of the conflicted objects


USAGE EXAMPLE:
    raw_dict = conflict.CheckConflicts(playdo, _LIST_LIGHTING_OBJ)
    pruned_dict = conflict.PruneConflicts(playdo, conflict_dictionary)
    conflict.FixConflicts(playdo, pruned_dict)
'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# TODO delete the whole section since there is no variable/constants here




#--------------------------------------------------#
'''Public Functions'''

def OrganizeObjectsBySortVal(playdo, list_scan_obj):
	'''Given a list of all existing Tiled objects in a level, will return a dictionary:
		KEY   - the unique sort values within the level (string)
		VALUE - a list of Tiled objects that share the same sort value
	'''
	log.Info("\n--- Checking for sort value conflicts ---\n")

	# Create the dictionary with each unique sort value as keys
	sortval_to_objects_map = {}
	for scanned_obj in list_scan_obj:
		curr_obj_list = playdo.GetAllObjectsWithName(scanned_obj)
		log.Info( f'# of \"{scanned_obj}\": {len(curr_obj_list)}' )
		for obj in curr_obj_list:
			curr_string = tiled_utils.GetPropertyFromObject(obj, '_sort')
			if curr_string == None: continue  # When object does not contain `_sort`
			if curr_string == '': continue    # When property has property but no value
			curr_string = curr_string.split('.')[0]	# For checking the "fixed" sort
			if not curr_string in sortval_to_objects_map:
				sortval_to_objects_map[curr_string] = []
			sortval_to_objects_map[curr_string].append(obj)

	log.Must("\n--- Finished checking conflicts! ---\n")
	return sortval_to_objects_map



def PrintPotentialConflicts(playdo, sortval_to_objects_map, list_scan_obj):
	'''Print the dictionary that has been checked and sorted by their sort values

	playdo - The processed level
	sortval_to_objects_map - Dictonary with all sort_value as keys, and object array as values
	list_scan_obj - All applicable objects that need to have sort_values checked
	'''

	# Find the max length in object names and layer names for indentation
	max_obj_name_len = len( max(list_scan_obj, key=len) )
	max_layer_name_len = 1
	list_layer_name = []
	for obj_layer in playdo.level_root.findall('.//objectgroup'):
		name_len = len( tiled_utils.GetNameFromObject(obj_layer) )
		if max_layer_name_len < name_len: max_layer_name_len = name_len

	# Set the parent of all objects
	parent_map = {child: parent for parent in playdo.level_root.iter() for child in parent}

	# Print for each sort value
	for key_sort, list_obj in sortval_to_objects_map.items():
		log.Extra( '\n--------------------------------------------------' )
		log.Info( f"{key_sort} has {len(list_obj)} elements" )
		for obj in list_obj:
			log.Extra( f'  {MakeInfoString(obj, GetParentObjectgroupName(obj, parent_map), max_obj_name_len, max_layer_name_len)}' )
	log.Extra('\n--------------------------------------------------')
	log.Must('\n--- Finished printing conflicts! ---\n')







#--------------------------------------------------#
'''Utility'''

# Unused for now
#def _GetSort( tiled_object ):
#    return tiled_utils.GetPropertyFromObject(tiled_object, '_sort')



def GetParentObjectgroupName(curr_obj, parent_map):
	'''Find the parent object of the current object, which should be an objectgroup.
	    Then extract the name property of the parent object.
	    Finally return the name of objectgroup, after removing the "objects_" prefix
	    e.g. objects_gravity_barrier -> gravity_barrier
	'''
	return parent_map[curr_obj].get('name')[8:]



def MakeInfoString(obj, parent_layer_name, max_obj_name_len = 0, max_layer_name_len = 0):
	'''Returns a string that contains various properties of an object.
	obj - The object with info listed
	parent_layer_name - Name of the parent object layer (objectgroup)
	max_obj_name_len - Maximum length of object names in the whole level
	max_layer_name_len - Maximum length of object layer names in the whole level

	The following info is included:
	  - Parent object layer name (trimmed)
	  - Object type
	  - Coordinates
	  - Size
	  - Color and alpha value
	e.g.   [gravity_barrier]  AT_bilinear     at (-3, 17),   [102 ☓ 5]   #ff7573/1    |
	'''

	# Extract object-specific data
	position_str = '   '
	dimension_str = ' '
	if obj.get('name') != 'AT_ray':
		position_str += 'at (' + _FormatNumS2TU(obj.get('x')) + ', ' + _FormatNumS2TU(obj.get('y')) + '),'
		dimension_str += '[' + _FormatNumS2TU(obj.get('width')) + ' ☓ ' + _FormatNumS2TU(obj.get('height')) + ']'
	else:
		list_pt = tiled_utils.GetPolyPointsFromObject(obj)
		p1_x = list_pt[0][0]
		p1_y = list_pt[0][1]
		p2_x = list_pt[1][0]
		p2_y = list_pt[1][1]
		line_beg = [ int(_FormatNumS2TU(obj.get('x'))) + p1_x, int(_FormatNumS2TU(obj.get('y'))) + p1_y ]
		line_end = [ int(_FormatNumS2TU(obj.get('x'))) + p2_x, int(_FormatNumS2TU(obj.get('y'))) + p2_y ]
		mid_x = round(( line_end[0] + line_beg[0] )/2)
		mid_y = round(( line_end[1] + line_beg[1] )/2)
		line_w = round(line_end[0] - line_beg[0])
		line_h = round(line_end[1] - line_beg[1])
		position_str += f'at ({mid_x}, {mid_y})'
		dimension_str += f'[{line_w} ☓ {line_h}]'


	# Construct printed string
	print_str = ''
	print_str += _Indent(' [' + parent_layer_name + ']', max_layer_name_len-4)
	print_str += _Indent(' ' + tiled_utils.GetNameFromObject(obj), max_obj_name_len+1)
	print_str += _Indent(position_str,17)
	print_str += _Indent(dimension_str,12)
	print_str += _Indent(' #' + tiled_utils.GetPropertyFromObject(obj, 'color'), 14)
	print_str += '|'
	return print_str





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