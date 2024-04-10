'''
Command-Line Tool to swap two layers of a TILED level by using a third layer as input

SETUP EXAMPLE:
    Inside the level XML, to swap select spots of 2 tile layers, create a 3rd tile layer
    that is named "SWAP#X#Y", where X & Y are the names of the two layers to be swapped.
    Paint in this 3rd tile layer spots that you want to be swapped between the 2 layers.
    After finishing, run the python cli_swap.py tool.
    
    Example tile layer setup in a level XML:
    - fg_ground                     # This is a tile layer to be swapped
    - fg mesh                       # This is another tile layer to be swapped
    - SWAP # fg mesh # fg_ground    # this is the 3rd layer - it specifies the layers to swap

USAGE EXAMPLE:
	python cli_swap.py j24.xml
'''

import argparse
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.common.log_utils as log
import logic.standalone.tile_swapper as tile_swapper


# Use argparse to get the filename & other optional arguments from the command line
parser = argparse.ArgumentParser(description='Swap two layers of a tiled level XML according to the input layer.')
parser.add_argument('file_name', type=str, help='Name of the tiled level XML to swap layers')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

log.SetVerbosityLevel(args.v)
log.Info(f'Running cli_swap on LEVEL {args.file_name}...')

# Use a playdo to read/process the XML
playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.file_name))

# Perform the matching - mold the playdo
result = tile_swapper.Swap(playdo)

# Flush changes to File!
if result: playdo.Write()
