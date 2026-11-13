'''
Command-Line Tool for comparing 2 tilesheets
 - The difference in pixels, as well as affected tiles, are highlight in a separate image
 - The highlight image is automatically opened with the user-specified viewing app
 - The highlight image is temporarily created at the tool folder, and automatically deleted afterwards

USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python tool_tiles_update.py

'''
import argparse
import logic.common.log_utils as log
import logic.common.file_utils as file_utils

import os
import shutil
import subprocess
import numpy as np
from PIL import Image, ImageChops, ImageDraw

#---------------------------------------------------------------------#
#-------------------- [Adjustable Configurations] --------------------#

# File names
file_name = "tiles.png"
filepath_diff_highlight = file_utils.GetInputFolder() + "tiles_highlights_DELETE.png" # This file rests in the input folder

# User-based filepaths & app of choice
curr_user = "Quang"    # Change this when running on a different computer
config_user = {}
config_user["TY"] = {
	"app_path":        "Preview",
	"folder_download": "/Users/Jimmy/Desktop",
	"folder_current":  "/Users/Jimmy/Documents/10 Star Iliad tasks/00-Tiling/10-workspace",
}
config_user["Quang"] = {
	"app_path":        r"C:\Program Files\ImageGlass\ImageGlass.exe",
	"folder_download": r"E:\Downloads",
	"folder_current":  r"C:\Users\qtran\Desktop\PROJECT Whale Nebula\StarIliad\Assets\Graphics",
}

# Color of the pixels in the output hignlight tilesheet
hex_base  = '#000000' # Base color of the sheet
hex_tile  = '#FF0000' # Base color of the tile altered
hex_pixel = '#00FFFF' # Color of all the changed pixels

# Configuraitons
config_check_0_alpha_same = True    # If true, treat color same if alpha values are 0, even if RGB values differ
config_ignore_transparent = True    # If true, will not highlight transparent pixels as "changed"





#------------------------------------------------#
#-------------------- [Main] --------------------#

arg_description = 'Compare 2 tilesheets in the designated filepaths'
arg_help2 = 'Controls the amount of information displayed to screen. 0 = nearly silent, 2 = verbose'



def main():
	# Use argparse to get the filename & other optional arguments from the command line
	parser = argparse.ArgumentParser(description = arg_description)
	parser.add_argument('--v', type=int, choices=[0, 1, 2], default=1, help = arg_help2)
	args = parser.parse_args()
	log.SetVerbosityLevel(args.v)

	# Identify the paths automatically based on user's system
	curr_user_config = config_user[curr_user]
	app_path        = curr_user_config["app_path"]
	folder_download = file_utils.FixFolderPath(curr_user_config["folder_download"])
	folder_current  = file_utils.FixFolderPath(curr_user_config["folder_current"])
	img_path_dl = folder_download + file_name
	img_path_pj = folder_current  + file_name

    # Error-check in case file does not exist
#	if not os.path.exists(app_path):    log.Must(f"[ERROR] Image-viewing app not found at {app_path}"); return
	if not os.path.exists(img_path_dl): log.Must(f"[ERROR] Downloaded Tilesheet PNG not found at {img_path_dl}"); return
	if not os.path.exists(img_path_pj): log.Must(f"[ERROR] In-Project Tilesheet PNG not found at {img_path_pj}"); return

	# Step 1 - Check diff, then output the diff PNG
	log.Must(f"  Checking the new tilesheet:\n    {img_path_dl}\n  with the existing one:\n    {img_path_pj}")
	compare_images(img_path_dl, img_path_pj, filepath_diff_highlight)
	log.Must("")
	log.Must(f"  Difference highlight temporarily created at:\n   {filepath_diff_highlight}")
	log.Must("")

	# Optional
	is_match = images_are_identical(img_path_dl, img_path_pj)
	if is_match: log.Must("  The 2 tilesheets are identical. Exiting tool now...\n"); os.remove(filepath_diff_highlight); return

	# Step 2 - Open image automatically
	try:
		if curr_user == "TY": subprocess.run(["open", "-a", app_path, filepath_diff_highlight])
		else:                 subprocess.Popen([app_path, filepath_diff_highlight])
	except Exception as e:
		log.Must(f"Failed to open image:\n  {e}")

	# Step 3 - Ask user to confirm changes
	user_input = input(f"  Copy tilesheet to new location? (Y/N) ")
	if user_input[0].lower() != 'y':
		log.Must("\n  No changes applied.\n"); os.remove(filepath_diff_highlight); return
	else:
		log.Must("");                          os.remove(filepath_diff_highlight)

	# Step 4 - Copy tilesheet to new location
	shutil.copy(img_path_dl, img_path_pj)
	log.Must("  Tilesheet overwritten.")
	log.Must("")





