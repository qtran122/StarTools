"""
Docstring for cli_vary_block
relic blocks have 2 properties
1) angle
2) flip_x

some blocks rotation configurations are bad (player can seem like they are floating when standing on blocks, due to blocks having gaps)
angle = [0, 90, 180, 270] will be randomly picked
flip_x = blocks may or may not have this property (50% chance of having)


goals:
    1) set angle and/or flip_x properties across all blocks inside a level
    2) allow users to reroll blocks configuration if re-run this tool multiple times

    
Pseudo Algo
1) scan level file for relic_blocks
2) remove the "autoset property from these blocks
3) a block will have 50% chance of having the flip_x property
4 all blocks will have an angle property where each angle can be [0, 90, 180, 270]
"""

import argparse
import logic.common.level_playdo as play


arg_desription = "Scans a level file for relic blocks and apply the custom properties of flip_x and angle"
arg_help1 = "Name of the tiled level XML"

def GetAllRelicBlocks(playdo):
    obj_grps = playdo.GetAllObjectgroup(is_print=False)
    layers_w_collision = []
    relic_blocks = []
    for obj_grp in obj_grps:
        group_name = obj_grp.get("name", "")
        if group_name.startswith("collisions"):
            layers_w_collision.append(obj_grp)
        if group_name.startswith("objects"):
            for shape in obj_grp:
                if shape.get("name") == "relic_block":
                    relic_blocks.append(shape)
    for obj_grp in layers_w_collision:
        for shape in obj_grp:
            if shape.get("name") == "relic_block":
                relic_blocks.append(shape)
    return relic_blocks

def main():
    parser = argparse. ArgumentParser(description=arg_desription)
    parser.add_argument('filename', type=str, help=arg_help1)
    args = parser.parse_args()
    print(f"Running for cli_vary_block on Tiled level {args.filename}")

    playdo = play.LevelPlayDo(args.filename)
    relic_blocks = GetAllRelicBlocks(playdo)

    if not relic_blocks:
        print(f"No relic blocks found inside Tiled level {args.filename}")
        return;
    


main();