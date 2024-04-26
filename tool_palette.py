'''
Standalone tool that will palette swap all PNGs in select folders.

This tool is underbaked and without much QoL since its use case is very narrow. It targets sprites
we want palette swapped and where we don't want to use the in-engine shaders to achieve that 
(For example, the goo slime is too simple for advance shaders, but has a poison variant)

SETUP EXAMPLE:
    Inside the tools/palette_swap folder, you will find pngs. Place all your PNGs to be palette
    swapped in this folder (using sub-folders is fine, they will be traversed). Next, open the
    "palette.png" file. And edit it to create a palette swap mapping of color A to color B to
    be applied to all sprites. This palette png should contain 2 mirrored images, where the
    image on the right is recolored. Now run "python tool_palette.py" and that's it!
    
USAGE EXAMPLE:
	python tool_palette.py
'''

import os
from PIL import Image, ImageColor


# FOLDER LOCATIONS to be targeted. Feel free to edit!
INPUT_FOLDER = "tools\palette_swap"
OUTPUT_FOLDER = "tools\palette_swap" # typically, we overwrite in place
PALETTE_PATH = "tools\palette_swap\palette.png"



def swap_colors(image, palette_swap_dict):
    image = image.convert("RGBA")
    data = image.getdata()
    new_data = []

    for item in data:
        r, g, b, a = item[:4]
        rgba = (r, g, b, a)
        hex_color = "#{:02x}{:02x}{:02x}".format(r, g, b)
        if hex_color in palette_swap_dict:
            new_rgba = ImageColor.getcolor(palette_swap_dict[hex_color], "RGB")
            new_data.append((*new_rgba, a))
        else:
            new_data.append(rgba)

    image.putdata(new_data)
    return image



def CreatePaletteSwapDict(image_path):
    image = Image.open(image_path)
    width, height = image.size
    half_width = width // 2

    left_half = image.crop((0, 0, half_width, height))
    right_half = image.crop((half_width, 0, width, height))

    left_pixels = left_half.getdata()
    right_pixels = right_half.getdata()

    palette_swap_dict = {}

    for left_pixel, right_pixel in zip(left_pixels, right_pixels):
        left_color = "#{:02x}{:02x}{:02x}".format(*left_pixel[:3])
        right_color = "#{:02x}{:02x}{:02x}".format(*right_pixel[:3])

        if left_color not in palette_swap_dict:
            palette_swap_dict[left_color] = right_color

    return palette_swap_dict
    
    
    
def PaletteSwapFolder(input_folder, output_folder, palette_swap_dict):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for root, dirs, files in os.walk(input_folder):
        for filename in files:
            if filename.startswith('palette'): continue
            if filename.endswith(".png"):
                input_path = os.path.join(root, filename)
                output_path = os.path.join(output_folder, os.path.relpath(input_path, input_folder))

                image = Image.open(input_path)
                image = swap_colors(image, palette_swap_dict)
                output_folder_path = os.path.dirname(output_path)
                if not os.path.exists(output_folder_path):
                    os.makedirs(output_folder_path)
                print(f"  processed... {output_path}")
                image.save(output_path)



if __name__ == "__main__":
    palette_swap_dict = CreatePaletteSwapDict(PALETTE_PATH)
    print("Palette Swap Dictionary:")
    print(palette_swap_dict)
    PaletteSwapFolder(INPUT_FOLDER, OUTPUT_FOLDER, palette_swap_dict)
