'''
<SUMMARY TBA>

USAGE EXAMPLE:
    raw_dict = conflict.CheckConflicts(playdo, _LIST_LIGHTING_OBJ)
    pruned_dict = conflict.PruneConflicts(playdo, conflict_dictionary)
    conflict.FixConflicts(playdo, pruned_dict)
'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''





#--------------------------------------------------#
'''Public Functions'''

def CheckConflicts(playdo, list_scan_obj):
	''' Task 1 - Check if there is any conflict '''
	log.Info("\n--- Checking for sort value conflicts ---\n")

	# Create the dictionary with each unique sort value as keys
	dict = {}
	for scanned_obj in list_scan_obj:
		curr_obj_list = playdo.GetAllObjectsWithName(scanned_obj)
		log.Info( f'# of \"{scanned_obj}\": {len(curr_obj_list)}' )
		for obj in curr_obj_list:
			curr_string = tiled_utils.GetSort(obj)
			if curr_string == None: continue
			if not curr_string in dict:
				dict[curr_string] = []
			dict[curr_string].append(obj)


	# Print the result
	max_name_len = len( max(list_scan_obj, key = len) )    # Length of longest name in list
	log.Info('')
	log.Info('~~Note: Sort Layers with only 1 element are skipped~~')
	for key, value in dict.items():
		if len(value) == 1: continue
		log.Extra( '--------------------------------------------------' )
		log.Info( f"{key} has {len(value)} elements" )
		for obj in value:
			log.Extra( f'    {PrintObjInfo(obj, GetParentName(obj, playdo), max_name_len)}' )
	log.Extra( '--------------------------------------------------' )


	log.Must("\n--- Finished checking conflicts! ---\n")
	return dict





#--------------------------------------------------#
'''Utility'''


def GetParentName(obj, playdo):
	parent = GetParent(obj, playdo)
	if parent == None: return '...'
	return parent.get('name')[8:]    # Remove beginning, i.e. 'objects_'


# TODO relocate to tiled_utils?
# TODO List comprehension?
def GetParent(obj, playdo):
	'''Return the name of the layer that the object is in'''
	root = playdo.level_root

	# Check all object layers that are in 0~1 layer of folder
	all_objectgroup = root.findall('objectgroup')
	for folder in root.findall('group'):
		all_objectgroup += folder.findall('objectgroup')

	# Check which objectgroup contains the obj
	for group in all_objectgroup:
		for child in group:
			if child == obj: return group
	return None



def PrintObjInfo(obj, p_name, max_name_len = 0):
	'''Specific to cli_sort_conflict'''

	# Extract object-specific data
	position_str = '   '
	dimension_str = ' '
	if obj.get('name') != 'AT_ray':
		position_str += 'at (' + s2tu(obj.get('x')) + ', ' + s2tu(obj.get('y')) + '),'
		dimension_str += '[' + s2tu(obj.get('width')) + ' ☓ ' + s2tu(obj.get('height')) + ']'
	else:
		# TODO
		'''
		line_beg = { get('x') + pt1.x, get('y') + pt1.y }
		line_end = { get('x') + pt2.x, get('y') + pt2.y }
		mid_x = ( line_end[0] + line_beg[0] )/2
		mid_y = ( line_end[1] + line_beg[1] )/2
		line_w = line_end[0] - line_beg[0]
		line_h = line_end[1] - line_beg[1]
		position_str += f'at ({mid_x}, {mid_y})'
		dimension_str += f'[{line_w} ☓ {line_h}]'
		'''
		position_str += ''
		dimension_str += ''


	# Construct printed string
	print_str = ''
	print_str += Indent(' [' + p_name + ']', 15)
	print_str += Indent(' ' + obj.get('name'), max_name_len+1)
	print_str += Indent(position_str,17)
	print_str += Indent(dimension_str,12)
	print_str += Indent(' #' + tiled_utils.GetProperty(obj, 'color'), 14)
	print_str += '|'
	return print_str



#--------------------------------------------------#
'''General Utility, to be relocated?'''

def Indent(s, min_len):
	'''Return the same string, with consistent spacing added to the end'''
	return ( s + ' ' * (min_len-len(s)) )


def s2tu(num_in_str):
	'''Shortcut, for converting coordinates measured in pixels intoto Tiled units'''
	if num_in_str == None: return ''
	return str(int( int(s2i(num_in_str)) / 16 ))
#	return str( int(s2i(num_in_str)) / 16 )


def s2i(num_in_str):
	'''Shortcut, ??? to string'''
	print_int = int(proper_round(float(num_in_str)))
#	print( f'{num_in_str} -> {print_int}' )
	return str(print_int)



# From: https://stackoverflow.com/questions/31818050/round-number-to-nearest-integer
def proper_round(num, dec=0):
    num = str(num)[:str(num).index('.')+dec+2]
    if num[-1]>='5':
        return float(num[:-2-(not dec)]+str(int(num[-2-(not dec)])+1))
    return float(num[:-1])










#--------------------------------------------------#
''' To be removed'''


def PrintObjInfo_deprecated(obj, p_name, max_name_len):
	'''Specific to cli_sort_conflict'''
	print_str = ''
	space_after_name = ' ' * ( max_name_len - len(obj.get('name')) )

	max_name_len = len(print_str) + 15    #  ^
	print_str += ' [' + p_name + ']'
	print_str += ' ' * ( max_name_len - len(print_str) )

	print_str += ' ' + obj.get('name')
	print_str += space_after_name

	max_name_len = len(print_str) + 17    # Increase the constant for extra spacing
	print_str += '   at (' + s2tu(obj.get('x')) + ', ' + s2tu(obj.get('y')) + '),'
	print_str += ' ' * ( max_name_len - len(print_str) )

	max_name_len = len(print_str) + 12    #  ^
	print_str += ' [' + s2tu(obj.get('width')) + ' ☓ ' + s2tu(obj.get('height')) + ']'
	print_str += ' ' * ( max_name_len - len(print_str) )

	max_name_len = len(print_str) + 14    #  ^
	print_str += Indent(' #' + tiled_utils.GetProperty(obj, 'color'), 14)
	print_str += ' ' * ( max_name_len - len(print_str) )

	print_str += '|'
	return print_str



#--------------------------------------------------#










# End of File