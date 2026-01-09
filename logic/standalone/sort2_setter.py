'''
Logic module to upgrade levels from sort1-standard to sort2-standard
 - Finds new sort-indices for objects that are unique in order to avoid conflicts & visual glitches
 - Renames tilelayers to orient them for lighting & rename any direct tilelayer references
 - If file is already using sort2 standard, continues its maintenance (separate out any conflicts)

USAGE EXAMPLE:
    main_logic.ErrorCheckSortOrder(playdo)
    main_logic.RenameTilelayer(playdo)

'''

import re    # For renaming
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# Constants
SLOT_SORT2_LAYER = 5000    # Each tilelayer takes up 5000 slots

LIST_OBJ_RESORT_NAME = {
    "AT",
    "env_particles", 
    "water_line", 
    "water_fill"
}

# TODO deprecate
# _bg_owp_layer_index = [] # Ensures objects previously above OWP remains above after renaming
# _max_layer_count = []    # Total layer numbers for BG & FG tilelayers




#--------------------------------------------------#
'''Milestone 1 - Check which sort standard a level is using'''

ERROR_VALUE_1 = (True, False)
def ErrorCheckSortOrder(playdo):
    '''
    This function does a thorough check to all objects within a level
    Error Check 1 : When an object is using both sort1 & sort2 standards
    Error Check 2 : When the level has some object using sort1 AND some using sort2
    Error Check 3 : When an old sort value cannot be converted into new sort2 value
    '''
    log.Must("Running ReSORT TOOL. Updating tile layer names & object SORT values...\n")
    log.Info(f"  Procedure 1 - Identify which sort standards is used in \'{playdo.full_file_name.split('/')[-1]}\'")

    list_old_sort_objects = []    # Use _sort or sort
    list_new_sort_objects = []    # Use _sort2
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
                return ERROR_VALUE_1

            # Otherwise, assign to list
            if is_obj_group1: list_old_sort_objects.append(obj)
            if is_obj_group2: list_new_sort_objects.append(obj)



    # If both standards exist simultaneously, print the problematic objects, then exit
    num_group1 = len(list_old_sort_objects)
    num_group2 = len(list_new_sort_objects)
    if num_group1 != 0 and num_group2 != 0:
        log.Must(f'Error! Both sort standards detected in the same level!')
        log.Must(f'    {num_group1} objects are explicitly using sort1')
        log.Must(f'    {num_group2} objects are explicitly using sort2\n')
        count = 0
        if num_group1 < num_group2:
            log.Must(f'    Offending sort1 objects: ')
            for obj in list_old_sort_objects:
                obj_name = obj.get('name')
                parent_name = tiled_utils.GetParentObject(obj, playdo).get('name')
                sort0_value = tiled_utils.GetPropertyFromObject(obj, 'sort')
                sort1_value = tiled_utils.GetPropertyFromObject(obj, '_sort')
                log.Must(f'      ({count+1}) \'{obj_name}\' at \'{parent_name}\' : \'{sort0_value}\', \'{sort1_value}\'')
                count += 1
        else:
            log.Must(f'    Offending sort2 objects: ')
            for obj in list_new_sort_objects:
                obj_name = obj.get('name')
                parent_name = tiled_utils.GetParentObject(obj, playdo).get('name')
                sort2_value = tiled_utils.GetPropertyFromObject(obj, '_sort2')
                log.Must(f'      ({count+1}) \'{obj_name}\' at \'{parent_name}\' : \'{sort2_value}\'')
                count += 1
        log.Must('\nAborting ReSort. Please correct level to exclusively use one sort standard and try again')
        return ERROR_VALUE_1



    # If only sort2 standard is used, do nothing for this function
    if num_group2 != 0:
        log.Info(f"  --- Only sort2 stardard is used, no change would be applied ---\n")
        return (False, False)
    else:
        log.Info(f"  --- {len(list_old_sort_objects)} objects detected using sort1 standard ---\n")
        return (False, True)





#--------------------------------------------------#
'''Milestone 2'''

