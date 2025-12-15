'''
Logic module that can
	1. If using `_sort`, add new `_sort2` property
	2. Rename tilelayers
 TODO	3. Color code lighting objects after sort
 TODO	4. Enable switching between two views for lighting objects
 TODO	?? Check for `_sort2` conflicts and resolve

USAGE EXAMPLE:
	main_logic.ErrorCheckSortOrder(playdo)
	main_logic.RenameTilelayer(playdo)

'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# Constants
SLOT_SORT2_LAYER = 5000	# Each tilelayer takes up 5000 slots



#--------------------------------------------------#
'''Milestone 1 - Check which sort standard a level is using'''

def ErrorCheckSortOrder(playdo):
	'''
	This function does a thorough check to all objects within a level
	Error Check 1 : When an object is using both sort1 & sort2 standards
	Error Check 2 : When the level has some object using sort1 AND some using sort2
	Error Check 3 : When an old sort value cannot be converted into new sort2 value
	'''
	log.Must(f"  Procedure 1 - Converting old _sort values into newer _sort2...")

	list_old_sort_objects = []	# Use _sort or sort
	list_new_sort_objects = []	# Use _sort2
	list_bad_sort_objects = []	# Use both sort standards in 1 object

	list_targetted_objects = []	# All objects that will be modified

	count = 0
	obj_name = ''



	# Separate all objects into either group, based on which sort standard is used
	both_sort_standards_used = False
	for objectgroup in playdo.GetAllObjectgroup():
		# Ignore object layers if name starts with _
		if objectgroup.get('name')[0] == '_': continue

		for obj in objectgroup:
			count += 1

			# Check properties
			sort0_value = tiled_utils.GetPropertyFromObject(obj, 'sort')
			sort1_value = tiled_utils.GetPropertyFromObject(obj, '_sort')
			sort2_value = tiled_utils.GetPropertyFromObject(obj, '_sort2')

			# Check which standard the object is using
			is_obj_group1 = sort0_value != '' or sort1_value != ''
			is_obj_group2 = sort2_value != ''

			# If object is using both standard, print error, then exit
			if is_obj_group1 and is_obj_group2:
				obj_name = obj.get('name')
				both_sort_standards_used = True
				log.Must(f'    ERROR! Both sort standards detected for \'{obj_name}\' : \'{sort0_value}\', \'{sort1_value}\'')
				log.Must(f'  Exiting program now...')
				return True

			# Otherwise, assign to list
			if is_obj_group1: list_old_sort_objects.append(obj)
			if is_obj_group2: list_new_sort_objects.append(obj)



	# If both standards exist simultaneously, print the problematic objects, then exit
	num_group1 = len(list_old_sort_objects)
	num_group2 = len(list_new_sort_objects)
	if num_group1 != 0 and num_group2 != 0:
		log.Must(f'  Error! Both sort standards detected in the same level!')
		log.Info(f'    {num_group1} objects are using sort1')
		log.Info(f'    {num_group2} objects are using sort2')
		count = 0
		if num_group1 < num_group2:
			log.Must(f'    List sort1: ')
			for obj in list_old_sort_objects:
				obj_name = obj.get('name')
				sort0_value = tiled_utils.GetPropertyFromObject(obj, 'sort')
				sort1_value = tiled_utils.GetPropertyFromObject(obj, '_sort')
				log.Must(f'      ({count}) {obj_name} : \'{sort0_value}\', \'{sort1_value}\'')
				count += 1
		else:
			log.Must(f'    List sort2: ')
			for obj in list_new_sort_objects:
				obj_name = obj.get('name')
				sort2_value = tiled_utils.GetPropertyFromObject(obj, '_sort2')
				log.Must(f'      ({count}) {obj_name} : \'{sort2_value}\'')
				count += 1
		log.Must(f'  Exiting program now...')
		return True



	# If only sort2 standard is used, do nothing for this function
	if num_group2 != 0:
		log.Info(f"  --- Only sort2 stardard is used, no change would be applied ---\n")
		return



	# Lastly, if only sort1 standard is used
	#  Apply conversion formula to all these objects
	for obj in list_old_sort_objects:
		# Only one of the two below should be present
		old_sort  = tiled_utils.GetPropertyFromObject(obj, 'sort')
		old_sort += tiled_utils.GetPropertyFromObject(obj, '_sort')

		# Apply conversion, then add to list
		sort2_value = _ConvertSort1(old_sort)
		if sort2_value == '':
			obj_name = obj.get('name')
			log.Extra(f'    ERROR! Unable to convert value of \'{obj_name}\' : {old_sort}')
			log.Must(f'  Exiting program now...')
			return True
#		tiled_utils.SetPropertyOnObject(obj, '_sort2', sort2_value)
#		tiled_utils.RemovePropertyFromObject(obj, 'sort')
#		tiled_utils.RemovePropertyFromObject(obj, '_sort')
		log.Extra(f'    ({len(list_targetted_objects)}) {obj_name} \t: {old_sort} -> {sort2_value}')
		list_targetted_objects.append(obj)

	log.Info(f"  --- Finished converting {len(list_targetted_objects)} old _sort values! ---\n")



def _ConvertSort1(sort1_value):
	# Certain objects cannot be converted? e.g. env_art
	sort1_tuple = sort1_value.split('/')
	if len(sort1_tuple) < 2: return ''

	# game_objects is ignored, and is thus not processed
	if sort1_tuple[0] == 'game_objects': return sort1_value

	# Apply simple conversion formula
	sort1_num = int(sort1_tuple[1])
	sort2_num1 = int(sort1_num / 10) * SLOT_SORT2_LAYER
	sort2_num2 = sort1_num % 10
	if sort1_num < 0:
		sort2_num2 = - (10 - sort2_num2)

	# Safety check, range: [-32768, 32767]
	sort2_num = sort2_num1 + sort2_num2
	if sort2_num < -32700: sort2_num = -32700
	if sort2_num >  32700: sort2_num =  32700

	sort2_value = f'{sort1_tuple[0]}/{sort2_num}'
	return sort2_value





#--------------------------------------------------#
'''Milestone 2'''

def RenameTilelayer(playdo):
	'''
	This renames all tilelayers to fit the current standard
	Error Check 1 : Level has more than 9 tilelayers
	Error Check 2 : Level has more than 6 FG, or 6 BG tilelayers
	Error Check 3 : Level has another BG layer above bg_owp
	Error Check 4 : A layer contains a _sort property
	Error Check 5 : Level does not have a bg_owp layer
	'''
	log.Must("  Procedure 2 - Renaming tilelayers with new standards...")

	list_name_bef_aft = []    # List of tuple, each stores a (<name_before>, <name_after>)
	contains_bg_owp = False
	now_at_fg = False
	layer_counter = 0
	layer_counter_all = 0

	for layer_name in playdo.GetAllTileLayerNames():
		if not (layer_name.startswith('fg') or layer_name.startswith('bg')): continue

		# If too many layers, print error
		layer_counter_all += 1
		if layer_counter_all > 9:
			log.Must("    ERROR! Level contains more than 9 tilelayers!")
			return True

		# For number suffix
		if not now_at_fg:
			if layer_name.startswith('fg'):
				now_at_fg = True
				layer_counter = 0
		layer_counter += 1
		if layer_counter > 6:
			log.Must("    ERROR! Level contains more than 6 BG/FG tilelayers!")
			return True

		# Check for the OWP anchor
		if layer_name.startswith('bg'):
			if contains_bg_owp:
				log.Must(f"    ERROR! Tilelayer \'{layer_name}\' is placed above BG OWP!")
				return True
			if 'owp' in layer_name.lower():
				contains_bg_owp = True

		# Check for overriding _sort property
		if _TilelayerHasSortProperty(playdo, layer_name):
			log.Must(f"    ERROR! Tilelayer \'{layer_name}\' contains _sort property!")
			return True

		# Renaming
		original_name = layer_name
		layer_name = _RemoveNumber(layer_name)
		layer_name = _RemoveEndingSpaceAndHyphen(layer_name)
		layer_name = _ReplaceSpace(layer_name) # With underscore
		layer_name = _RemoveDoubleHyphen(layer_name)
		layer_name = _SetAllLowercase(layer_name)
		layer_name = _AddTilelayerSortNumber(layer_name, layer_counter)
		layer_name = _RenameOWPLayer(layer_name)

		# Apply change, then append to list
		_RenameTilelayer(playdo, original_name, layer_name)
		list_name_bef_aft.append( (original_name, layer_name) )
		log.Extra(f"    Renaming layer : \'{original_name}\' \t-> \'{layer_name}\'")

	if not contains_bg_owp:
		log.Must("    ERROR! Level does not contain the BG OWP anchor")
		return True

	log.Info(f"  --- Finished renaming {len(list_name_bef_aft)} layers! ---\n")





def _TilelayerHasSortProperty(playdo, layer_name):
	for layer in playdo.level_root.findall('.//layer'):
		if layer.get('name') != layer_name: continue
		if tiled_utils.GetPropertyFromObject(layer, '_sort') != '': return True
	return False

def _RenameTilelayer(playdo, original_name, layer_name):
	for layer in playdo.level_root.findall('.//layer'):
		if layer.get('name') != original_name: continue
		layer.set('name', layer_name)
		return



def _RemoveNumber(layer_name):
	for i in range(10):
		layer_name = layer_name.replace(f'{i}', '')
	layer_name = layer_name.replace('__', '_')
	return layer_name

def _RemoveEndingSpaceAndHyphen(layer_name):
	# bg_3_deco -> bg_deco
	has_fx = '/fx' in layer_name
	layer_name = layer_name.replace('/fx', '')
	if layer_name.endswith(' '): layer_name = layer_name[:-1]
	if layer_name.endswith('-'): layer_name = layer_name[:-1]
	if layer_name.endswith(' '): layer_name = layer_name[:-1]
	if has_fx: layer_name += '/fx'
	return layer_name

def _ReplaceSpace(layer_name):
	return layer_name.replace(' ', '_')

def _RemoveDoubleHyphen(layer_name):
	return layer_name.replace('__', '_')

def _SetAllLowercase(layer_name):
	return layer_name.lower()

def _AddTilelayerSortNumber(layer_name, layer_counter):
	has_fx = '/fx' in layer_name
	layer_name = layer_name.replace('/fx', '')
	layer_name += f"_{layer_counter * 5}k"
	if has_fx: layer_name += '/fx'
	return layer_name

def _RenameOWPLayer(layer_name):
	# Always renamed to bg_owp_30k
	if layer_name.startswith('bg') and 'owp' in layer_name.lower():
		return "bg_owp_30k"
	return layer_name





#--------------------------------------------------#






	'''

def _RemoveStartingNumber(layer_name):
	# bg_3_deco -> bg_deco
	for i in range(10):
		layer_name = layer_name.replace(f'_{i}_', '_')
	return layer_name




To be deleted
	# Can we just do it after the file is written?
	for obj in playdo.GetAllObjects():
		list_properties = obj.get("properties")
		for property in list_properties:
			prop_value = property.get("value")
			if prop_value contains list_name_bef_aft
	'''




#--------------------------------------------------#
'''Milestone 3'''

def TODO(playdo):
	x = 1





#--------------------------------------------------#
'''Other Utility'''






#--------------------------------------------------#










# End of File