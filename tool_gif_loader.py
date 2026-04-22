'''
Command-Line Tool for exporting GIFs into individual frames of PNGs
It's the pre-requisites for using dev_load to load GIF in Unity project
	
USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python tool_gif_loader.py --v 2
'''
import argparse
import logic.common.log_utils as log
import logic.common.file_utils as file_utils
import os
from PIL import Image

#--------------------------------------------------#
'''Shared with Unity'''
# When attempting to change these values, make sure the changes are matched in the Unity module as well

# Folder Directories
#  Home folder is where you put the PNGs and GIFs (to be loaded in Unity)
#  The other one is the hidden folder, which houses the pre-processed frames of GIFs

# TY's folders
#HOME_FOLDER              = r"/Users/Jimmy/Desktop/PSD/dev_load_gif"
#PREPROCESSED_GIFS_FOLDER = r"/Users/Jimmy/Desktop/PSD/dev_load_gif/_GIF"
# Quang's folders
HOME_FOLDER              = r"C:\\Users\\qtran\\Desktop\\Star Iliad Image Dev"
PREPROCESSED_GIFS_FOLDER = r"C:\\Users\\qtran\\Desktop\\Star Iliad Image Dev\\_GIF"



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
	list_gif    = os.listdir(HOME_FOLDER)
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
	'''
	 This function return a list of GIF names that have already been sliced previously
	'''
	list_exported_gif = []
	file_utils.CreateFolderAt(PREPROCESSED_GIFS_FOLDER)

	# Check if individual folders exist; If yes, it means the GIF has already been exported prior
	entries = os.scandir(PREPROCESSED_GIFS_FOLDER)
	for entry in entries:
		if not entry.is_dir(): continue
		list_exported_gif.append(entry.name)
	return list_exported_gif

def _ExportGifToFrames(name):
	'''
	 This function exports the raw GIF into individual frames as PNGs
	 The naming convention should be the same as how it's read in Unity
	'''
	gif_folder = file_utils.FixFolderPath(HOME_FOLDER)
	path_raw_gif = f'{gif_folder}{name}{EXTENSION_I}'
	log.Must(f' \"{path_raw_gif}\" will be exported...')

	# Open the animated GIF
	with Image.open(path_raw_gif) as img:
		# Basic data
		num_frames = img.n_frames
		frame_duration = int(img.info.get('duration', 0) * (60 / 1000))

		# Ensure name doesn't conflict with naming format, and folder directory will exist when exporting
		new_folder = file_utils.FixFolderPath(PREPROCESSED_GIFS_FOLDER)
		new_folder = f'{new_folder}{name}/'
		new_folder = file_utils.FixFolderPath(new_folder)

		# Output path name in specific format
		if SPLIT_CHAR in name: name = name.replace(SPLIT_CHAR, "")
		path_frames_prefix = f'{new_folder}{name}{SPLIT_CHAR}'
		path_frames_prefix += f'{frame_duration}{SPLIT_CHAR}'
		path_frames_prefix += f'{num_frames}{SPLIT_CHAR}'

		# Iterate over every frame in the GIF
		for i in range(img.n_frames):
			num_str = ''
			if num_frames >= 10  and i < 10:  num_str += '0'
			if num_frames >= 100 and i < 100: num_str += '0'
			num_str += f'{i}'
			curr_name = f'{path_frames_prefix}{num_str}{EXTENSION_O}'
			log.Extra(f'  {curr_name}')

			# Convert to RGBA to ensure transparency is preserved
			img.seek(i)
			frame = img.convert("RGBA")
			frame.save(curr_name)

	log.Must('')





#--------------------------------------------------#

main()










# End of File