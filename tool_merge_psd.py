'''
Command-Line Tool for merging each layer from multiple PSD into 1 PSD.

NOTE
There is a recurring bug where,
 If the PSD has transparent background, layer is
  automatically resized to trim out all the transparent pixel

USAGE EXAMPLE:
	python tool_merge_psd.py
	clear; python tool_merge_psd.py

'''
import os
import argparse
from pathlib import Path
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

#--------------------------------------------------#
'''Adjustable Configurations'''

# Extension format & Configurations
EXTENSION = '.psd'
config_reverse_order = False # If True, inputs are read in reversed alphabetical order instead
config_do_merge = True       # If False, ends program prematurely without merging/outputting


# Input folder paths: PSDs are loaded in alphabetical order
#  e.g. From top to bottom: 1 -> 2 -> 3
#   BEFORE1.psd
#   BEFORE2.psd
#   BEFORE3.psd
config_folder = r'/Users/Jimmy/Desktop/PSD' # Default folder path


# Output PSD at desktop by default
output_folder = os.path.expanduser("~/Desktop") + '/'
output_file = output_folder + 'AFTER'





#--------------------------------------------------#

def MergePsdLayers(input_psd_files = [], output_psd_file = output_file):

    # Argument parsing in command; Optional
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str, default='')
    parser.add_argument('--ms', type=int, default=-1, help = 'Millisecond between frame, default at 100')
    parser.add_argument('--fps', type=int, default=-1, help = 'FPS in animated GIF, default at 10')
    args = parser.parse_args()

    millisecond = -1
    if args.ms > 0: millisecond = args.ms
    elif args.fps > 0: millisecond = int(1000 / args.fps)

    # Add the slash at the end of the folder path if needed
    print('Verifying paths...')
    if args.filepath != '':
        input_folder = args.filepath
    else:
        input_folder = config_folder
    input_folder = _CheckFolderPath(input_folder)
    print(f'  Folder:')
    print(f'    {input_folder}')

    # Adjust the input/output paths
    # If none is provided, read all PSD in folder
    input_psd_files, output_psd_file = _AdjustFilePaths(input_folder, input_psd_files, output_psd_file)
    input_psd_files.sort() # Sort temp list alphabetically
    if config_reverse_order: input_psd_files.reverse()
    
    # Show the filepaths to user to ensure it's desirable
    print("  Reading input PSD files: (order is top to bottom)")
    for input in input_psd_files:
        print(f'    {input}')
    print("  Outputting PSD file at:")
    print(f'    {output_psd_file}')
    print()


    if not config_do_merge: return
    print('Begin merging layers...')

    # Load the first PSD file to get dimensions and layers
    input_psd_files.reverse() # First in list used as base, then the rest are drawn above them
    base_psd = PSDImage.open(input_psd_files[0])
    num_layers = len(base_psd)
    max_viewport = ( 0, 0, base_psd.size[0], base_psd.size[1] )
    print(f"  Opening {input_psd_files[0]}... (base image)")
    print(f"    Layer Number : {num_layers}")
    print(f"    PSD Size     : {base_psd.size}")
    
    # Create a new PSD with the same dimensions
    # Then iterate over each input PSD file
    merged_psd = base_psd
    for psd_file in input_psd_files[1:]:
        print(f"  Opening {psd_file}...")
        psd = PSDImage.open(psd_file)

        new_num = len(psd)
        if new_num != num_layers: print('WARNING! Layer number mismatch!')
        new_size = psd.size
        if new_size[0] != base_psd.size[0] or new_size[1] != base_psd.size[1]:
            print(f'WARNING! Image size mismatch - {new_size}')

        for i in range(new_num):
            if i > num_layers-1: break # If the above PSD has more layers than base PSD, skip the extra frames

            # Merge the layers: paste layer 2 over layer 1
            img1 = merged_psd[i].composite(viewport=max_viewport) # No need to specify viewport here? Normally base image is supposed to be at max
            img2 = psd[i].composite(viewport=max_viewport) # This ensures no auto-trimming occurs
            img1.paste(img2, (0, 0), img2)

            # If FPS specified, include it in layer name too
            new_layer_name = f'GIF Frame {i+1}'
            if millisecond > 0:
                new_layer_name = f'_a_frm{i},{millisecond}'

            # Make the PSD layer from merged image, then replace the existing one with it
            curr_layer = PixelLayer.frompil(
                img1,
                merged_psd,
                layer_name=new_layer_name,
                opacity=255, # 0-255
            )
            merged_psd[i] = curr_layer
    print()

    # Save the merged PSD
    print('Saving merged PSD...')
    merged_psd.save(output_psd_file)
    print(f"    {output_psd_file}")

    print()
    print('DONE!')
    print()





def _CheckFolderPath(filepath):
    '''Return the folder path after ensuring the end char is slash, print a warning if it could be invalid'''
    ending_char = filepath[-1]
    if (ending_char != '/') and (ending_char in filepath):
        filepath += '/'
    elif (ending_char != '\\') and (ending_char in filepath):
        filepath += '\\'
    else:
        print(f'WARNING! Folder path {filepath} might not be valid!')
    return filepath


def _AdjustFilePaths(input_folder, input_psd_files, output_psd_file):
    '''
     If no input specified,
       read through the input folder (default behavior)
     Otherwise,
       use the specified PSD as is
    '''
    temp_list = []
    if input_psd_files == []: # No input file names specified
        for entry in os.listdir(input_folder):
            if Path(entry).suffix != EXTENSION: continue    # Ignore if is not PSD
            full_path = os.path.join(input_folder, entry)
            if os.path.isfile(full_path):
                temp_list.append(full_path)
#        temp_list.sort() # Sort temp list alphabetically
    else:
        for name in input_psd_files:
            temp_list.append(input_folder + name + EXTENSION)
    input_psd_files = temp_list

    # Fix output path - Add extension ().psd) at the end of file
#    output_psd_file = input_folder + output_psd_file + EXTENSION
    if not EXTENSION in output_psd_file: output_psd_file += EXTENSION
    
    return input_psd_files, output_psd_file





#--------------------------------------------------#

# merge_psd_layers(input_files, output_file)
MergePsdLayers()










# End of File