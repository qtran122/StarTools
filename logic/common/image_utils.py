'''A convenience module for image operations'''

import math
import webbrowser
import numpy as np

from PIL import Image, ImageDraw, ImageFont



def SliceTileSheet(png_image_path, make_into_np_array = False, tile_size = 16):
    '''Slice a tilesheet png into tiles and return them as a list of images or NP.Arrays.'''
    
    # np.arrays provide fast, flexible, and efficient ways to store and manipulate large datasets
    with Image.open(png_image_path) as img:
        img_tiles = []
        for y in range(0, img.height, tile_size):
            for x in range(0, img.width, tile_size):
                tile = img.crop((x, y, x + tile_size, y + tile_size))
                if make_into_np_array : img_tiles.append(np.array(tile))
                else : img_tiles.append(tile)
        return img_tiles



def NpArrayToImage(np_array):
    return Image.fromarray(np_array, 'RGBA')



def AddHeaderToImage(image, title):
    header_height = 32
    
    # Create a new image for the header with the same width as the original and a black background
    header = Image.new('RGBA', (image.width, header_height), 'black')
    
    # Create a drawing context for the header
    draw = ImageDraw.Draw(header)
   
    # Calculate the position to center the text in the header
    text_x = (header.width - draw.textlength(title)) // 2
    text_y = (header_height - (draw.textbbox((0, 0), title)[3] - draw.textbbox((0, 0), title)[1])) // 2
    
    # Draw the title text onto the header
    draw.text((text_x, text_y), title, fill="white")
    
    # Create a new image with extra space for the header + original image size
    new_image = Image.new('RGBA', (image.width, image.height + header_height))
    
    # Paste the header and the original image onto the new image
    new_image.paste(header, (0, 0))  # Paste header at the top
    new_image.paste(image, (0, header_height), mask=image)  # Paste the original image below the header
    
    return new_image



