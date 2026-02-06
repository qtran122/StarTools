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

REAL_LIGHT_OBJECTGROUP_NAME = 'objects_REAL_LIGHTS'
LIST_OBJ_REAL_LIGHT_NAME = {
    "light_global",
    "light_circle", 
    "light_poly", 
    "light_line"
}





#--------------------------------------------------#
'''Milestone 1 - Check which sort standard a level is using'''

def ErrorCheckSortOrder(playdo):
    '''
    This function does a thorough check to all objects within a level
     Error Check 1 : When an object is using both sort1 & sort2 standards
     Error Check 2 : When the level has some object using sort1 AND some using sort2
     Error Check 3 : When an old sort value cannot be converted into new sort2 value

    Return a tuple (bool, bool)
     1st : Whether an error has been detected
     2nd : Whether the level is using sort1 standard
    '''
    log.Must("Running ReSORT TOOL. Updating tile layer names & object SORT values...\n")
    log.Info(f"  Procedure 1 - Identifying sort standard of \'{playdo.full_file_name.split('/')[-1]}\'")

    # Default error value; 2nd value is irrelevant since the program would exit upon detecting an error
    DEFAULT_ERROR = (True, False)
    
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
                return DEFAULT_ERROR

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
        return DEFAULT_ERROR



    # If only sort2 standard is used, do nothing for this function
    if num_group2 != 0:
        log.Info(f"  --- Only sort2 stardard is used, maintenance mode initiated ---\n")
        return (False, False)
    else:
        log.Info(f"  --- {len(list_old_sort_objects)} objects detected using sort1 standard ---\n")
        return (False, True)





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

    Return a tuple (bool, int, int[2])
     1st : Whether an error has been detected
     2nd : The original layer that BG OWP was at, e.g. 4 if there were 3 BG tilelayers below it
     3rd : Number of BG tilelayers and FG tilelayers in total respectively
    '''
    log.Info("  Procedure 2 - Renaming tilelayers...")

    # Default error value; 2nd & 3rd value are irrelevant since the program would exit upon detecting an error
    DEFAULT_ERROR = (True, -1, [-1,-1])

    list_name_bef_aft = []    # List of tuple, each stores a (<name_before>, <name_after>)
    contains_bg_owp = False
    reached_fg_layers = False
    layer_counter = 0
    layer_counter_all = 0
    max_name_len = 0             # Purely cosmetic, for making the output looks pretty
    bg_anchor_prev_index = -1    # For later : BG "anchor" from OWP; Ensure objects previously above OWP remains above after renaming
    fg_anchor_prev_index = -1    # For later : FG "anchor" from Parallax; same as above
    max_layer_count = []         # For later : Total layer numbers for BG & FG tilelayers

    for layer_name in playdo.GetAllTileLayerNames():
        if not (layer_name.startswith('fg') or layer_name.startswith('bg')): continue
        if max_name_len < len(layer_name): max_name_len = len(layer_name)

        # If too many layers, print error
        layer_counter_all += 1
        if layer_counter_all > 9:
            log.Must("    ERROR! Level contains more than 9 tilelayers!")
            return DEFAULT_ERROR

        # For number suffix
        if not reached_fg_layers:
            if layer_name.startswith('fg'):
                reached_fg_layers = True
                max_layer_count.append(layer_counter)
                layer_counter = 0
        layer_counter += 1
        if layer_counter > 6:
            log.Must("    ERROR! Level contains more than 6 BG/FG tilelayers!")
            return DEFAULT_ERROR

        # Check for the OWP anchor
        if layer_name.startswith('bg'):
            if contains_bg_owp:
                log.Must(f"    ERROR! Tilelayer \'{layer_name}\' is placed above BG OWP!")
                return DEFAULT_ERROR
            if 'owp' in layer_name.lower():
                contains_bg_owp = True

        # Check for overriding _sort property
        if _TilelayerHasSortProperty(playdo, layer_name):
            log.Must(f"    ERROR! Tilelayer \'{layer_name}\' contains _sort property!")
            return DEFAULT_ERROR

        # Renaming
        original_name = layer_name
        layer_name, temp_index = _GetStringOfNewName(layer_name, layer_counter)
        if temp_index > 0: bg_anchor_prev_index = temp_index

        # Apply change, then append to list
        _RenameTilelayer(playdo, original_name, layer_name)
        list_name_bef_aft.append( (original_name, layer_name) )
    max_layer_count.append(layer_counter)


    # Log the layer name change in reversed order
    num_name_change = 0
    for tuple in reversed(list_name_bef_aft):
        if tuple[0] == tuple[1]: continue    # No need to log if the name before == name after
        num_name_change += 1
        log.Must(f"    {_IndentBack(tuple[0], max_name_len+2, True)} -> \'{tuple[1]}\'")
    if num_name_change == 0: log.Must("    None of the tilalayers needs to be renamed")
    log.Must("")

    # Inform user that there is no OWP layer, ask if want to proceed normally or exit
    if not contains_bg_owp:
        log.Must("    WARNING! Level does not contain the BG OWP anchor")


    # Scan through all objects to check their properties and see if affected by renaming
    log.Must("   Additional references in objects will be updated to match the new tilelayer names")
    count = 1
    for obj in playdo.GetAllObjects():
        has_change = _UpdateTileLayerReferencesInObject(obj, list_name_bef_aft, count, playdo)
        if has_change: count += 1
    if count == 1:
        log.Must(f"    (no object references need to be changed)")

    log.Must("")
    return (False, bg_anchor_prev_index, max_layer_count)





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



def _UpdateTileLayerReferencesInObject(obj, list_name_bef_aft, count, playdo):
    '''
     Check through an object's properties to see if there is any outdated tilelayer name references.
     Return True if the object's reference has been updated
    
     :param obj:               XML Object, its properties would be checked
     :param list_name_bef_aft: (string, string), stores the tilelayer name before and after renaming respectively
     :param count:             int, number of objects that have been updated so far
     :param playdo:            A TILED level in an easily moldable state (wrapped around ElementTree + some helpers)
    '''
    # Only proceed if the object contains properties
    properties = obj.find('properties')
    if properties == None: return

    # Check each property individually
    has_change = False
    obj_name = obj.get('name')
    layer_name = tiled_utils.GetParentObject(obj, playdo).get('name')
    for curr_property in properties.findall('property'):
        has_change = has_change or _RenameLayerInProperty(curr_property, list_name_bef_aft, count, obj_name, layer_name)
        # Does not return immediately, in case an object has more than 1 property that needs updating
    return has_change

def _RenameLayerInProperty(curr_property, list_name_bef_aft, count, obj_name, layer_name):
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
        if obj_name == None : obj_name = 'no-name obj'
        log.Must(f"    ({count}) \'{obj_name}\' in layer \'{layer_name}\' will change \'{curr_property.get('name')}\' to \'{new_value}\'")
        return True
    return False



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
    log.Info(f"  Procedure 3 - Re-sorting objects...")
    DEFAULT_ERROR = (True, None)

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
    log.Must(f"   {len(objs_to_resort)} objects will be re-examined to space out the sort orders as needed")
    count_sort_changed, dict_sortval = _Resort_NormalObjects(objs_to_resort, playdo, bg_owp_prev_index, max_layer_count, is_using_sort1)
    if count_sort_changed < 0:
        log.Must("Aborting ReSort. Please correct the error and try again\n")
        return DEFAULT_ERROR

    # Resort dev objects
    if len(objs_dev_sort) > 0:
        log.Info(f"    {len(objs_dev_sort)} objects will be set to the layer's top")
        for obj in objs_dev_sort: _Resort_DevObjects(obj)
        log.Extra("")


    # Log the number of objects using sort1
    _LogObjectsToResort(objs_losing_sort)

    # Remove old sort property
    log.Must(f"    CHANGE SUMMARY:")
    log.Must(f"     objects updating sort listings : {count_sort_changed}")
    log.Must(f"     objects removing sort entirely : {len(objs_losing_sort)}")
    log.Must(f"     dev objects detected           : {len(objs_dev_sort)}")
    
    log.Extra("\n    Removing sort1 property...")
    max_name_len = 1
    for obj in playdo.GetAllObjects():
            layer_name = tiled_utils.GetParentObject(obj, playdo).get('name')
            if max_name_len < len(layer_name): max_name_len = len(layer_name)
    for obj in objs_to_resort: _RemoveOldSortProperty(obj, playdo, max_name_len)
    for obj in objs_dev_sort: _RemoveOldSortProperty(obj, playdo, max_name_len)
    for obj in objs_losing_sort: _RemoveOldSortProperty(obj, playdo, max_name_len)

    log.Must("")

    if is_using_sort1:
        return False, None
    return False, dict_sortval





def _LogObjectsToResort(objs_to_resort):
    '''This function is purely for logging - Shows how many of each objects have redundant _sort'''
    if len(objs_to_resort) == 0: return

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




def _Resort_NormalObjects(objs_to_resort, playdo, bg_owp_prev_index, max_layer_count, is_using_sort1):
    '''
      1. Scan through all input objects
      2. Sort them by existing sort values, either sort1 or sort2
      3. Set adjusted sort2 values to all objects' properties
      4. Return the number of objects whose sort value has been changed
    
    :param objs_to_resort:    List of all relevant XML objects that are currenting using sort2, or will convert to using sort2
    :param playdo:            A TILED level in an easily moldable state (wrapped around ElementTree + some helpers)
    :param bg_owp_prev_index: Integer that indicates index of previous BG OWP layer, e.g. would be 4 for bg_4_owp
    :param max_layer_count:   Integer tuple that keeps track of total numbers of BG & FG tilelayers respectively
    :param is_using_sort1:    Boolean that indicates whether level is using sort1 or sort2
    '''

    DEFAULT_ERROR = -1, None
    # Any really big number - This lets me reorder both BG/FG objects without a separate dictionary
    DICT_KEY_ADDON_FG_SORT = 100000

    count_sort_changed = 0 # Number of objects whose sort value has been changed
    max_name_len = 0    # Purely cosmetic, for making the output looks pretty

    # Map all objects to dictionary, grouped by sort values to then be sorted numerically
    #  Key is the unique sort-group but converted, e.g. "fg_tiles/15" -> big_number + 15 -> 100015
    #  Value is the array of objects, which all belong to the same sort-group 100015
    has_error = False
    dict_all_sortval = {}
    for obj in objs_to_resort:
        old_sort = ''

        # Ignore object when it doesn't have sort property
        if is_using_sort1:
            old_sort = tiled_utils.GetPropertyFromObject(obj, 'sort')
            old_sort += tiled_utils.GetPropertyFromObject(obj, '_sort')
            if old_sort == '':
                obj_name = obj.get('name')
                layer_name = tiled_utils.GetParentObject(obj, playdo).get('name')
                log.Must(f'     WARNING! \'{obj_name}\' in \'{layer_name}\' has no assigned sort1')
                continue
        else:
            old_sort += tiled_utils.GetPropertyFromObject(obj, '_sort2')
            if old_sort == '':
                obj_name = obj.get('name')
                layer_name = tiled_utils.GetParentObject(obj, playdo).get('name')
                log.Must(f'     WARNING! \'{obj_name}\' in \'{layer_name}\' has no assigned sort2')
                continue


        # Create the "key" that allows sorting items by values
        #  e.g. As string, it has trouble handling single-digit numbers
        # old_sort example : "fg_tiles/13"
        sort_layer = old_sort.split('/')[0]      # string portion
        sort_order = int(old_sort.split('/')[1]) # int portion
        if sort_layer == 'fg_tiles': sort_order += DICT_KEY_ADDON_FG_SORT
        elif sort_layer == 'bg_tiles': sort_order += 0    # Do nothing
        else:
            obj_name = obj.get('name')
            parent_name = tiled_utils.GetParentObject(obj, playdo).get('name')
            log.Must(f'ERROR! Invalid sort \'{old_sort}\' : \'{obj_name}\' at \'{parent_name}\'')
            has_error = True
            continue

        if not sort_order in dict_all_sortval: dict_all_sortval[sort_order] = []
        dict_all_sortval[sort_order].append(obj)

    # Show multiple objects with bad sort1 values before exiting
    if has_error: return DEFAULT_ERROR

    # Sort
    dict_all_sortval = dict(sorted(dict_all_sortval.items()))


    # Map all objects to the 2nd dictionary into their respective buckets
    #  Key is the tuple storing unique sort-group in "buckets", e.g. "fg_tiles/15" -> is FG & 2nd layer -> (True, 2)
    #  Value is the array of objects, which all belong to the same "bucket"
    dict_all_buckets = {}
    for key, value in dict_all_sortval.items():
        is_fg_layer = (key > DICT_KEY_ADDON_FG_SORT * 0.8) # Slightly smaller than big number in case of negative
        if is_fg_layer: key -= DICT_KEY_ADDON_FG_SORT

        new_layer_num = _GetLayerNumberFromSortValue(is_fg_layer, key, max_layer_count, is_using_sort1)
        curr_key = (is_fg_layer, new_layer_num)
        if not curr_key in dict_all_buckets:
            dict_all_buckets[curr_key] = []

        for obj in value:
            dict_all_buckets[curr_key].append(obj)
            obj_name = obj.get('name')
            if max_name_len < len(obj_name): max_name_len = len(obj_name)


    # Assign new sort values in properties
    replace_key_bef_aft = None
    for key, value in dict_all_buckets.items():
        is_fg = key[0]
        sortval = key[1]

        # If the BG OWP index is not invalid
        #  Check if current the bucket is BG and above the original OWP anchor layer
        if bg_owp_prev_index >= 0:
            if not is_fg and sortval >= bg_owp_prev_index:
                replace_key_bef_aft = ( (is_fg, sortval), (is_fg, 6) )
                sortval = 6    # OWP is always at the 6th BG tilelayer

        sortval = sortval * 5000
        for obj in value:
            sortval += 10

            sort2_value = ''
            if is_fg: sort2_value += 'fg'
            else: sort2_value += 'bg'
            sort2_value += '_tiles/' + str(sortval)

            obj_name = obj.get('name')
            old_sort  = tiled_utils.GetPropertyFromObject(obj, 'sort')
            old_sort += tiled_utils.GetPropertyFromObject(obj, '_sort')
            old_sort += tiled_utils.GetPropertyFromObject(obj, '_sort2')
            change_indicator = ' '
            if old_sort != sort2_value:
                change_indicator = '*'
                count_sort_changed += 1
            log.Must(f'      {_IndentBack(obj_name, max_name_len+2, True)} {change_indicator} {old_sort} -> {sort2_value}')

            tiled_utils.SetPropertyOnObject(obj, '_sort2', sort2_value)

            # This should never happen
            if sortval > 32000:
                log.Must(f'        WARNING! \'{obj_name}\' has new sort exceeding limit : \'{sortval}\'')
        log.Must("")

    # After the processing, update the dictionary key to correct value before returning
    if replace_key_bef_aft != None:
        old_key = replace_key_bef_aft[0]
        new_key = replace_key_bef_aft[1]
        dict_all_buckets[new_key] = dict_all_buckets.pop(old_key)
    return count_sort_changed, dict_all_buckets





def _GetLayerNumberFromSortValue(is_fg_layer, curr_sort, max_layer_count, is_using_sort1):
    '''
    Helper function for _Resort_NormalObjects().
    Returns the layer number based on the input sort string,
     sort1 - fg_tiles/15    => above the 2nd FG layer => return 2
     sort2 - fg_tiles/16120 => above the 3nd FG layer => return 3

     :param is_fg_layer:     bool, whether current object is in FG tilelayers
     :param curr_sort:       int, the original sort value, accepts both sort1 and sort2
     :param max_layer_count: int, maximum number of BG or FG tilelayers, whichever applicable
     :param is_using_sort1:  bool, whether current object is using sort1
    '''

    # Formula is different between sort1 and sort2
    if is_using_sort1:
        layer_num = int(curr_sort/10) + 1
    else:
        layer_num = int(curr_sort/5000)

    # Allows negative numbers
    if curr_sort < 0: layer_num -=1

    # Cap it based on the number of tilelayers
    #  e.g. As a result, if there are only 4 BG layers, we would treat bg_tiles/31 and bg_tiles/101 the same
    if not is_fg_layer:
        if layer_num > max_layer_count[0]: layer_num = max_layer_count[0]
    else:
        if layer_num > max_layer_count[1]: layer_num = max_layer_count[1]

    return layer_num



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



def _RemoveOldSortProperty(obj, playdo, max_len):
    has_old_sort_a = tiled_utils.RemovePropertyFromObject(obj, 'sort')
    has_old_sort_b = tiled_utils.RemovePropertyFromObject(obj, '_sort')
    if has_old_sort_a or has_old_sort_b:
        obj_name = obj.get('name')
        parent_name = tiled_utils.GetParentObject(obj, playdo).get('name')
        log.Extra(f"      {_IndentBack(parent_name, max_len, True)} : \'{obj_name}\'")





#--------------------------------------------------#
'''Milestone 4'''

def RelocateSortObjects(playdo, dict_sortval, change_view_split = False, change_view_combine = False):
    '''
     Relocate all the sort2 lighting objects.
     Split View:
      For the resorted objects, move next the tilelayers
      For the real light objects, move all to 1 objectgroup next to 'meta'
     Combined View:
      For the resorted objects, move all to 1 objectgroup next to 'meta'
      For the real light objects, they are unaffected
    
     :param playdo:              A TILED level in an easily moldable state (wrapped around ElementTree + some helpers)
     :param dict_sortval:        Dictionary from resorting sort2 objects, key stores the "bucket" info and value stores the array of objects
     :param change_view_split:   Boolean, whether to relocate objects into objectgroups, each group placed next to tilelayers
     :param change_view_combine: Boolean, whether to relocate objects into 1 objectgroup
    '''
    log.Must(f"  Procedure 4 - Relocating all lighting objects")

    if (not change_view_split) and (not change_view_combine):
        log.Must("    No change needed\n")
        return
    if change_view_split and change_view_combine:
        log.Must("    ERROR! Attempting to apply both \"Split View\" and \'Combine View\"\n")
        return

    if change_view_split:
        # Assign new sort values in properties
        log.Must(f"    Applying \"Split View\" into {len(dict_sortval)} groups...")
        for key, value in dict_sortval.items():
            is_fg = key[0]
            sortval = key[1]
            list_obj = value

            # The name for the new objectgroup
            layer_name = 'objects_'
            if is_fg:
                layer_name += 'fg_'
            else:
                layer_name += 'bg_'
            layer_name += f'{str(sortval * 5)}k'
            log.Must(f"     {layer_name}\t{len(list_obj)} objects")

            # Relocate objects between layers
            objectgroup_destination = playdo.GetObjectGroup(layer_name, False)
            for obj in list_obj:
                # Ignore if is already in that objectgroup
                parent_layer = tiled_utils.GetParentObject(obj, playdo)
                parent_name = parent_layer.get('name')
                if parent_name == layer_name: continue
                tiled_utils.MoveObjectToNewObjectgroup(playdo, obj, objectgroup_destination)

            # Move objectgroup next to the correct tilelayer
            tilelayer_destination = _FindAdjacentTilelayer(playdo, layer_name)
            tiled_utils.MoveObjectgroupAfter(playdo, objectgroup_destination, tilelayer_destination)

        # Move all objects to the "Real Light" objectgroup
        log.Must(f"    Moving \"Real Light\" objects into objectgroup \"{REAL_LIGHT_OBJECTGROUP_NAME}\"...")
        real_light_objectgroup = playdo.GetObjectGroup(REAL_LIGHT_OBJECTGROUP_NAME, False)
        meta_objectgroup = playdo.GetObjectGroup('meta', False)
        tiled_utils.MoveObjectgroupAfter(playdo, real_light_objectgroup, meta_objectgroup)
        for obj in playdo.GetAllObjects():
            # Ignore if objects don't need to be moved
            obj_name = obj.get('name')
            if not obj_name in LIST_OBJ_REAL_LIGHT_NAME: continue
            
            # Ignore if is already in that objectgroup
            parent_layer = tiled_utils.GetParentObject(obj, playdo)
            parent_name = parent_layer.get('name')
            if parent_name == REAL_LIGHT_OBJECTGROUP_NAME: continue

            # Move object and log message
            tiled_utils.MoveObjectToNewObjectgroup(playdo, obj, real_light_objectgroup)

        # Move meta objectgroup to be 1st in level, otherwise level might not load in-game
#        tiled_utils.MoveMetaObjectgroupToBottom(playdo)    # Deprecated. Level no longer breaks when lighting comes first?
    
    elif change_view_combine:
        log.Must("    Applying \"Combine View\"...")
        for key, value in dict_sortval.items():
            is_fg = key[0]
            sortval = key[1]
            list_obj = value

            # Relocate all sorted objects to same objectgroup
            layer_name = 'objects_lighting_combined'
            objectgroup_destination = playdo.GetObjectGroup(layer_name, False)
            for obj in list_obj:
                tiled_utils.MoveObjectToNewObjectgroup(playdo, obj, objectgroup_destination)

            # Move the objectgroup right after meta
            meta_objectgroup = playdo.GetObjectGroup('meta', False)
            tiled_utils.MoveObjectgroupAfter(playdo, objectgroup_destination, meta_objectgroup)

    log.Must("")
#    log.Info(f"  --- Finished relocating {1} objects! ---\n")


def _FindAdjacentTilelayer(playdo, layer_name):
    '''
     Find the best spot to relocate the split-view objectgroups.
     e.g. If it's 'objects_bg_10k', it should be slotted between the 'bg_5k' and 'bg_10k' tilelayers
     e.g. If it's 'objects_fg_0k', it should be inserted right before the 'fg_5k" tilelayer
    
     :param playdo:     A TILED level in an easily moldable state (wrapped around ElementTree + some helpers)
     :param layer_name: Name of the objectgroup, e.g. objects_fg_15k
    '''
    
    # Extra the needed info from layer name
    tuple = layer_name.split('_')
    is_fg = (tuple[1] == 'fg')
    sortval = f'_{tuple[2]}'
#    print(f'{tuple} -> {is_fg}, {sortval}')
    
    # Find the correct tilelayer
    list_layer_names = playdo.GetAllTileLayerNames()
    for name in list_layer_names:
        # Check FG/BG layer
        if is_fg and not ('fg' in name): continue
        # Check sort value
        if not sortval in name: continue
        return playdo.GetTilelayer(name, False)
    
    # If none is found, likely indicate it's below the first BG/FG tilelayer, e.g. fg_0k
    # In that case, use the tilelayer right below that instead
    log.Must(f'    WARNING! Cannot find tilelayer with sort \'{sortval}\', may insert objectgroup at wrong spot.')
    for index, name in enumerate(list_layer_names):
        # Check FG/BG layer
        if is_fg and not ('fg' in name): continue
        # Check sort value
        if not '_5k' in name: continue
        return playdo.GetTilelayer(list_layer_names[index-1], False)

    # If still nothing is found, log error, then return 1st tilelayer
    log.Must('    ERROR! Sending to bottom instead...')
    return playdo.GetTilelayer(None, False)




#--------------------------------------------------#
'''Milestone 5'''

def RecolorSortObjects(playdo, dict_sortval, do_recolor = False):
    ''' TBA '''
    log.Must(f"  Procedure 5 - Recolor lighting objects based on color-value")





    log.Info(f"  --- Finished procedure! ---\n")






#--------------------------------------------------#
'''To be deleted'''







#--------------------------------------------------#
'''Other Utility'''

def _IndentBack(string, max_len, add_quotation = False):
    if add_quotation:
        string = f'\'{string}\''
        max_len += 2
    if len(string) < max_len:
        string += (max_len - len(string)) * ' '
    return string









#--------------------------------------------------#










# End of File