"""
Command-Line Tool for converting original coord objects into Tiled insert point object

Goals:
    1. find all existing coord objects
    2. replace original coord objects with new point object
    3. change point objects location coordinate (x, y) and its name


"""
import argparse
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.common.tiled_utils as tiled
import xml.etree.ElementTree as ET


tool_description = "Scans a level for original coord objects and convert these objects into point objects"
arg_help_level = "Named of the tiled level XML"


def ConvertToPoint(coord, index):
    # get x, y, width, height values from original coord
    x = int(coord.get('x'))
    y = int(coord.get('y'))
    width = int(coord.get('width'))
    height = int(coord.get('height'))

    # calculate new x,y coordinates for point
    center_x = x + (width // 2)
    center_y = y + (height // 2)

    # update coordinates
    coord.set('x', str(center_x))
    coord.set('y', str(center_y))
    coord.set('name', str(f"k{index}"))
    coord.set('type', "coord")

    # remove the old custom property, since we are renaming the new point object (k1, k2, k3 etc...)
    tiled.RemovePropertyFromObject(coord, 'ref')

    # delete width and height XML attribute
    del coord.attrib['width']
    del coord.attrib['height']

    ET.SubElement(coord, 'point')

def ReplaceCoord(filename):
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(filename))
    coords = playdo.GetAllObjectsWithName("coord")
    for num, coord in enumerate(coords):
       ConvertToPoint(coord, num + 1)
    playdo.Write()


def main():
    parser = argparse.ArgumentParser(description=tool_description)
    parser.add_argument('filename', type=str, help=arg_help_level, nargs='?')
    parser.add_argument('--all', action='store_true', help="")
    args = parser.parse_args()


    ReplaceCoord(args.filename)


main()