ERROR_VALUE_2 = (True, -1, [-1,-1])
def RenameTilelayer(playdo):
    '''
    This renames all tilelayers to fit the current standard
    Error Check 1 : Level has more than 9 tilelayers
    Error Check 2 : Level has more than 6 FG, or 6 BG tilelayers
    Error Check 3 : Level has another BG layer above bg_owp
    Error Check 4 : A layer contains a _sort property
    Error Check 5 : Level does not have a bg_owp layer
    '''
    log.Info("  Procedure 2 - Rename tilelayers following the new standards")

    list_name_bef_aft = []    # List of tuple, each stores a (<name_before>, <name_after>)
    contains_bg_owp = False
    reached_fg_layers = False
    layer_counter = 0
    layer_counter_all = 0
    max_name_len = 0          # Purely cosmetic, for making the output looks pretty
    bg_owp_prev_index = -1    # For later : Ensure objects previously above OWP remains above after renaming
    max_layer_count = []      # For later : Total layer numbers for BG & FG tilelayers

    for layer_name in playdo.GetAllTileLayerNames():
        if not (layer_name.startswith('fg') or layer_name.startswith('bg')): continue
        if max_name_len < len(layer_name): max_name_len = len(layer_name)

        # If too many layers, print error
        layer_counter_all += 1
        if layer_counter_all > 9:
            log.Must("    ERROR! Level contains more than 9 tilelayers!")
            return ERROR_VALUE_2

        # For number suffix
        if not reached_fg_layers:
            if layer_name.startswith('fg'):
                reached_fg_layers = True
                max_layer_count.append(layer_counter)
                layer_counter = 0
        layer_counter += 1
        if layer_counter > 6:
            log.Must("    ERROR! Level contains more than 6 BG/FG tilelayers!")
            return ERROR_VALUE_2

        # Check for the OWP anchor
        if layer_name.startswith('bg'):
            if contains_bg_owp:
                log.Must(f"    ERROR! Tilelayer \'{layer_name}\' is placed above BG OWP!")
                return ERROR_VALUE_2
            if 'owp' in layer_name.lower():
                contains_bg_owp = True

        # Check for overriding _sort property
        if _TilelayerHasSortProperty(playdo, layer_name):
            log.Must(f"    ERROR! Tilelayer \'{layer_name}\' contains _sort property!")
            return ERROR_VALUE_2

        # Renaming
        original_name = layer_name
        layer_name, temp_index = _GetStringOfNewName(layer_name, layer_counter)
        if temp_index > 0: bg_owp_prev_index = temp_index

        # Apply change, then append to list
        _RenameTilelayer(playdo, original_name, layer_name)
        list_name_bef_aft.append( (original_name, layer_name) )
    max_layer_count.append(layer_counter)


    # Log the layer name change in reversed order
    log.Must("    Existing tilelayers will be renamed to the following:\n")
    for tuple in reversed(list_name_bef_aft):
        log.Must(f"    {_IndentBack(tuple[0], max_name_len+2, True)} -> \'{tuple[1]}\'")
    log.Must("")

    # Inform user that there is no OWP layer, ask if want to proceed normally or exit
    if not contains_bg_owp:
        log.Must("WARNING! Level does not contain the BG OWP anchor")


    # Scan through all objects to check their properties and see if affected by renaming
    log.Must("Additional tilelayer references in objects now updated to match the new names")
    count = 1
    for obj in playdo.GetAllObjects():
        properties = obj.find('properties')
        if properties == None: continue
        obj_name = obj.get('name')
        for curr_property in properties.findall('property'):
            has_change = _RenameLayerInProperty(curr_property, list_name_bef_aft, obj_name, count)
            if has_change: count += 1
    if count == 1:
        log.Must(f"    (no object references need to be changed)")

    log.Info(f"  --- Finished renaming {len(list_name_bef_aft)} layers! ---\n")
    log.Must("")
    return (False, bg_owp_prev_index, max_layer_count)





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

def _RenameLayerInProperty(curr_property, list_name_bef_aft, obj_name, count):
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
        log.Must(f"    ({count}) \'{obj_name}\' : \'{curr_property.get('name')}\' : \'{new_value}\'")
        return True



# https://docs.google.com/document/d/1GN5UMAfNQC44met51Ms4MZ575rQlZAk61CYXeYQelzg/edit?tab=t.i244z3rn90j6
def _GetStringOfNewName(layer_name, layer_counter):
    '''This renames tilelayer from old to new standard'''

    # Keep track of /fx, then remove it temporarily during renaming
    has_fx = '/fx' in layer_name
    layer_name = layer_name.replace('/fx', '')

    # Case 1 - OWP layer is always renamed to 'bg_owp_30k'
    if layer_name.startswith('bg') and 'owp' in layer_name.lower():
        layer_name = "bg_owp_30k"
        if has_fx: layer_name += '/fx'
        return (layer_name, layer_counter)

    # Case 2 - Other layers, 'bg_1_wall' -> 'bg_wall'
    #  1. Remove the ending 'k' in previous sort2 before renaming, e.g. bg_wall_5k
    #  2. Lowercase
    #  3. Non-letter -> space, then trim
    #  4. Space -> underscore
    if layer_name[-1] == 'k': layer_name = layer_name[:-1]
    layer_name = layer_name.lower()
    layer_name = re.sub(r'[^a-z]+', ' ', layer_name)
    layer_name = layer_name.strip()
    layer_name = layer_name.replace(' ', '_')

    # Add the sort number at the end, then add back /fx if needed
    layer_name += f"_{layer_counter * 5}k"
    if has_fx: layer_name += '/fx'
    return (layer_name, -1)