#-------------------------------------------------#
#-------------------- [Logic] --------------------#

def compare_images(image1_path, image2_path, output_path, grid_size=16):
	'''Read the PNG in the 2 filepaths, then create a new PNG that highlights the difference'''
	with Image.open(image1_path) as image1, Image.open(image2_path) as image2:
		if image1.size != image2.size:
			raise ValueError(
				f"Images must have the same dimensions. "
				f"Got {image1.size} and {image2.size}."
			)

		image1 = image1.convert("RGBA")
		image2 = image2.convert("RGBA")

		difference = ImageChops.difference(image1, image2)

		# Mark a pixel as changed if any RGBA channel differs.
		channels = difference.split()
		mask = channels[0]
		for channel in channels[1:]:
			mask = ImageChops.lighter(mask, channel)
		mask = mask.point(lambda value: 255 if value > 0 else 0)



		# NOTE This snippet is a replacement of the above to account for transparent pixel
		# Differences in RGB, ignoring alpha for the moment
		if config_check_0_alpha_same:
			rgb_mask = channels[0]
			for channel in channels[1:3]:
				rgb_mask = ImageChops.lighter(rgb_mask, channel)
			rgb_mask = rgb_mask.point(lambda value: 255 if value > 0 else 0)

			# Differences in alpha still count
			alpha_mask = channels[3].point(lambda value: 255 if value > 0 else 0)

			# Find pixels that are transparent in both images
			transparent1 = image1.getchannel("A").point( lambda alpha: 255 if alpha == 0 else 0 )
			transparent2 = image2.getchannel("A").point( lambda alpha: 255 if alpha == 0 else 0 )
			both_transparent = ImageChops.darker(transparent1, transparent2)

			# Ignore RGB differences for pixels transparent in both images
			visible_mask = ImageChops.invert(both_transparent)
			rgb_mask = ImageChops.multiply(rgb_mask, visible_mask)

			# A pixel differs if its visible RGB differs or its alpha differs
			mask = ImageChops.lighter(rgb_mask, alpha_mask)



		if config_ignore_transparent:
			# Mark a pixel if any RGBA channel differs
			channels = difference.split()
			diff_mask = channels[0]
			for channel in channels[1:]:
				diff_mask = ImageChops.lighter(diff_mask, channel)

			diff_mask = diff_mask.point(lambda value: 255 if value > 0 else 0)

			# Keep only pixels that are nontransparent in BOTH images
			visible1 = image1.getchannel("A").point(
				lambda alpha: 255 if alpha > 0 else 0
			)
			visible2 = image2.getchannel("A").point(
				lambda alpha: 255 if alpha > 0 else 0
			)
			both_visible = ImageChops.darker(visible1, visible2)

			# Final mask: different and visible in both images
			mask = ImageChops.multiply(diff_mask, both_visible)





		width, height = image1.size
		output = Image.new("RGB", image1.size, hex_base)
		draw = ImageDraw.Draw(output)

		# Color each grid cell blue if it contains at least one changed pixel.
		for y in range(0, height, grid_size):
			for x in range(0, width, grid_size):
				right = min(x + grid_size, width)
				bottom = min(y + grid_size, height)

				cell_mask = mask.crop((x, y, right, bottom))
				if cell_mask.getbbox() is not None:
					draw.rectangle(
						(x, y, right - 1, bottom - 1),
						fill=hex_tile
					)

		# Paint the differing pixels red on top of the blue cells.
		red = Image.new("RGB", image1.size, hex_pixel)
		output.paste(red, mask=mask)

		output.save(output_path)
#		print(f"Difference image saved to: {output_path}")

def images_are_identical(img1_path, img2_path):
	'''Returns True / False depending on whether the 2 images are identical'''
	with Image.open(img1_path) as img1, Image.open(img2_path) as img2:
		# Convert images to NumPy arrays
		arr1 = np.array(img1)
		arr2 = np.array(img2)
		
		# Check if the arrays are strictly identical in shape and pixel values
		return np.array_equal(arr1, arr2)





#--------------------------------------------------#

main()










# End of File