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

import argparse
import logic.common.level_playdo as play
import logic.common.tiled_utils as tiled
import logic.common.file_utils as file_utils
import random


tool_desription = "Scans a level file for relic blocks and apply the custom properties of flip_x and angle"
arg_help_level = "Name of the tiled level XML"
angle = [0, 90, 180, 270]

def GetAllRelicBlocks(playdo):
    relic_blocks = playdo.GetAllObjectsWithName("relic_block")
    print(f"There are {len(relic_blocks)} relic blocks")
    return relic_blocks

def main():
    parser = argparse. ArgumentParser(description=tool_desription)
    parser.add_argument('filename', type=str, help=arg_help_level)
    args = parser.parse_args()
    print(f"Running for cli_vary_block on Tiled level {args.filename}")

    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))
    relic_blocks = GetAllRelicBlocks(playdo)

    if not relic_blocks:
        print(f"No relic blocks found inside Tiled level {args.filename}")
        return;
    
    for relic_block in relic_blocks:
        tiled.RemovePropertyFromObject(relic_block, "autoset")
        tiled.SetPropertyOnObject(relic_block, "angle", str(random.choice(angle)))
        if random.choice([True, False]):
            tiled.SetPropertyOnObject(relic_block, "flip_x", "true")

    playdo.Write()
main();