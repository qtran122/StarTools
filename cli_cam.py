'''
Command-Line Tool for creating the reference tilelayer to simulate the range of in-game camera.
The tilelayer has parallax factor adjusted, such that the "frame" stays in the center of the editor.

The size inside the frame is either game's rough resolution (30x17) or a square (17x17)

USAGE EXAMPLE:
    python cli_cam.py z01
    python cli_cam.py z01 --square

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play
import logic.standalone.camera_framing as cam_logic

#--------------------------------------------------#
'''Adjustable Configurations'''

# Passing configurations to logic
LAYER_NAME = '_CAM_BOUNDS'
SIZE_RECT = (30,17)
SIZE_SQR  = (17,17)

FRAME_TILE_IDs = [1024, 1032]    # "Frame tiles"; Array length = Frame's thickness
# Tile ID is the same as shown within the Tiled app, when hovering cursor over a tile in any tilelayer
# Yon can expand and change the tiles used (i.e. frame color) as follows:
#  TILE_ID = [1024, 1032, 1033, 1034, 1035]





#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and create a tilelayer with camera reference for parallax'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'
arg_help3 = 'Type \'--square\' to print a square, instead of the default rectangle'



def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
    parser.add_argument('--square', action='store_true', help = arg_help3)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Use a playdo to read/process the XML
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # Main Logic
    size = SIZE_RECT
    if args.square : size = SIZE_SQR
    cam_logic.AddCameraFrameToLevel(playdo, size, FRAME_TILE_IDs, LAYER_NAME)

    # Flush changes to File!
    playdo.Write()





#--------------------------------------------------#

main()










# End of File