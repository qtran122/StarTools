import logic.common.level_playdo as play
import logic.common.tiled_utils as tiled
import logic.common.file_utils as file_utils
import random
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


def VaryRelicBlocks(filename):
    if filename.endswith('.xml') or filename.endswith('.tmx'):
        playdo = play.LevelPlayDo(filename)
    else:
        playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(filename))
    relic_blocks = GetAllRelicBlocks(playdo)

    if not relic_blocks:
        return
    
    relic_blocks_to_configure = [relic_block for relic_block in relic_blocks if ValidRelicBlocks(relic_block)]
    for relic_block in relic_blocks_to_configure:
        tiled.RemovePropertyFromObject(relic_block, "autoset")
        tiled.RemovePropertyFromObject(relic_block, "flip_x")
        tiled.SetPropertyOnObject(relic_block, "angle", str(random.choice(ANGLE)))
        if random.choice([True, False]):
            tiled.SetPropertyOnObject(relic_block, "flip_x", "")
    playdo.Write()