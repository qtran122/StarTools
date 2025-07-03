'''
Command-Line Tool to combine any multiple object layers of a TILED level if they use the same name

SETUP EXAMPLE:
    Inside the level XML, multiple object layers may result with the same name (for example,
    due to stacked uses of the cli_dupe tool). It's often advantageous to keep the layers
    separate for ease of working. But at the end, to combine them all can be cumbersome,
    which is where this tool comes in.
    
    Example tile layer setup in a level XML:
    - objects_water             # A object layer to be combined
    - objects_water             # Another object layer to be combined

USAGE EXAMPLE:
	python cli_merge.py l16.xml
'''

import argparse
import logic.common.file_utils as file_utils
import logic.common.level_playdo as play
import logic.common.log_utils as log
import xml.etree.ElementTree as ET

# Use argparse to get the filename & other optional arguments from the command line
parser = argparse.ArgumentParser(description='Combine two or more object groups of a tiled level XML')
parser.add_argument('file_name', type=str, help='Name of the tiled level XML to swap layers')
parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help='Verbosity level: 0 = silent. 2 = verbose')
parser.add_argument('--w', action='store_true', help='Indicates we want to proceed with the operation. Otherwise, this is a test run')
args = parser.parse_args()

log.SetVerbosityLevel(args.v)
log.Info(f'Running cli_mergegroup on LEVEL {args.file_name}...\n')


def _ProcessObjectGroup(objectgroups, wider_objectgroup_map, parent, parent_map):
    # Goes through a list of objectgroups and adds their entries to the wider map
    # wider map maps objectgroup_name STRING to a LIST of object group XML element tree objs
    for objectgroup in objectgroups:
        objectgroup_name = objectgroup.get('name')
        #print(objectgroup.get('name'))
        if objectgroup_name in wider_objectgroup_map:
            wider_objectgroup_map[objectgroup_name].append(objectgroup)
        else:
            wider_objectgroup_map[objectgroup_name] = [objectgroup]
        parent_map[objectgroup] = parent

def main():
    playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.file_name))
    edits_made = False # Dirty Flag to track if we should flush edits later
    
    wider_objectgroup_map = {} # Maps object group name to an XML element tree
    parent_map = {} # maps objectgroup element tree obj to its parent. We maintain the parent map to
                    # know where to remove the original object group from if proceeding with merging
    # Fill the wider_objectgroup_map. We need to scan one level deep (only one layer of folders is supported)
    
    # First, scan the top-level for all object groups OUTSIDE of folders
    objectgroups = playdo.level_root.findall('objectgroup')
    _ProcessObjectGroup(objectgroups, wider_objectgroup_map, playdo.level_root, parent_map)
    
    # Second, scan inside folders for objectgroups outside of folders
    folders = playdo.level_root.findall('group')
    for folder in folders:
        objectgroups = folder.findall('objectgroup')    
        _ProcessObjectGroup(objectgroups, wider_objectgroup_map, folder, parent_map)
        
    # Merge opportunities are where objectgroups share the same name
    merge_opportunities = [];
    for objgrp_name, objgrps in wider_objectgroup_map.items():
        if len(objgrps) > 1:
            merge_opportunities.append(objgrp_name)
            log.Info(f"    '{objgrp_name}' : Shared by {len(objgrps)} object groups")
    
    if not merge_opportunities:
        log.Info("No object groups were found to be sharing names")
        
    if not args.w:
        log.Info("\nIf you'd like to proceed with merging objectgroups, add --w")
        return
        
    for objectgroup_name in merge_opportunities:
        combined_group = ET.Element("objectgroup", name=objectgroup_name)
        
        objectgroups_to_combine = wider_objectgroup_map[objectgroup_name]
        for objectgroup in objectgroups_to_combine:
            for obj in objectgroup.findall("object"):
                combined_group.append(obj)
            parent = parent_map[objectgroup]
            parent.remove(objectgroup)
        
        playdo.level_root.append(combined_group)
        
    # Proceeding with merge operation. Flush changes to File!
    playdo.Write()


main()