#--------------------------------------------------#
'''Milestone 3'''

def ConvertSortValueStandard(playdo, bg_owp_prev_index, max_layer_count, is_using_sort1):
    '''
    This fixes the _sort2 values in all objects' property.
    Old sort properties shall all be removed afterwards.
    NOTE : Only objects in 'collisions_' and 'objects_' layers are checked, not 'meta' layer
    '''
    log.Info(f"  Procedure 3 - Catergorising objects by sort groups...")

    # Separate objects into one of these 3 groups
    objs_to_resort = []   # These meet the criteria to be "re-sorted", and are most likely to be conflicting
    objs_dev_sort = []    # These are placeholder objects, used for development but not meant to be in the game
    objs_losing_sort = [] # These no longer need a sort property because of the new sort2 standard
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
    log.Extra("")


    # Resort normal objects
    log.Must(f"{len(objs_to_resort)} objects will be updated to use sort2 standard. Results:")
    has_error = _Resort_NormalObjects(objs_to_resort, playdo, bg_owp_prev_index, max_layer_count)
    if has_error:
        log.Must("Aborting ReSort. Please correct the error and try again\n")
        return True

    # Resort dev objects
    if len(objs_dev_sort) > 0:
        log.Info(f"    {len(objs_dev_sort)} objects will be set to the layer's top")
        for obj in objs_dev_sort: _Resort_DevObjects(obj)
        log.Extra("")


    # Log the number of objects using sort1
    _LogObjectsToResort(objs_losing_sort)

    # Remove old sort property
    log.Must(f"    WARNING! SORT TOOL will be removing old sort values for all objects")
    log.Must(f"     objs_to_resort   : {len(objs_to_resort)}")
    log.Must(f"     objs_dev_sort    : {len(objs_dev_sort)}")
    log.Must(f"     objs_losing_sort : {len(objs_losing_sort)}")
    for obj in objs_to_resort: _RemoveOldSortProperty(obj)
    for obj in objs_dev_sort: _RemoveOldSortProperty(obj)
    for obj in objs_losing_sort: _RemoveOldSortProperty(obj)


    log.Info(f"  --- Finished fixing sorts! ---")
    log.Must("")





def _LogObjectsToResort(objs_to_resort):
    '''This function is purely for logging - Shows how many of each objects have redundant _sort'''
    log.Must(f"{len(objs_to_resort)} objects no longer require a sort property and have graduated to a")
    log.Must( " permanent unique sort order; their sort property will be removed.")

    # Key is object name; Value is number of objects with for each name
    dict_by_name = {}
    for obj in objs_to_resort:
        obj_name = obj.get('name')
        if not obj_name in dict_by_name: dict_by_name[obj_name] = 0
        dict_by_name[obj_name] += 1

    # Log the details
    for key, value in dict_by_name.items():
        log.Must(f'    Removing sort property from {value} \'{key}\'')
    log.Must("")




