from PIL import Image
import os


# Process a GIF and remove the specified BG colors, turning it transparent.
# Made this tool since this is often the format that I receive gifs.

# Variables
colors_to_remove = ["070b17", "071d33"]  # List of colors (hex codes) to remove
pictures_location = r"C:\Users\qtran\Desktop\PROJECT Whale Nebula\TexturePacking\SyncedFolder(Chars)\blythe\helmet"  # Folder path containing PNGs

# Convert hex colors to RGB tuples
colors_to_remove = [tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) for hex_color in colors_to_remove]

def process_image(image_path, colors_to_remove):
    """Processes a single image, removing specified colors and making them transparent."""
    with Image.open(image_path) as img:
        img = img.convert("RGBA")  # Ensure image is in RGBA mode
        pixels = img.load()

        for y in range(img.height):
            for x in range(img.width):
                r, g, b, a = pixels[x, y]
                if (r, g, b) in colors_to_remove:
                    pixels[x, y] = (r, g, b, 0)  # Set alpha to 0 (transparent)

        img.save(image_path)  # Overwrite the original image

# Process all PNG files in the specified folder
for file_name in os.listdir(pictures_location):
    if file_name.lower().endswith(".png"):
        file_path = os.path.join(pictures_location, file_name)
        process_image(file_path, colors_to_remove)

print("Processing complete. Specified colors have been removed from the PNGs.")