"""
Command-Line Interface Tool to quickly duplicate (copy) graphical tile layers from one level into another.
The tile layers will be copied if they're "visible" in TILED. This saves on the trouble of manually
creating tile layers in a level, switching tabs, copying, pasting, renaming, etc.

USAGE EXAMPLE:
    python cli_dupe_tiles.py l02
"""
import argparse
import xml.etree.ElementTree as ET
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.common.log_utils as log
import logic.common.tiled_utils as tiled_utils

# Tile ID for the fuzz layer
FUZZ_TILE_ID = 1288

# Use argparse to get the filename & other optional arguments from the command line
parser = argparse.ArgumentParser(description='Duplicates tile layers from "_dupe.xml" into specified level')
parser.add_argument('filename', type=str, help='Name of the tiled level XML to paste tile layers into')
parser.add_argument('--src', type=str, default='_dupe', help='Name of the SRC level XML to copy tile layers from')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

log.SetVerbosityLevel(args.v)
log.Info(f'Running cli_dupe_tiles on LEVEL {args.filename}...')

# Use a playdo to read/process the XML
def main():
    playdo_src = play.LevelPlayDo(file_utils.GetFullLevelPath(args.src))
    playdo_dest = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))
    edits_made = False # Dirty Flag to track if we should flush edits later

    # Create a folder in the destination to hold all copied tile layers
    folder_name = f'adj_level_{args.src}'
    dest_folder = ET.SubElement(playdo_dest.level_root, 'group', {'name': folder_name})

    # Get SRC level's tile layers. Note: we intentionally only do a surface-level traversal.
    # This is to avoid awkward scenarios like copying visible tile layers inside invisible folders, etc.
    src_tile_layers = playdo_src.level_root.findall('layer')
    fuzz_tiles2d = None 
    for tile_layer in src_tile_layers:
        # if something is visible, the property is not listed, hence NONE is our check for visibility
        is_visible = tile_layer.get('visible') == None
        src_layer_name = tile_layer.get('name')
        has_valid_prefix = src_layer_name.startswith('fg_') or src_layer_name.startswith('bg_')
        log.Info(f'TILE LAYER {src_layer_name} / {is_visible} / {has_valid_prefix}')
        if is_visible and has_valid_prefix:
            edits_made = True
            # Rename the layer so it's prefixed with the src level name (e.g. "_a01_bg_context_15k")
            tile_layer.set('name', f'_{args.src}_{src_layer_name}')
            # Append the tile layer into the destination folder
            dest_folder.append(tile_layer)

            data_str = tile_layer.find('data').text.strip()
            tiles2d = tiled_utils.DecodeIntoTiles2d(data_str, playdo_src.map_width)
            if fuzz_tiles2d is None:
                fuzz_tiles2d = [[0 for _ in row] for row in tiles2d]
            for y, row in enumerate(tiles2d):
                for x, cell in enumerate(row):
                    if cell != 0:
                        fuzz_tiles2d[y][x] = FUZZ_TILE_ID

    # Add a single fuzz overlay layer on top of all the copied layers
    if edits_made:
        fuzz_data_str = tiled_utils.EncodeToTiledFormat(fuzz_tiles2d)
        fuzz_layer = ET.SubElement(dest_folder, 'layer', {
            'name': "_fuzz_",
            'width': str(playdo_src.map_width),
            'height': str(playdo_src.map_height),
            'opacity': '0.2',
        })
        fuzz_data = ET.SubElement(fuzz_layer, 'data', {'encoding': 'base64', 'compression': 'zlib'})
        fuzz_data.text = fuzz_data_str

    # Remove the folder if no layers were copied into it
    if not edits_made:
        playdo_dest.level_root.remove(dest_folder)
        log.Must("edits NOT made!")
    else:
        log.Must("edits made!")
        playdo_dest.Write()

main()
