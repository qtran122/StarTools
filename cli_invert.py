'''
Command-Line Tool for inverting a level vertically or rotating all tilelayers by 180˚
This is intended as a helper tool to help design levels that deal with gravity inversion.
Note, this tool only affects the graphical tile layers and does not touch object layers

USAGE EXAMPLE:
    python cli_invert.py r05                # flips the level vertically
    python cli_invert.py r05 --rotate       # rotates the level 180 degrees

'''
import argparse
import logic.common.file_utils as file_utils
import logic.common.tiled_utils as tiled_utils
import logic.common.log_utils as log
import logic.common.level_playdo as play


#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and rotate all the tilelayer contents by 180˚'
arg_help_lvl = 'Name of the tiled level XML'
arg_help_log = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'
arg_help_rotate = 'instructs the tool to rotate the level instead of flip'


def main():
    # Use argparse to get the filename & other optional arguments from the command line
    parser = argparse.ArgumentParser(description = arg_description)
    parser.add_argument('filename', type=str, help = arg_help_lvl)
    parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help_log)
    parser.add_argument('--rotate', action='store_true', help=arg_help_rotate)
    
    args = parser.parse_args()
    log.SetVerbosityLevel(args.v)

    # Use a playdo to read/process the XML
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

    # Main Logic
    for layer_name in playdo.GetAllTileLayerNames():
        tiles2d = playdo.GetTiles2d(layer_name)
        
        tiles2d = tiled_utils.RotateTiles2d(tiles2d)
        tiles2d = tiled_utils.RotateTiles2d(tiles2d)
        
        # "inverting" is accomplished by two rotations & then a flipX, because we don't have a flipY
        if not args.rotate:
            tiles2d = tiled_utils.FlipTiles2d(tiles2d)
            
        playdo.SetTiles2d(layer_name, tiles2d)

    # Flush changes to File!
    playdo.Write()





#--------------------------------------------------#

main()










# End of File