def CreateTilesCollage(image_title, tiles_n_images, output_path, open_on_complete=True):
    '''Given a list of (tile_id, Image) tuples, will create a collage for study & visualization purposes
    
    image_title - the title the final generated image will have
    tiles_n_images - a list of tuples, where each tuple is a pair of (int tile_id, Image objects). 
        Each image is a tile (generally 16x16) cropped from a larger tilesheet
    output_path - where the generated image will be saved
    open_on_complete - if true, opens the image upon its completion for easy viewing
    '''
    tiles_per_row = math.ceil(math.sqrt(len(tiles_n_images)))  # Export unmatched tiles in a square shape
    if tiles_per_row < 4 : tiles_per_row = 4
    tile_size = 16 # 16 pixels wide & tall
    spacing = 16  # 16 pixels between tiles
    text_height = 10  # Space for text below each tile, before scaling
    scale = 2  # Scale factor (it's 2x so we can fit text more neatly)

    # Calculate planned image dimensions by first accounting for spacing and scaled text height
    img_width = tiles_per_row * (tile_size + spacing) - spacing  # Remove last spacing
    img_height = math.ceil(len(tiles_n_images) / tiles_per_row) * (tile_size + spacing)

    # Create an image with transparent slots to fit tiles - black everywhere else
    output_image = _CreateCheckeredCanvas(img_width, img_height, tile_size, tile_size, spacing)
    
    # Loop through tiles_n_images and paste the small images into the larger image
    for index, (tile_id, tile_image) in enumerate(tiles_n_images):
        x = (index % tiles_per_row) * (tile_size + spacing)
        y = (index // tiles_per_row) * (tile_size + spacing)
        output_image.paste(tile_image, (x, y), tile_image)
    
    # After placing tiles, scale the image up in anticipation for text (text needs higher resolution)
    scaled_width = output_image.width * scale
    scaled_height = output_image.height * scale
    scaled_image = output_image.resize((scaled_width, scaled_height), Image.NEAREST)
    draw = ImageDraw.Draw(scaled_image)
    
    # Loop through tiles_n_images again, this time writing their name (tile_id) below them
    dy_between_texts = (tile_size + spacing) * scale # times 2 due to the 1 tile buffer between tiles
    y_start = tile_size * scale + 2 # Adding 2 extra pixels of buffer for niceness
    for index, (tile_id, tile_image) in enumerate(tiles_n_images):
        x = (index % tiles_per_row) * (tile_size + spacing) * scale
        row = (index // tiles_per_row)
        text_y = y_start + row * dy_between_texts # Adjust text placement below the tile at the scaled image
        draw.text((x, text_y), str(tile_id - 1), fill="white") # TILED naming convention subtracts 1 from tile_id
        
    scaled_image = AddHeaderToImage(scaled_image, image_title)
    scaled_image.save(output_path)
    
    if (open_on_complete):
        webbrowser.open(output_path)



def CreateTilesCollage2X(image_title, tiles_n_images_A, tiles_n_images_B, output_path, open_on_complete=True):
    '''Similar to CreateTilesCollage(), except the generated image is tailored to compare 2 equal-lengthed image sets
    
    image_title - the title the final generated image will have
    tiles_n_images_A - a list of tuples, where each tuple is a pair of (int tile_id, Image objects). 
    tiles_n_images_B - a list of tuples, where each tuple is a pair of (int tile_id, Image objects).
    output_path - where the generated image will be saved
    open_on_complete - if true, opens the image upon its completion for easy viewing
    '''
    bindings_per_row = 4
    tile_size = 16 # 16 pixels wide & tall
    spacing_within = 16 # 16 pixels between the old binding and new binding
    spacing_without = 32  # 32 pixels of space between two entirely separate tile_id_bindings
    text_height = 10  # Space for text below each tile, before scaling
    scale = 2  # Scale factor (it's 2x so we can fit text more neatly)
    
    # Calculate planned image dimensions by first accounting for spacing and scaled text height
    img_width = bindings_per_row * (2 * tile_size + spacing_within) + (bindings_per_row - 1) * spacing_without
    num_rows_expected = math.ceil(len(tiles_n_images_A) / bindings_per_row)
    img_height = num_rows_expected * tile_size + (num_rows_expected - 1) * spacing_without
    
    # Create an image with transparent slots to fit tiles - black everywhere else
    output_image = _CreateCheckeredCanvas(img_width, img_height + spacing_within, tile_size * 3, tile_size, spacing_without)
    
    # Loop through tiles_n_images_A and tiles_n_images_B and paste their small images into the larger image
    for index, ((tile_id_A, image_A), (tile_id_B, image_B)) in enumerate(zip(tiles_n_images_A, tiles_n_images_B)):
        offset_each_iteration = 2 * tile_size + spacing_within + spacing_without
        x1 = (index % bindings_per_row) * offset_each_iteration
        x2 = x1 + tile_size + spacing_within
        y = (index // bindings_per_row) * (tile_size + spacing_without)
        output_image.paste(image_A, (x1, y), image_A)
        output_image.paste(image_B, (x2, y), image_B)

    # After placing tiles, scale the image up in anticipation for text (text needs higher resolution)
    scaled_width = output_image.width * scale
    scaled_height = output_image.height * scale
    scaled_image = output_image.resize((scaled_width, scaled_height), Image.NEAREST)
    draw = ImageDraw.Draw(scaled_image)

    # Loop through tile_id_bindings again, this time writing their names (aka TILED tile_id) below them
    dy_between_texts = (tile_size + spacing_without) * scale # times 2 due to the 1 tile buffer between tiles
    y_start = tile_size * scale + 2 # Adding 2 extra pixels of buffer for niceness
    
    for index, ((tile_id_A, image_A), (tile_id_B, image_B)) in enumerate(zip(tiles_n_images_A, tiles_n_images_B)):
        x1 = (index % bindings_per_row) * (2 * tile_size + spacing_within + spacing_without) * scale
        x2 = x1 + (tile_size + spacing_within) * scale
        y = ((index // bindings_per_row) * (tile_size + spacing_without) + tile_size) * scale
        # TILED naming convention subtracts 1 from tile_id
        draw.text((x1, y), str(tile_id_A - 1), fill="white")
        draw.text((x2, y), str(tile_id_B - 1), fill="white")
    
    scaled_image = AddHeaderToImage(scaled_image, image_title)
    scaled_image.save(output_path)
    if (open_on_complete):
        webbrowser.open(output_path)



def _CreateCheckeredCanvas(image_width, image_height, tile_size_x, tile_size_y, stripe_size):
    '''Creates a black image with little rectangular cut outs to slot tile graphics'''
    # Create a transparent image
    image = Image.new('RGBA', (image_width, image_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Draw black horizontal stripes
    for y in range(tile_size_y, image_height, tile_size_y + stripe_size):
        draw.rectangle([0, y, image_width, y + stripe_size - 1], fill=(0, 0, 0, 255))
    
    # Draw black vertical stripes
    for x in range(tile_size_x, image_width, tile_size_x + stripe_size):
        draw.rectangle([x, 0, x + stripe_size - 1, image_height], fill=(0, 0, 0, 255))
    
    return image
    
