"""
Command-Line Tool for varying the angle & flipped-ness of relic block objects within a level

Relic blocks can have 2 custom properties
1. angle 
2. flip_x
angle = [0, 90, 180, 270] angle degree will be randomly picked
flip_x = relic blocks may or may not have this property (50% chance of having)

Varying block rotation & flipped configurations prevents block patterns from looking visually stale. Furthermore, some blocks rotation configurations are bad (player can seem like they are floating when standing on blocks, due to blocks having gaps).

Goals:
    1. set angle and/or flip_x properties across all blocks inside a level
    2. allow users to reroll blocks configuration if re-run this tool multiple times

Pseudo Algo
1. scan level file for relic_blocks
2. remove the "autoset property from these blocks
3. a block will have 50% chance of having the flip_x property
4. all blocks will have an angle property where each angle can be [0, 90, 180, 270]
"""

import sys
import argparse
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.standalone.vary_block as VB
import time


tool_desription = "Scans a level file for relic blocks and apply the custom properties of flip_x and angle"
arg_help_level = "Name of the tiled level XML"
arg_help_all = "Scans ALL levels for relic blocks and apply the custom properties of flip_x and angle"


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




def main():
    parser = argparse.ArgumentParser(description=tool_desription)
    parser.add_argument('filename', type=str, help=arg_help_level, nargs='?')
    parser.add_argument('--all', action='store_true', help=arg_help_all)
    args = parser.parse_args()
    
    if args.all:
        level_files = file_utils.GetAllLevelFiles()
        print(f"Varying relic blocks for {len(level_files)} level files")
        for num, level_file in enumerate(level_files):
            playdo = play.LevelPlayDo(level_file)
            VB.VaryRelicBlocks(playdo)
            playdo.Write()
            PrintProgressBar(num + 1, len(level_files), prefix='Varying Progress:', suffix=f'processing {_FormatName(level_file)}')
    else:
        if not args.filename:
            parser.error("File name is required when not using --all")
        print(f"Varying relic blocks for {args.filename}")
        level_file = file_utils.GetFullLevelPath(args.filename)
        playdo = play.LevelPlayDo(level_file)
        VB.VaryRelicBlocks(playdo)
        playdo.Write()
    
    
    time.sleep(0.25)
    print("Finished varying all relic blocks")
            
main()