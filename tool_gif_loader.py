'''
Command-Line Tool for exporting GIFs into individual frames of PNGs
It's the pre-requisites for using dev_load to load GIF in Unity project
	
USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python tool_gif_loader.py --v 2
'''
import argparse
import logic.common.log_utils as log
import os
from PIL import Image

#--------------------------------------------------#
'''Shared with Unity'''
# When attempting to change these values, make sure the changes are matched in the Unity module as well

# Folder Directories
FOLDER_GIF    = "/Users/Jimmy/Desktop/PSD/dev_load_gif/"
FOLDER_FRAMES = "/Users/Jimmy/Desktop/PSD/dev_load_frames/"

# Naming Conventinos
SPLIT_CHAR = '-'

# Extensions
EXTENSION_I = '.gif'
EXTENSION_O = '.png'





#--------------------------------------------------#
'''Main'''

arg_description = 'Process a tiled level XML and <TBA>'
arg_help1 = 'Name of the tiled level XML'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Loop through all the GIF in folder, export only if needed
	# Use argparse to get the filename & other optional arguments from the command line
	list_gif    = os.listdir(FOLDER_GIF)
	list_frames = _GetSlicedFrames()
	for filename in list_gif:
		# Ignore non-GIF
		if not filename.endswith(EXTENSION_I): continue

		# Ignore GIF already sliced
		name_without_extension = filename.split('.')[0]
		if name_without_extension in list_frames: continue

		# Export for GIF not yet sliced
		_ExportGifToFrames(name_without_extension)
#		print(name_without_extension)





def _GetSlicedFrames():
	list_frames = []
	entries = os.listdir(FOLDER_FRAMES)
	for filename in entries:
		if not filename.endswith(EXTENSION_O): continue
		prefix = filename.split(SPLIT_CHAR)[0]
		if prefix in list_frames: continue
		list_frames.append(prefix)
	return list_frames

def _ExportGifToFrames(name):
	path_raw_gif       = f'{FOLDER_GIF}{name}{EXTENSION_I}'
	log.Must(f'\"{path_raw_gif}\" will be exported...')

	# Open the animated GIF
	with Image.open(path_raw_gif) as img:
		# Basic data
		num_frames = img.n_frames
		frame_duration = int(img.info.get('duration', 0) * (60 / 1000))

		# Output path name
		if SPLIT_CHAR in name: name = name.replace(SPLIT_CHAR, "")
		path_frames_prefix = f'{FOLDER_FRAMES}{name}{SPLIT_CHAR}'
		path_frames_prefix += f'{frame_duration}{SPLIT_CHAR}'
		path_frames_prefix += f'{num_frames}{SPLIT_CHAR}'
#		return

		# Iterate over every frame in the GIF
		for i in range(img.n_frames):
			num_str = ''
			if num_frames >= 10  and i < 10:  num_str += '0'
			if num_frames >= 100 and i < 100: num_str += '0'
			num_str += f'{i}'

			curr_name = f'{path_frames_prefix}{num_str}{EXTENSION_O}'
			log.Extra(f'  {curr_name}')
#			continue

			# Convert to RGBA to ensure transparency is preserved
			img.seek(i)
			frame = img.convert("RGBA")
			frame.save(curr_name)
#			break

	log.Must('')









#--------------------------------------------------#

main()










# End of File