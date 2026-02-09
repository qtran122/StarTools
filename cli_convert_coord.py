"""
Command-Line Tool for converting original coord objects into Tiled insert point object

Goals:
    1. find all existing coord objects
    2. replace original coord objects with new point object
    3. change point objects location coordinate (x, y) and its name


"""
import time
import sys
import argparse
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.common.tiled_utils as tiled
import xml.etree.ElementTree as ET


tool_description = "Scans a level for original coord objects and convert these objects into point objects"
arg_help_level = "Name of the tiled level XML"
arg_help_all = "Convert coords for all level XML"
arg_help_exclude_sizes = "Ignore coords with width or height over a specific number. Default is 14.9"


def PrintProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=50, fill='='):
    """Call in a loop to create terminal progress bar"""
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\r{prefix} |{bar}| {percent}% {suffix}')
    sys.stdout.flush()

def _FormatName(name):
    name = file_utils.StripFilename(name)
    if len(name) > 20:
        # Truncate and add "..." to the end
        formatted_name = name[:17] + "..."
    else:
        # Pad with spaces to make it 20 characters
        formatted_name = name.ljust(20)
    return formatted_name

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
    parser.add_argument('--all', action='store_true', help=arg_help_all)
    parser.add_argument('--exclude_sizes_over', type=int, default=14.9, help=arg_help_exclude_sizes)
    args = parser.parse_args()

    if args.all:
        level_files = file_utils.GetAllLevelFiles()
        print(f"Converting coords for {len(level_files)} levels")
        for num, level_file in enumerate(level_files):
            ReplaceCoord(level_file)
            PrintProgressBar(num + 1, len(level_files), prefix="Converting Coords Progress", suffix=f"processing {_FormatName(level_files)}")
        
    else:
        if not args.filename:
            parser.error("File name is required when not using --all")
        print(f"Converting coords for file level {args.filename}")
        ReplaceCoord(args.filename)
        

    time.sleep(0.25)
    print("Coordinates conversion complete")
   
    



main()

