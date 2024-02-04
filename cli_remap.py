""" Command-Line Tool to 'remap' (or 'reskin') a level according to a remap file
    
    USAGE EXAMPLE: "python cli_remap.py d51 remap_cave"
"""
import argparse
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.remapper.tile_remapper as TM

# Use argparse to get the filename & other optional arguments from the command line
parser = argparse.ArgumentParser(description='Reskins a tiled level XML according to the remap file provided.')
parser.add_argument('file_name', type=str, help='Name of the tiled level XML to remap')
parser.add_argument('pattern_name', type=str, help='Name of the remap/reskin XML from which to obtain remapping info')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

# Use a playdo to read/process the XML
playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.file_name))

# Create a TileRemapper and load it with the specified remap instructions
tile_remapper = TM.TileRemapper()
tile_remapper.LoadRemapXml(file_utils.GetFullRemapPath(args.pattern_name))

# Perform the matching - mold the playdo
tile_remapper.Remap(playdo)

# Flush changes to File!
playdo.Write()
