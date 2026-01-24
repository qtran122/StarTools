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
from psd_tools import PSDImage
from psd_tools.api.layers import PixelLayer
from PIL import ImageDraw

#--------------------------------------------------#
'''Adjustable Configurations'''

# File paths
EXTENSION = '.psd'

# Your input PSD files
input_folder = '/Users/Jimmy/20-GitHub/StarTools/input/' # Default folder path
input_files = [
    'BEFORE1', 
    'BEFORE2', 
    'BEFORE3'
]
# From top to bottom: 1 -> 2 -> 3

# Desired output file name
output_folder = input_folder
output_file = 'AFTER'

# Configurations
config_reverse_order = True




#--------------------------------------------------#

def merge_psd_layers(input_psd_files, output_psd_file):
    temp_list = []
    for name in input_psd_files:
        temp_list.append(input_folder + name + EXTENSION)
    input_psd_files = temp_list
    output_psd_file = output_folder + output_psd_file + EXTENSION

    # Configurations
    if config_reverse_order: input_psd_files.reverse()
#    print(input_psd_files)
#    print(output_psd_file)
#    return

    # Load the first PSD file to get dimensions and layers
    base_psd = PSDImage.open(input_psd_files[0])
    num_layers = len(base_psd)
    print(f"Layer Number : {num_layers}")
    
    # Create a new PSD with the same dimensions
#    merged_psd = PSDImage.new(mode='RGB', size=base_psd.size)
    merged_psd = base_psd

    # Iterate over each input PSD file
    for psd_file in input_psd_files[1:]:
        print(f"Opening {psd_file}...")
        psd = PSDImage.open(psd_file)

        new_num = len(psd)
        if new_num != num_layers: print('WARNING! Layer number mismatch!')

        for i in range(new_num):
            # Merge the layers: paste layer 2 over layer 1
            img1 = merged_psd[i].composite()
            img2 = psd[i].composite()

            # If the PSD has transparent background, layer is automatically resized to trim out all the transparent pixel
            # This is bad and not desirable... TODO find a way to deal with this
            x,y = _find_top_left_in_psd(psd[i]) # This didn't work... orz
            print(f"{psd[i].size} - {img2.size} - {x, y}")
            x,y = 0,0
            img1.paste(img2, (x, y), img2)

            # Make the PixelLayer
            curr_layer = PixelLayer.frompil(
                img1,
                merged_psd,
                layer_name=f"Image Layer {i}",
                opacity=255, # 0-255
            )
            merged_psd[i] = curr_layer

#            img2 = psd[-1].composite()
#            print(output_psd_file)
#            img2.save(output_psd_file, 'PNG')
#            return

        '''        
                print(output_psd_file)
                img1.save(output_psd_file, 'PNG')
                return

                merged_psd.append( PixelLayer.frompil(
                    img1,
                    merged_psd,
                    layer_name=f"Image Layer {i}",
                    left=0,
                    top=0,
                    compression=Compression.RLE # RLE compression is efficient for PSDs
                ) )
        '''

    # Save the merged PSD
    merged_psd.save(output_psd_file)
    print(f"Merged PSD saved as: {output_psd_file}")





#--------------------------------------------------#

def _find_top_left(img):
    # Open image and convert to RGBA to ensure alpha channel exists
    width, height = img.size
    
    # Iterate top-to-bottom, then left-to-right
    for y in range(height):
        for x in range(width):
            # getpixel returns (R, G, B, A)
            pixel = img.getpixel((x, y))
            # Check if Alpha channel > 0
            if pixel[3] > 0:
                return (x, y) # Return first match
    return (0, 0) # No non-transparent pixel found

def _find_top_left_in_psd(psd_layer):
    # Convert to PIL Image (RGBA)
    pil_image = psd_layer.composite()
    width, height = pil_image.size
    pixels = pil_image.load()

    # Iterate through rows then columns
    for y in range(height):
        for x in range(width):
            # Check alpha channel
            if pixels[x, y][3] > 0:
                return (x, y) # Return first found
    return (0, 0)

#--------------------------------------------------#

merge_psd_layers(input_files, output_file)










# End of File