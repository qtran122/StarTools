'''
Aligner scans the whole level, then process all objects with name as "water_line".


USAGE EXAMPLE:
    aligner.AlignWater(playdo)
'''

import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

#--------------------------------------------------#
'''Variables'''

# For logging
CHAR_TRUE  = "  ○ "
CHAR_FALSE = "  ☓ "



#--------------------------------------------------#
'''Public Functions'''

def AlignWater(playdo):
    log.Info("\n--- Aligning water_line Objects ---\n")

    # Get objectgroup that contains the water
    list_of_all_water_lines = playdo.GetAllObjectsWithName("water_line")
    log.Must(f'Found {len(list_of_all_water_lines)} waterlines')

    # Process individual object
    count_need_alignment = 0
    log.Info("--------------------------------------------------")
    for count, water_line_obj in enumerate(list_of_all_water_lines):
        if count != 0:
            log.Extra("--------------------------------------------------")

        # Obtain vertice data
        polyline_attribute = water_line_obj.find('polyline')
        if polyline_attribute == None : continue
        points_string = polyline_attribute.get('points')
        line_points = tiled_utils.GetPolyPoints(points_string)

        # Check
        new_vertice_str = MakeNewAlignment(line_points)
        if new_vertice_str == None: continue
        count_need_alignment += 1

        # Apply changes
        polyline_attribute.set('points', new_vertice_str)

    # End messages
    log.Info("--------------------------------------------------")
    log.Must(f'Aligned {count_need_alignment} waterlines')

    log.Must("\n--- cli_water has finished! ---\n")





#--------------------------------------------------#
'''Utility'''

def MakeNewAlignment(line_points):
    '''Return a new str if the line needs alignment'''

    # Obtain vertex values
    [x1, y1], [x2, y2] = line_points
    x_diff = x2-x1
    y_diff = y2-y1
    log.Extra(f"Bef - ({x1}, {y1}) ~ ({x2}, {y2})")


    # No change needed - Line is already perfectly aligned
    if x_diff == 0:
        log.Info(CHAR_FALSE + "Line is completely vertical")
        return None
    if y_diff == 0:
        log.Info(CHAR_FALSE + "Line is completely horizontal")
        return None


    # Check if slope is greater or less than 1
    slope = y_diff / x_diff
    slope *= slope # Remove negative sign
    if slope == 1:
        log.Info(CHAR_FALSE + "Cannot determine line's snapping axis")
        return None
    elif slope > 1:
        log.Info(CHAR_TRUE + "Line should snap to y-axis (vertical)")
        return MakeAlignedStr(line_points, True)
    else:
        log.Info(CHAR_TRUE + "Line should snap to x-axis (horizontal)")
        return MakeAlignedStr(line_points, False)


    # Default, should be impossible to reach
    return None



def MakeAlignedStr(line_points, is_vertical):
    '''Alter the x-/y-position of the 2nd vertex to match the 1st'''
    [x1, y1], [x2, y2] = line_points

    # Alignment
    new_x = x2
    new_y = y2
    if is_vertical: new_x = x1
    else: new_y = y1
    new_str_value = f"{x1},{y1} {new_x},{new_y}"

    # Logging
    log.Extra(f"Aft - ({x1}, {y1}) ~ ({new_x}, {new_y})")
    return new_str_value



#--------------------------------------------------#










# End of File