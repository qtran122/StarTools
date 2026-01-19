'''
Command-Line Tool for rotating all tilelayers by 180˚
 1. Select all tiles of a tilelayer
 2. "Press [Z]" 2 times
 3. Apply this to all tilelayers

USAGE EXAMPLE:
    python cli_invert.py z01 --v 0
    clear; python cli_invert.py z01 --v 0

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.tiled_utils as tiled_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play

#--------------------------------------------------#
'''Adjustable Configurations'''





#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and rotate all the tilelayer contents by 180˚'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help1)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Use a playdo to read/process the XML
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # Main Logic
    for layer_name in playdo.GetAllTileLayerNames():
        tiles2d = playdo.GetTiles2d(layer_name)
        tiles2d = tiled_utils.RotateTiles2d(tiles2d)
        tiles2d = tiled_utils.RotateTiles2d(tiles2d)
        playdo.SetTiles2d(layer_name, tiles2d)

    # Flush changes to File!
    playdo.Write()





#--------------------------------------------------#

main()










# End of File