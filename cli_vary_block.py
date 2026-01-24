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
import logic.common.tiled_utils as tiled
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import random


tool_desription = "Scans a level file for relic blocks and apply the custom properties of flip_x and angle"
arg_help_level = "Name of the tiled level XML"
ANGLE = [0, 90, 180, 270]
EXCLUDED_PREFIXES = ("VINE_", "REEF_", "FALL_", "TOTEM_", "MELON_")

def GetAllRelicBlocks(playdo):
    relic_blocks = playdo.GetAllObjectsWithName("relic_block")
    return relic_blocks

def ValidRelicBlocks(relic_block):
    block_type = tiled.GetPropertyFromObject(relic_block, "_type")
    if block_type and block_type.startswith(EXCLUDED_PREFIXES):
        return False
    return True

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
    parser.add_argument('filename', type=str, help=arg_help_level)
    parser.add_argument('--all', action='store_true', help='Scans ALL levels for relic blocks and apply the custom properties of flip_x and angle')
    args = parser.parse_args()
    
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))
    relic_blocks = GetAllRelicBlocks(playdo)
    if not relic_blocks:
        print(f"No relic blocks found inside Tiled level {args.filename}")
        return
    
    relic_blocks_to_configure = [relic_block for relic_block in relic_blocks if ValidRelicBlocks(relic_block)]
    for relic_block in relic_blocks_to_configure:
        tiled.RemovePropertyFromObject(relic_block, "autoset")
        tiled.RemovePropertyFromObject(relic_block, "flip_x")
        tiled.SetPropertyOnObject(relic_block, "angle", str(random.choice(ANGLE)))
        if random.choice([True, False]):
            tiled.SetPropertyOnObject(relic_block, "flip_x", " ")

    playdo.Write()
main()