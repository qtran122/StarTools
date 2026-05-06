import logic.common.tiled_utils as tiled
import logic.common.level_playdo as play
import random
ANGLE = [0, 90, 180, 270]
EXCLUDED_PREFIXES = ("VINE_", "REEF_", "FALL_", "TOTEM_", "MELON_")



def GetAllBreakBlocks(playdo):
    break_blocks = playdo.GetAllObjectsWithName("break_block")
    return break_blocks

def ValidBreakBlocks(break_block):
    block_type = tiled.GetPropertyFromObject(break_block, "_type")
    if block_type and block_type.startswith(EXCLUDED_PREFIXES):
        return False
    return True


def VaryBreakBlocksFromFile(file_path):
    playdo = play.LevelPlayDo(file_path)
    VaryBreakBlocks(playdo)
    playdo.Write()


def VaryBreakBlocks(playdo):
    break_blocks = GetAllBreakBlocks(playdo)

    if not break_blocks:
        return
    
    break_blocks_to_configure = [break_block for break_block in break_blocks if ValidBreakBlocks(break_block)]
    for break_block in break_blocks_to_configure:
        tiled.RemovePropertyFromObject(break_block, "autoset")
        tiled.RemovePropertyFromObject(break_block, "flip_x")
        tiled.SetPropertyOnObject(break_block, "angle", str(random.choice(ANGLE)))
        if random.choice([True, False]):
            tiled.SetPropertyOnObject(break_block, "flip_x", "")