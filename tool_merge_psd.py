'''
Command-Line Tool for merging each layer from multiple PSD into 1 PSD.

TODO Feature to remove transparency on the addon PSD layers if needed
    First check if all 4 corner pixels are equal?

USAGE EXAMPLE:
	cd /Users/Jimmy/20-GitHub/StarTools
	clear; python tool_merge_psd.py --fps 100
	clear; python tool_merge_psd.py
	clear; python tool_merge_psd.py --filepath '/Users/Jimmy/Desktop/Star Iliad Image Dev'
	clear; python tool_merge_psd.py --fps 10 --filepath '/Users/Jimmy/Desktop/Star Iliad Image Dev'

'''
import os
import argparse
from pathlib import Path
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer

#---------------------------------------------------#
# ---------- [Adjustable Configurations] ---------- #

# Extension format & Configurations
EXTENSION = '.psd'
config_do_merge = True       # If False, ends program prematurely without merging/outputting

config_reverse_order = True  # If True, input files are read in reversed alphabetical order instead
# Input folder paths: PSDs are loaded in alphabetical order
#  e.g. From top to bottom: 1 -> 2 -> 3
#   BEFORE1.psd
#   BEFORE2.psd
#   BEFORE3.psd
#config_folder = r'/Users/Jimmy/Desktop/PSD' # Default folder path
config_folder = r'C:\Users\qtran\Desktop\twitter' # Default folder path

# Output PSD at desktop by default
output_folder = os.path.expanduser("~/Desktop") + '/'
output_file   = output_folder + 'AFTER'





#---------------------------------------#
# ---------- [Main Function] ---------- #

def main():
    # Argument parsing in command; Optional
    parser = argparse.ArgumentParser()
    parser.add_argument('--filepath', type=str, default='')
    parser.add_argument('--ms', type=int, default=-1, help = 'Millisecond between frame, default at 100')
    parser.add_argument('--fps', type=int, default=-1, help = 'FPS in animated GIF, default at 10')
    args = parser.parse_args()

    # Read the PSD files
    if args.filepath != '':
        input_folder = args.filepath
    else:
        input_folder = config_folder
    input_psd_filenames, output_psd_filename = ReadPsdFiles(input_folder)

    # This affects only the layer names, which can later be used to change output GIF speed
    millisecond = -1
    if args.ms > 0: millisecond = args.ms
    elif args.fps > 0: millisecond = int(1000 / args.fps)

    # Do the merging, then export the PSD
    if not config_do_merge: return
    new_psd = CreateMergedPSD(input_psd_filenames, millisecond)

    # Save the merged PSD
    print('Saving merged PSD...')
    new_psd.save(output_psd_filename)
    print(f"    {output_psd_filename}")

    print()
    print('DONE!')
    print()





#----------------------------------------#
# ---------- [Read PSD Files] ---------- #

def ReadPsdFiles(filepath = ''):
    # This returns a turple of these 2 things:
    #  - List of filenames of the PSD files
    #  - Filenames of the output PSD file

    # Add the slash at the end of the folder path if needed
    print('Verifying paths...')
    if filepath != '':
        input_folder = filepath
    else:
        input_folder = config_folder
    input_folder = _CheckFolderPath(input_folder)
    print(f'  Folder:')
    print(f'    {input_folder}')

    # Adjust the input/output paths
    # If none is provided, read all PSD in folder
    input_psd_files = []
    output_psd_file = output_file
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
    return input_psd_files, output_psd_file
    

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



#------------------------------------------#
# ---------- [Merge Processing] ---------- #

def CreateMergedPSD(input_psd_files, millisecond):
    # Terminology:
    #  - PSD          from PSDImage.open("a.psd")
    #  - Pixel Image  from psd[i].composite()
    #  - Layer        from PixelLayer.frompil( img, psd, name, opacity )
    print('Begin appending layers...')

    # Load the first PSD file to get dimensions and layers
    merged_psd = PSDImage.open(input_psd_files[0])    # The base PSD to paste other layers onto
    print(f"  Opening {input_psd_files[0]}... (base image)")
    print(f"    PSD Size     : {merged_psd.size}")
    
    # Iterate over each input PSD file
    max_viewport = ( 0, 0, merged_psd.size[0], merged_psd.size[1] )
    img_default = merged_psd[0].composite(viewport=max_viewport)
    for curr_psd in input_psd_files[:]:
        MergeOntoPSD(merged_psd, curr_psd, max_viewport, img_default, millisecond )
    print()
    return merged_psd



def MergeOntoPSD( base_psd, addon_psd, max_viewport, img_default, millisecond ):
        print(f"  Opening {addon_psd}...")
        psd = PSDImage.open(addon_psd)
        new_size = psd.size

        # Check if the width and height of both PSD matches up  
        if new_size[0] != base_psd.size[0] or new_size[1] != base_psd.size[1]:
            print(f'WARNING! Image size mismatch - {new_size}')

        # Loop through each layer of the current PSD
        psd_len = len(psd)
        for i in range(psd_len):
            # If FPS specified, include it in layer name too
            new_layer_name = f'GIF Frame {i+1}'
            if millisecond > 0:
                new_layer_name = f'_a_frm{i},{millisecond}'
#            print(f'    {new_layer_name}')

            # Merge the layers: paste layer 2 over layer 1
            if i < len(base_psd):
                base_img = base_psd[i].composite(viewport=max_viewport) # No need to specify viewport here? Normally base image is supposed to be at max
                print_str = "(merged)"
#                print("Using merged image...")
            else:
                base_img = img_default.copy()
                print_str = "(default)"
#               print("Using default as BG image...")
            print(f"    Layer {i} \"{new_layer_name}\" {print_str}")
            img2 = psd[i].composite(viewport=max_viewport) # This ensures no auto-trimming occurs
            base_img.paste(img2, (0, 0), img2)

            # Make the PSD layer from merged image, then replace the existing one with it
            curr_layer = PixelLayer.frompil(
                base_img,
                base_psd,
                layer_name = new_layer_name,
                opacity = 255, # 0-255
            )

            # Replace layer if index not out of bound, otherwise append to the end
            if i < len(base_psd):
                base_psd[i] = curr_layer
            else:
                base_psd.append(curr_layer)



#----------------------------------#
# ---------- [Template] ---------- #

main()









# End of File