# Any really big number - This lets me reorder both BG/FG objects without a separate dictionary
DICT_KEY_ADDON_FG_SORT = 100000
def _Resort_NormalObjects(objs_to_resort, playdo, bg_owp_prev_index, max_layer_count):
    '''Assign new sort values to the input objects' properties'''

    max_name_len = 0    # Purely cosmetic, for making the output looks pretty

    # Map all objects to dictionary, grouped by sort values to then be sorted numerically
    #  Key is the unique sort-group but converted, e.g. "fg_tiles/15" -> big_number + 15 -> 100015
    #  Value is the array of objects, which all belong to the same sort-group 100015
    has_error = False
    dict_all_sortval = {}
    for obj in objs_to_resort:
        # Ignore object when it doesn't have sort property
        old_sort = tiled_utils.GetPropertyFromObject(obj, 'sort')
        old_sort += tiled_utils.GetPropertyFromObject(obj, '_sort')
        if old_sort == '':
            obj_name = obj.get('name')
            layer_name = tiled_utils.GetParentObject(obj, playdo).get('name')
            log.Must(f'WARNING! \'{obj_name}\' in \'{layer_name}\' has no assigned sort1')
            continue

        # Create the "key" that allows sorting items by values
        #  e.g. As string, it has trouble handling single-digit numbers
        sort_group = old_sort.split('/')[0]
        sort_value = old_sort.split('/')[1]
        sort_id = int(sort_value)
        if sort_group.startswith('fg'): sort_id += DICT_KEY_ADDON_FG_SORT
        elif sort_group.startswith('bg'): sort_id += 0    # Do nothing
        else:
            obj_name = obj.get('name')
            log.Must(f'ERROR! \'{obj_name}\' is using invalid sort value : \'{old_sort}\'')
            has_error = True
            continue

        if not sort_id in dict_all_sortval: dict_all_sortval[sort_id] = []
        dict_all_sortval[sort_id].append(obj)

    # Show multiple objects with bad sort1 values before exiting
    if has_error: return True

    # Sort
    dict_all_sortval = dict(sorted(dict_all_sortval.items()))


    # Map all objects to the 2nd dictionary into their respective buckets
    #  Key is the tuple storing unique sort-group in "buckets", e.g. "fg_tiles/15" -> is FG & 2nd layer -> (True, 2)
    #  Value is the array of objects, which all belong to the same "bucket"
    dict_all_buckets = {}
    for key, value in dict_all_sortval.items():
        is_fg_layer = (key > DICT_KEY_ADDON_FG_SORT * 0.8) # Slightly smaller than big number in case of negative
        if is_fg_layer: key -= DICT_KEY_ADDON_FG_SORT

        curr_key = _GetNewKeyFromSortValue(is_fg_layer, key, max_layer_count)
        if not curr_key in dict_all_buckets:
            dict_all_buckets[curr_key] = []

        for obj in value:
            dict_all_buckets[curr_key].append(obj)
            obj_name = obj.get('name')
            if max_name_len < len(obj_name): max_name_len = len(obj_name)


    # Assign new sort values in properties
    count_all_obj = 0    # TODO remove it since it's redundant
    for key, value in dict_all_buckets.items():
        is_fg = key[0]
        sortval = key[1]

        # If not invalid
        #  Check if current the bucket is BG and above the original OWP anchor layer
        if bg_owp_prev_index >= 0:
            if not is_fg and sortval >= bg_owp_prev_index: sortval = 6    # OWP is always at the 6th BG tilelayer

        sortval = sortval * 5000
        for obj in value:
            count_all_obj += 1
            sortval += 10

            sort2_value = ''
            if is_fg: sort2_value += 'fg'
            else: sort2_value += 'bg'
            sort2_value += '_tiles/' + str(sortval)
            tiled_utils.SetPropertyOnObject(obj, '_sort2', sort2_value)

            obj_name = obj.get('name')
            old_sort  = tiled_utils.GetPropertyFromObject(obj, 'sort')
            old_sort += tiled_utils.GetPropertyFromObject(obj, '_sort')
            log.Must(f'      {_IndentBack(obj_name, max_name_len+2, True)} : {old_sort} -> {sort2_value}')
#            log.Must(f'  {count_all_obj}\t  {_IndentBack(obj_name, max_name_len+2, True)} : {old_sort} -> {sort2_value}')

            # This should never happen
            if sortval > 32000:
                log.Must(f'        WARNING! \'{obj_name}\' has new sort exceeding limit : \'{sortval}\'')
        log.Must("")





def _GetNewKeyFromSortValue(is_fg_layer, curr_sort, max_layer_count):
    '''Returns the key of which sort bucket this value should lead to'''
    layer_num = int(curr_sort/10) + 1
    if curr_sort < 0: layer_num -=1

    # If there are only 4 BG layers, bg_tiles/31 & bg_tiles/101 are treated the same
    if not is_fg_layer:
        if layer_num > max_layer_count[0]: layer_num = max_layer_count[0]
    else:
        if layer_num > max_layer_count[1]: layer_num = max_layer_count[1]

    new_key = (is_fg_layer, layer_num)
    return new_key



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
#    log.Must(f"      \'{obj_name}\' : {has_old_sort_a}, {has_old_sort_b}")
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







#--------------------------------------------------#
'''Other Utility'''

def _IndentBack(string, max_len, add_quotation = False):
    if add_quotation: string = f'\'{string}\''
    if len(string) < max_len:
        string += (max_len - len(string)) * ' '
    return string









#--------------------------------------------------#










# End of File