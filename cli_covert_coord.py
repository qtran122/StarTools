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



tool_description = "Scans a level for original coord objects and convert these objects into point objects"
arg_help_level = "Named of the tiled level XML"


def FindCenter(x, y, w, h):
    center_x = x + (w // 2)
    center_y = y + (h // 2)
    return (x, y)

def ReplaceCoord(filename):
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(filename))
    coords = playdo.GetAllObjectsWithName("coord")
    for coord in coords:
        x = int(coord.get('x'))
        y = int(coord.get('y'))
        width = int(coord.get('width'))
        height = int(coord.get('height'))
        new_x, new_y = FindCenter(x, y, width, height)
        print(new_x)
        print(new_y)


def main():
    parser = argparse.ArgumentParser(description=tool_description)
    parser.add_argument('filename', type=str, help=arg_help_level, nargs='?')
    parser.add_argument('--all', action='store_true', help="")
    args = parser.parse_args()


    ReplaceCoord(args.filename)


main()

