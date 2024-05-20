"""
Command-Line Interface Tool to quickly duplicate (copy) object and group layers from one level into another.
The objects and folders will be copied if they're "visible" in TILED. This saves on the trouble of manually
creating object groups in a level, switching tabs, copying, pasting, renaming, etc.
    
USAGE EXAMPLE: 
    python cli_dupe.py l02
"""
import argparse
import random
import logic.common.level_playdo as play
import logic.common.file_utils as file_utils
import logic.pattern.pattern_matcher as PM
import logic.common.log_utils as log

# Use argparse to get the filename & other optional arguments from the command line
parser = argparse.ArgumentParser(description='Duplicates layers and groups from "_dupe.xml" into specified level')
parser.add_argument('filename', type=str, help='Name of the tiled level XML to paste objects into')
parser.add_argument('--src', type=str, default='_dupe', help='Name of the SRC level XML to copy objects from')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
args = parser.parse_args()

log.SetVerbosityLevel(args.v)
log.Info(f'Running cli_dupe on LEVEL {args.filename}...')

# Use a playdo to read/process the XML
def main():
    playdo_src = play.LevelPlayDo(file_utils.GetFullLevelPath(args.src))
    playdo_dest = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))
    edits_made = False # Dirty Flag to track if we should flush edits later

    # Get SRC level's objectgroups &  folders. Note: we intentionally only do a surface-level traversal.
    # This is to avoid awkward scenarios like copying visible objectgroups inside invisible folders, etc.
    src_object_groups = playdo_src.level_root.findall('objectgroup')
    for object_group in src_object_groups:
        # if something is visible, the property is not listed, hence NONE is our check for visibility
        is_visible = object_group.get('visible') == None 
        log.Info(f'OBJ LAYER {object_group.get("name")} / {is_visible}')
        if is_visible:            
            edits_made = True
            src_layer_name = object_group.get('name')
            dest_object_group = playdo_dest.GetObjectGroup(src_layer_name, discard_old = False)
            for object in object_group:
                dest_object_group.append(object)
    
    
    src_folders = playdo_src.level_root.findall('group')
    dest_map = playdo_dest.level_root
    for folder in src_folders:
        # if something is visible, the property is not listed, hence NONE is our check for visibility
        is_visible = folder.get('visible') == None 
        log.Info(f'FOLDER {folder.get("name")} / {is_visible}')
        if is_visible:
            edits_made = True
            dest_map.append(folder)
            
    # Flush changes to File!
    if edits_made:
        log.Must("edits made!")
        playdo_dest.Write()
    else:
        log.Must("edits NOT made!")

main()