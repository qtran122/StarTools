'''
Command-Line Tool for upscaling (or downscaling) all images in the input folder in a batch.
There is NO anti-aliasing applied.

Enter 2 values to specify HORIZONTAL and VERTICAL multiplier.
But if only 1 value is provided, it's applied to both height and width.


USAGE EXAMPLE:
	python tool_image_upscale.py 5
	python tool_image_upscale.py 9.5 5

'''
import argparse
import os
import sys
import logic.common.file_utils as file_utils
from PIL import Image


#--------------------------------------------------#
'''Variables'''

folder_i = 'image/'
folder_o = 'image_upscaled/'



#--------------------------------------------------#
'''Main'''

def main():
	# Return if no multiplier is provided in command
	if len(sys.argv) < 2:
		print("Usage: python upscale_images.py <multiplier> [multiplier2]")
		sys.exit(1)


	# Fetch multipler from argument
	multi_x = float(sys.argv[1])
	if len(sys.argv) == 2:
		multi_y = multi_x
	else: 	multi_y = float(sys.argv[2])
	print(f'  Applying multipler to images : {multi_x} x {multi_y}')


	# Filepath
	input_folder  = file_utils.GetInputFolder() + folder_i
	output_folder = file_utils.GetInputFolder() + folder_o


	# Scan folder for only image files, then output all images after processed
	for file_name in os.listdir(input_folder):
		if not file_name.lower().endswith(('.jpg', '.jpeg', '.png')): continue

		file_path_i = os.path.join(input_folder, file_name)
		img_i = Image.open(file_path_i)
		input_w, input_h = img_i.size 

		file_path_o = os.path.join(output_folder, file_name)
		output_w = int( input_w * multi_x )
		output_h = int( input_h * multi_y )
		
		img_o = img_i.resize( (output_w, output_h), resample=Image.BOX )
		img_o.save( file_path_o )
		print( f'    {file_name}: {output_w} x {output_h}' )

	print("~~End of All Procedures~~")





#--------------------------------------------------#

main()










# End of File