'''
Logic module that can
	1. If using `_sort`, add new `_sort2` property
	2. Rename tilelayers
	3. Group all objects by their sorts, then resort the `_sort2` values
 TODO	x. Color code lighting objects after sort
 TODO	x. Enable switching between two views for lighting objects

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

LIST_OBJ_RESORT_NAME = {
	"AT",
	"env_particles", 
	"water_line", 
	"water_fill"
}

_bg_owp_bef_aft = []	# Second number is always 6, for the bg_owp_30k anchor
_max_layer_count = []	# Total layer numbers for BG & FG tilelayers




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
	obj_name = ''



	# Separate all objects into either group, based on which sort standard is used
	both_sort_standards_used = False
	for objectgroup in playdo.GetAllObjectgroup():
		# Ignore object layers if not read by level
		layer_name = objectgroup.get('name')
		if not (layer_name.startswith('objects') or layer_name.startswith('collisions')): continue

		for obj in objectgroup:
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
		log.Info(f'    {num_group1} objects are explicitly using sort1')
		log.Info(f'    {num_group2} objects are explicitly using sort2')
		count = 0
		if num_group1 < num_group2:
			log.Must(f'    List sort1: ')
			for obj in list_old_sort_objects:
				obj_name = obj.get('name')
				parent_name = tiled_utils.GetParentObject(obj, playdo).get('name')
				sort0_value = tiled_utils.GetPropertyFromObject(obj, 'sort')
				sort1_value = tiled_utils.GetPropertyFromObject(obj, '_sort')
				log.Must(f'      ({count+1}) \'{obj_name}\' at \'{parent_name}\' : \'{sort0_value}\', \'{sort1_value}\'')
				count += 1
		else:
			log.Must(f'    List sort2: ')
			for obj in list_new_sort_objects:
				obj_name = obj.get('name')
				parent_name = tiled_utils.GetParentObject(obj, playdo).get('name')
				sort2_value = tiled_utils.GetPropertyFromObject(obj, '_sort2')
				log.Must(f'      ({count+1}) \'{obj_name}\' at \'{parent_name}\' : \'{sort2_value}\'')
				count += 1
		log.Must(f'  Exiting program now...')
		return True



	# If only sort2 standard is used, do nothing for this function
	if num_group2 != 0:
		log.Info(f"  --- Only sort2 stardard is used, no change would be applied ---\n")
	else:
		log.Info(f"  --- {len(list_old_sort_objects)} objects detected using sort1 standard ---\n")





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
				_max_layer_count.append(layer_counter)
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
		layer_name = _GetStringOfNewName(layer_name, layer_counter)

		# Apply change, then append to list
		_RenameTilelayer(playdo, original_name, layer_name)
		list_name_bef_aft.append( (original_name, layer_name) )
		log.Extra(f"    Renaming layer : \'{original_name}\' \t-> \'{layer_name}\'")
	_max_layer_count.append(layer_counter)
#	print(f'{_max_layer_count[0]} BG Layer & {_max_layer_count[1]} FG Layers')


	# Inform user that there is no OWP layer, ask if want to proceed normally or exit
	if not contains_bg_owp:
		log.Must("    WARNING! Level does not contain the BG OWP anchor")
		user_input = input("      Continue processing the level? (Y/N) ")
		if user_input[0].lower() == 'n':
			log.Must("      Exiting program...")
			return True

	# Scan through all objects to check their properties and see if affected by renaming
	for obj in playdo.GetAllObjects():
		properties = obj.find('properties')
		if properties == None: continue
		for curr_property in properties.findall('property'):
			_RenameLayerInProperty(curr_property, list_name_bef_aft)

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

def _RenameLayerInProperty(curr_property, list_name_bef_aft):
	'''Adjust the property value if it contains a tilelayer name that needs to be renamed'''
	# Scan through all properties
	old_value = curr_property.get('value')
	new_value = old_value
	for tuple in list_name_bef_aft:
		if tuple[0] in new_value:
			new_value = new_value.replace(tuple[0], tuple[1])

	# Set the property value if there is a change
	if new_value != old_value:
		curr_property.set('value', new_value)
		log.Extra(f"    Update property \'{curr_property.get('name')}\' : \'{old_value}\' \t-> \'{new_value}\'")



def _GetStringOfNewName(layer_name, layer_counter):
	'''This renames tilelayer from old to new standard'''

	# Keep track of /fx
	has_fx = '/fx' in layer_name
	layer_name = layer_name.replace('/fx', '')

	# For the OWP layer, always renamed to bg_owp_30k
	if layer_name.startswith('bg') and 'owp' in layer_name.lower():
		_bg_owp_bef_aft.append(layer_counter)
		_bg_owp_bef_aft.append(6)
		layer_name = "bg_owp_30k"
		if has_fx: layer_name += '/fx'
		return layer_name

	# Remove numbers
	for i in range(10):
		layer_name = layer_name.replace(f'{i}', '')
	layer_name = layer_name.replace('__', '_')

	# Remove the ending space & hyphen
	#  bg_deco - 3 -> bg_deco
	if layer_name.endswith(' '): layer_name = layer_name[:-1]
	if layer_name.endswith('-'): layer_name = layer_name[:-1]
	if layer_name.endswith(' '): layer_name = layer_name[:-1]

	# Replace space with underscore
	layer_name = layer_name.replace(' ', '_')

	# Remove double-hyphen
	layer_name = layer_name.replace('__', '_')

	# Set all char to lowercase
	layer_name = layer_name.lower()

	# Add the sort number at the end
	layer_name += f"_{layer_counter * 5}k"

	# Add back /fx if applicable
	if has_fx: layer_name += '/fx'
	return layer_name





#--------------------------------------------------#
'''Milestone 3'''

def ConvertSortValueStandard(playdo):
	''' TBA '''
	log.Must(f"  Procedure 3 - Catergorising objects by sort groups...")

	# Separate objects into one of these 3 groups
	objs_to_resort = []
	objs_dev_sort = []
	objs_losing_sort = []
	for obj in playdo.GetAllObjects():
		obj_name = obj.get('name')
		if obj_name == None: continue

		# Is in resort group?
		if obj_name in LIST_OBJ_RESORT_NAME:
			objs_to_resort.append(obj)
			continue
		if obj_name.startswith('AT_'):
			objs_to_resort.append(obj)
			continue

		# Is in dev group?
		if tiled_utils.GetPropertyFromObject(obj, '_dev_load') != '':
			objs_dev_sort.append(obj)
			continue

		# Otherwise, link to the TBD group
		if tiled_utils.GetPropertyFromObject(obj, 'sort') != '':
			objs_losing_sort.append(obj)
		if tiled_utils.GetPropertyFromObject(obj, '_sort') != '':
			objs_losing_sort.append(obj)

	# Append the 2 groups to remove their sort as well?
	for obj in objs_to_resort: objs_losing_sort.append(obj)
	for obj in objs_dev_sort: objs_losing_sort.append(obj)
	log.Extra("")


	# Resort normal objects
	log.Info(f"    {len(objs_to_resort)} objects will be resorted")
	_Resort_NormalObjects(objs_to_resort)
	log.Extra("")
	return

	# Resort dev objects
	log.Info(f"    {len(objs_dev_sort)} objects will be set to the layer's top")
	for obj in objs_dev_sort: _Resort_DevObjects(obj)
	log.Extra("")


	# Proceed with removing sort values, only if the list is non-empty
	if len(objs_losing_sort) == 0:
		log.Info(f"  --- Finished fixing sorts! ---\n")
		return

	# Waits for player's input
	log.Must(f"    WARNING! SORT TOOL will be removing sort values for:")
	log.Must(f"    (TODO for TY - show list of objects by names)")
	log.Must(f"      {_CountObjectsWithName(objs_losing_sort, 'enemy')} enemies,")
	log.Must(f"      {_CountObjectsWithName(objs_losing_sort, 'relic_block')} relic blocks,")
	log.Must(f"      {len(objs_to_resort)} objects with new sort2 values,")
	log.Must(f"      {len(objs_dev_sort)} objects with dev sort2 values, (\'_dev_load\')")
	user_input = input("      Proceed? (Y/N) ")
	if user_input[0].lower() == 'n': return

	# Remove old sort property
	log.Info(f"    All {len(objs_losing_sort)} objects will remove their sort values")
	for obj in objs_losing_sort: _RemoveOldSortProperty(obj)
	for obj in objs_to_resort: _RemoveOldSortProperty(obj)
	for obj in objs_dev_sort: _RemoveOldSortProperty(obj)

	log.Info(f"  --- Finished fixing sorts! ---\n")





DICT_KEY_ADDON_FG_SORT = 10000	# Any really big number
def _Resort_NormalObjects(objs_to_resort):
	# TBA
	# Create the dictionary with each "bucket" as key, i.e. dictionaries each for a layer


	# Map all objects to dictionary, grouped by sort values to then be sorted numerically
	dict_all_sortval = {}
	for obj in objs_to_resort:
		old_sort = tiled_utils.GetPropertyFromObject(obj, 'sort')
		old_sort += tiled_utils.GetPropertyFromObject(obj, '_sort')
		if old_sort == '': continue    # When doesn't have the property somehow

		# Create the "key" that allows sorting items by values
		#  e.g. As string, it has trouble handling single-digit numbers
		sort_group = old_sort.split('/')[0]
		sort_value = old_sort.split('/')[1]
		sort_id = int(sort_value)
		if sort_group.startswith('fg'): sort_id += DICT_KEY_ADDON_FG_SORT
		elif sort_group.startswith('bg'): sort_id += 0	# Do nothing
		else:
			obj_name = obj.get('name')
			log.Must(f'      WARNING! \'{obj_name}\' with invalid sort is ignored : \'{old_sort}\'')
			continue

		if not sort_id in dict_all_sortval: dict_all_sortval[sort_id] = []
		dict_all_sortval[sort_id].append(obj)

	dict_all_sortval = dict(sorted(dict_all_sortval.items()))
#	for key, value in dict_all_sortval.items(): print(f'{key} : {len(value)}')
#	print()


	# Map all objects to the 2nd dictionary into their respective buckets
	dict_all_buckets = {}
	for key, value in dict_all_sortval.items():
		is_fg_layer = (key > DICT_KEY_ADDON_FG_SORT * 0.8)
		if is_fg_layer: key -= DICT_KEY_ADDON_FG_SORT
#		print(f'{is_fg_layer} {key}')

		curr_key = _GetNewKeyFromSortValue(is_fg_layer, key)
		if not curr_key in dict_all_buckets:
			dict_all_buckets[curr_key] = []
		for obj in value: dict_all_buckets[curr_key].append(obj)

#	print()
#	for key, value in dict_all_buckets.items(): print(f'{key} : {len(value)}')


	# Assign new sort values in properties
	count_all_obj = 0
#	_bg_owp_bef_aft.append(5)	# Debug
#	_bg_owp_bef_aft.append(10)	# Debug
#	print(f'{_max_layer_count[0]} BG Layer & {_max_layer_count[1]} FG Layers')
#	print(f'OWP Anchor : {_bg_owp_bef_aft[0]} -> {_bg_owp_bef_aft[1]}')
	for key, value in dict_all_buckets.items():
		sortval = key[1]

		# Check if the bucket is above the original OWP anchor layer
		if not key[0] and len(_bg_owp_bef_aft) >= 2:
			if sortval >= _bg_owp_bef_aft[0]: sortval = _bg_owp_bef_aft[1]

		sortval = sortval * 5000
		for obj in value:
			count_all_obj += 1
			sortval += 10

			sort2_value = ''
			if key[0]: sort2_value += 'fg'
			else: sort2_value += 'bg'
			sort2_value += '_tiles/' + str(sortval)
			tiled_utils.SetPropertyOnObject(obj, '_sort2', sort2_value)

			obj_name = obj.get('name')
			old_sort  = tiled_utils.GetPropertyFromObject(obj, 'sort')
			old_sort += tiled_utils.GetPropertyFromObject(obj, '_sort')
			log.Extra(f'      \'{obj_name}\' \t: {old_sort} -> {sort2_value}')

			# This should never happen
			if sortval > 32000:
				log.Must(f'        WARNING! \'{obj_name}\' has new sort exceeding limit : \'{sortval}\'')

#	log.Info(f"    --- Finished resorting {count_all_obj} objects! ---\n")



def _GetNewKeyFromSortValue(is_fg_layer, curr_sort):
	'''Returns the key of which sort bucket this value should lead to'''
	layer_num = int(curr_sort/10) + 1
	if curr_sort < 0: layer_num -=1

	# If there are only 4 BG layers, bg_tiles/31 & bg_tiles/101 are treated the same
	if not is_fg_layer:
		if layer_num > _max_layer_count[0]: layer_num = _max_layer_count[0]
	else:
		if layer_num > _max_layer_count[1]: layer_num = _max_layer_count[1]

	new_key = (is_fg_layer, layer_num)
	return new_key





def _CountObjectsWithName(list_obj, prefix):
	count = 0
	for obj in list_obj:
		obj_name = obj.get('name')
		obj_type = obj.get('type')
		if obj_name != None and obj_name.startswith(prefix): count += 1
		else:
			if obj_type != None and obj_type.startswith(prefix): count += 1
	return count



def _Resort_DevObjects(obj):
	obj_name = obj.get('name')
	old_sort = tiled_utils.GetPropertyFromObject(obj, 'sort')
	old_sort += tiled_utils.GetPropertyFromObject(obj, '_sort')
	if old_sort != '':
		new_value = ''
		if old_sort.startswith('fg_'): new_value += 'fg'
		else: new_value += 'bg'
		new_value += '_tiles/32767'
		tiled_utils.SetPropertyOnObject(obj, '_sort2', new_value)
		log.Extra(f"      \'{obj_name}\' \t: {old_sort} -> {new_value}")
	else:
		log.Must(f"      ERROR! \'{obj_name}\' object has \'_dev_load\' but doesn't contain a sort value")



def _RemoveOldSortProperty(obj):
	has_old_sort_a = tiled_utils.RemovePropertyFromObject(obj, 'sort')
	has_old_sort_b = tiled_utils.RemovePropertyFromObject(obj, '_sort')
	if has_old_sort_a or has_old_sort_b:
		obj_name = obj.get('name')
		log.Extra(f"      Removing old sort property from \'{obj_name}\'")





#--------------------------------------------------#
'''Milestone 4'''

def TBA(playdo):
	''' TBA '''
	log.Must(f"  Procedure 4 - ")






	log.Info(f"  --- Finished renaming {1} layers! ---\n")






#--------------------------------------------------#
'''To be deleted'''


def _Resort_NormalObjects_deprecate(obj):
	obj_name = obj.get('name')

	# Only one of the two below should be present
	old_sort  = tiled_utils.GetPropertyFromObject(obj, 'sort')
	old_sort += tiled_utils.GetPropertyFromObject(obj, '_sort')

	# Apply conversion, then add to list
	sort2_value = _ConvertSort1(old_sort)
	if sort2_value == '':
		log.Must(f'      WARNING! \'{obj_name}\' is using invalid sort value : \'{old_sort}\'')
#		log.Must(f'    Exiting program now...')
#		return True
#	tiled_utils.SetPropertyOnObject(obj, '_sort2', sort2_value)
#	tiled_utils.RemovePropertyFromObject(obj, 'sort')
#	tiled_utils.RemovePropertyFromObject(obj, '_sort')

#	({len(list_targetted_objects)+1}) 
	log.Extra(f'      \'{obj_name}\' \t: {old_sort} -> {sort2_value}')
#	list_targetted_objects.append(obj)

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
'''Other Utility'''






#--------------------------------------------------#










# End of File