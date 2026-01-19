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


