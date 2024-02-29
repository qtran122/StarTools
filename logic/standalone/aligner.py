'''
Aligner scans the whole level, then process all objects with name as "water_line".


USAGE EXAMPLE:
    aligner.AlignWater(playdo)
'''

import xml.etree.ElementTree as ET
import logic.common.log_utils as log

#--------------------------------------------------#
'''Config'''

# Enumerator
STATE_INV = 0
STATE_HOR = 1
STATE_VER = 2

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
    for water_line_obj in list_of_all_water_lines:
        if water_line_obj != list_of_all_water_lines[0]:
            log.Extra("--------------------------------------------------")

        # Obtain vertice data
        polyline_attribute = water_line_obj.find('polyline')
        if polyline_attribute == None : continue
        points_string = polyline_attribute.get('points')
        line_tuple = GetVertexTuple(points_string)

        # Check
        obj_state = CheckNeedAlignment(line_tuple)
        if obj_state == STATE_INV: continue
        count_need_alignment += 1
        new_vertice_str = MakeAlignedStr(obj_state, line_tuple)

        # Apply changes
        polyline_attribute.set('points', new_vertice_str)

    # End messages
    log.Info("--------------------------------------------------")
    log.Must(f'Aligned {count_need_alignment} waterlines')

    log.Must("\n--- cli_water has finished! ---\n")



#--------------------------------------------------#
'''Utility'''


def GetVertexTuple( line_vertice ):
    '''Convert string into tuple of integers: [ [x1,y1], [x2,y2] ]'''

    # Convert raw string into tuples
    list_point = line_vertice.split(" ")
    point1 = list_point[0].split(",")
    point2 = list_point[1].split(",")

    # Convert tuples from string to int
    result = []
    result.append( [ int(point1[0]), int(point1[1]) ] )
    result.append( [ int(point2[0]), int(point2[1]) ] )

    return result



def MakeAlignedStr(obj_state, line_tuple):
    '''Alter the x-/y-position of the 2nd vertex to match the 1st'''
    x1 = line_tuple[0][0]
    y1 = line_tuple[0][1]
    x2 = line_tuple[1][0]
    y2 = line_tuple[1][1]

    # Alignment
    new_x = x2
    new_y = y2
    if obj_state == STATE_VER: new_x = x1
    elif obj_state == STATE_HOR: new_y = y1
    new_str_value = f"{x1},{y1} {new_x},{new_y}"

    # Logging
    log.Extra(f"Aft - ({x1}, {y1}) ~ ({new_x}, {new_y})")
    return new_str_value



def CheckNeedAlignment(line_tuple):
    '''Return the state indicating whether the line needs alignment'''

    # Obtain vertex values
    x1 = line_tuple[0][0]
    y1 = line_tuple[0][1]
    x2 = line_tuple[1][0]
    y2 = line_tuple[1][1]
    x_diff = x2-x1
    y_diff = y2-y1
    log.Extra(f"Bef - ({x1}, {y1}) ~ ({x2}, {y2})")


    # No change needed - Line is already perfectly aligned
    if x_diff == 0:
        log.Info(CHAR_FALSE + "Line is completely vertical")
        return STATE_INV
    if y_diff == 0:
        log.Info(CHAR_FALSE + "Line is completely horizontal")
        return STATE_INV


    # Check if slope is greater or less than 1
    slope = y_diff / x_diff
    slope *= slope # Remove negative sign
    if slope == 1:
        log.Info(CHAR_FALSE + "Cannot determine line's snapping axis")
        return STATE_INV
    elif slope > 1:
        log.Info(CHAR_TRUE + "Line should snap to y-axis (vertical)")
        return STATE_VER
    else:
        log.Info(CHAR_TRUE + "Line should snap to x-axis (horizontal)")
        return STATE_HOR


    # Default, should be impossible to reach
    return STATE_INV



#--------------------------------------------------#










# End of File