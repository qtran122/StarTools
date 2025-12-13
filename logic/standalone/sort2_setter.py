'''
Logic module that can
	1. If using `_sort`, add new `_sort2` property
 TODO	2. Check for `_sort2` conflicts and resolve
 TODO	3. Rename tilelayers

USAGE EXAMPLE:
	main_logic.ErrorCheckSortOrder(playdo)



'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# Constants
SORT0_NAME = 'sort'
SORT1_NAME = '_sort'
SORT2_NAME = '_sort2'

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

	log.Info(f"  Converting old _sort values into newer _sort2...")

	list_old_sort_objects = []	# Use _sort or sort
	list_new_sort_objects = []	# Use _sort2
	list_bad_sort_objects = []	# Use both sort standards in 1 object

	list_targetted_objects = []	# All objects that will be modified

	count = 0
	obj_name = ''



	# Separate all objects into either group, based on which sort standard is used
	IsBothSortStandardUsed = False
	for objectgroup in playdo.GetAllObjectgroup():
		# Ignore object layers if name starts with _
		if objectgroup.get('name')[0] == '_': continue

		for obj in objectgroup:
			count += 1

			# Check properties
			sort0_value = tiled_utils.GetPropertyFromObject(obj, SORT0_NAME)
			sort1_value = tiled_utils.GetPropertyFromObject(obj, SORT1_NAME)
			sort2_value = tiled_utils.GetPropertyFromObject(obj, SORT2_NAME)

			# Check which standard the object is using
			is_obj_group1 = sort0_value != '' or sort1_value != ''
			is_obj_group2 = sort2_value != ''

			# If object is using both standard, print error, then exit
			if is_obj_group1 and is_obj_group2:
				obj_name = obj.get('name')
				IsBothSortStandardUsed = True
				log.Must(f'    ERROR! Both sort standards detected for \'{obj_name}\' : \'{sort0_value}\', \'{sort1_value}\'')
				log.Must(f'  Exiting program now...')
				continue

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
				sort0_value = tiled_utils.GetPropertyFromObject(obj, SORT0_NAME)
				sort1_value = tiled_utils.GetPropertyFromObject(obj, SORT1_NAME)
				log.Must(f'      ({count}) {obj_name} : \'{sort0_value}\', \'{sort1_value}\'')
				count += 1
		else:
			log.Must(f'    List sort2: ')
			for obj in list_new_sort_objects:
				obj_name = obj.get('name')
				sort2_value = tiled_utils.GetPropertyFromObject(obj, SORT2_NAME)
				log.Must(f'      ({count}) {obj_name} : \'{sort2_value}\'')
				count += 1
		log.Must(f'  Exiting program now...')
		return



	# If only sort2 standard is used, exit
	if num_group2 != 0:
		log.Info(f"  --- Only sort2 stardard is used, no change would be applied ---\n")
		return



	# Lastly, if only sort1 standard is used
	#  Apply conversion formula to all these objects
	for obj in list_old_sort_objects:
		# Only one of the two below should be present
		old_sort  = tiled_utils.GetPropertyFromObject(obj, SORT0_NAME)
		old_sort += tiled_utils.GetPropertyFromObject(obj, SORT1_NAME)

		# Apply conversion, then add to list
		sort2_value = _ConvertSort1(old_sort)
		if sort2_value == '':
			obj_name = obj.get('name')
			log.Extra(f'    ERROR! Unable to convert value of \'{obj_name}\' : {old_sort}')
			log.Must(f'  Exiting program now...')
			return
#		tiled_utils.SetPropertyOnObject(obj, SORT2_NAME, sort2_value)
#		tiled_utils.RemovePropertyFromObject(obj, SORT0_NAME)
#		tiled_utils.RemovePropertyFromObject(obj, SORT1_NAME)
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

def ResolveNewSortConflict(playdo):
	x = 1
	log.Info("\n  --- Finished checking conflicts! ---\n")



#--------------------------------------------------#
'''Milestone 3'''

def RenameTilelayer(playdo):
	x = 1





#--------------------------------------------------#
'''Other Utility'''






#--------------------------------------------------#










# End of File