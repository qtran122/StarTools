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
import os


tool_description = "Scans a level for original coord objects and convert these objects into point objects"
arg_help_level = "Name of the tiled level XML"
arg_help_all = "Convert coords for all level XML"
arg_help_exclude_sizes = "Ignore coords with width or height over a specific number. Default is 14.9"
default_exclude_size = 14.9
unconverted_files = []


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

def ConvertToPoint(coord):
    # get x, y, width, height values from original coord
    try:
        x = int(float(coord.get('x')))
        y = int(float(coord.get('y')))
        width = int(float(coord.get('width')))
        height = int(float(coord.get('height')))
    except (TypeError, ValueError) as e:
        raise ValueError(f"Coord object has missing x/y or width/height property: {e}")

    # calculate new x,y coordinates for point
    center_x = x + (width // 2)
    center_y = y + (height // 2)

    # extract the value from the "ref" custom property. This value will be the new name of the point object
    ref_name = tiled.GetPropertyFromObject(coord, "ref")
    if ref_name is None:
        raise ValueError(f"Coord at ({x}, {y}) is missing a 'ref' custom property")
    # update coordinates
    coord.set('x', str(center_x))
    coord.set('y', str(center_y))
    coord.set('name', ref_name)
    coord.set('type', "coord")

    # remove the old custom property, since we are renaming the new point object to the extracted ref value
    tiled.RemovePropertyFromObject(coord, 'ref')

    # delete width and height XML attribute
    del coord.attrib['width']
    del coord.attrib['height']

    ET.SubElement(coord, 'point')

def ReplaceCoord(filename, maxsize, full_path=False):
    if full_path: # when user runs --all, each level file is already an absolute path
        file_path = filename
    else: # for individual level, we need to return the absolute path
        file_path = file_utils.GetFullLevelPath(filename)

    if not os.path.exists(file_path):
        print(f"File not found, skipping: {file_utils.StripFilename(filename)}")
        raise Exception("File not found")

    playdo = play.LevelPlayDo(file_path)
    coords = playdo.GetAllObjectsWithName("coord")

    if not coords:
        print(f"No coord objects found in {file_utils.StripFilename(file_path)}")
        raise Exception("No coords object found")

    # only get coords with height or width that are smaller than or equal to a specified maxsize
    filtered_coords = [coord for coord in coords if float(coord.get('width')) <= maxsize * 16 and float(coord.get('height')) <= maxsize * 16]

    if not filtered_coords:
        print(f"No coords within size limit, skipping {file_utils.StripFilename(file_path)}")
        return

    for num, coord in enumerate(filtered_coords):
       ConvertToPoint(coord)
    playdo.Write()


def main():
    parser = argparse.ArgumentParser(description=tool_description)
    parser.add_argument('filename', type=str, help=arg_help_level, nargs='?')
    parser.add_argument('--all', action='store_true', help=arg_help_all)
    parser.add_argument('--exclude_sizes_over', type=float, default=default_exclude_size, help=arg_help_exclude_sizes)
    args = parser.parse_args()

    if args.all:
        level_files = file_utils.GetAllLevelFiles()
        print(f"Converting coords for {len(level_files)} levels")
        for num, level_file in enumerate(level_files):
            try:
                ReplaceCoord(level_file, args.exclude_sizes_over, full_path=True)
            except Exception as e:
                unconverted_files.append(file_utils.StripFilename(level_file))
            PrintProgressBar(num + 1, len(level_files), prefix="Converting Coords Progress", suffix=f"processing {_FormatName(level_file)}")
        
        if unconverted_files:
            print(f"Unable to convert {len(unconverted_files)} files")
            # for file in unconverted_files:
            #     print(f"unable to complete cli_convert_coords on {file}")
    else:
        if not args.filename:
            parser.error("File name is required when not using --all")
        print(f"Converting coords for file level {args.filename}")
        ReplaceCoord(args.filename, args.exclude_sizes_over)
      

        

    time.sleep(0.25)
    
   
    



main()

