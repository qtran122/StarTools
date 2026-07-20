'''
Command-Line Tool for ... TBA
	
USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python tool_spruce_notes.py z01 --v 2

'''
import argparse
import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import logic.common.tiled_utils as tiled_utils
import logic.common.backup_utils as backup_utils
import logic.common.level_playdo as play

#--------------------------------------------------#
'''Adjustable Configurations'''

# In-editor object layers for nodes & routes
note_layer_keyword = "note"
overflow_check     = "7"




#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and <TBA>'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
	parser.add_argument('filename', type=str, help = arg_help1)
	parser.add_argument('--rewind', action='store_true')
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Quick rewind
	if args.rewind:
		log.Must(f"Restoring backup for level \"{args.filename}\"")
		backup_utils.RestoreBackupViaName(file_utils.GetFullLevelPath(args.filename))
		return

	# Use a playdo to read/process the XML
	playdo = play.LevelPlayDo(file_utils.GetFullLevelPath(args.filename))

	# TODO
	list_objectgroup = playdo.GetAllObjectgroup()
	for objectgroup in list_objectgroup:
#		if not objectgroup.get("name").startswith(note_layer_keyword): continue
		if not note_layer_keyword in objectgroup.get("name"): continue
		for obj in objectgroup:
			if not is_notes_overflowing(obj): continue
			add_leading_zero(obj)

	# Flush changes to File!
	playdo.Write(make_auto_backup=True)



def GetAllPropertiesTuple(tiled_object):
	prop_elem = tiled_object.find('properties')
	if prop_elem is None: return []
	list_properties = []
	for property in prop_elem.findall('property'):
		list_properties.append( (property.get('name'), property.get('value')) )
	return list_properties



def is_notes_overflowing(obj):
	list_properties = GetAllPropertiesTuple(obj)
	is_overflowing = False
	for tuple in list_properties:
		old_name = tuple[0]
		if old_name[0] != overflow_check: continue
		is_overflowing = True
		break
	return is_overflowing

def add_leading_zero(tiled_object):
	list_properties = GetAllPropertiesTuple(tiled_object)
	for tuple in list_properties:
		old_name = tuple[0]
		value    = tuple[1]
		if not (old_name[0].isdecimal() and not old_name[1].isdecimal()): continue
		new_name = '0' + old_name
		rename_property(tiled_object, old_name, new_name)

def rename_property(tiled_object, old_name, new_name):
	prop_elem = tiled_object.find('properties')
	if prop_elem is None: return
	for property in prop_elem.findall('property'):
		if property.get('name') != old_name: continue
		property.set('name', new_name)
		break





#--------------------------------------------------#

main()










# End of File