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
CHAR_TRUE  = "  O "
CHAR_FALSE = "  X "



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
    for index, water_line_obj in enumerate(list_of_all_water_lines):
        if index != 0:
            log.Extra("--------------------------------------------------")

        # Obtain vertice data
        line_points = tiled_utils.GetPolyPointsFromObject(water_line_obj)
        if line_points == None : continue

        # Check
        new_vertice_str = MakeNewAlignment(line_points)
        if new_vertice_str == None: continue
        count_need_alignment += 1

        # Apply changes
        polyline_attribute = water_line_obj.find('polyline')
        water_line_obj.find('polyline').set('points', new_vertice_str)

    # End messages
    log.Info("--------------------------------------------------")
    log.Must(f'Aligned {count_need_alignment} waterlines')

    log.Must("\n--- cli_water has finished! ---\n")





#--------------------------------------------------#
'''Utility'''

def MakeNewAlignment(line_points):
    '''Return a new str if the line needs alignment'''

    # Obtain vertex values
    (x1, y1), (x2, y2) = line_points
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
        log.Extra(f"Aft - ({x1}, {y1}) ~ ({x1}, {y2})") # same x-value
        return f"{x1},{y1} {x1},{y2}"
    else:
        log.Info(CHAR_TRUE + "Line should snap to x-axis (horizontal)")
        log.Extra(f"Aft - ({x1}, {y1}) ~ ({x2}, {y1})") # same y-value
        return f"{x1},{y1} {x2},{y1}"


    # Default, should be impossible to reach
    return None



#--------------------------------------------------#










# End of File