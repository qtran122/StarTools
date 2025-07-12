import os
from PIL import Image
import numpy as np

# User-editable fields
FOLDER_PATH = r"C:\Users\qtran\Desktop\PROJECT Whale Nebula\TexturePacking\SyncedFolder(Chars)\blythe\defeat\carry_loop"  # Specify the path to the folder containing PNG files
COLORS_TO_REMOVE = ["#ff9ea5", "#fff297", "#cc627b", "#f8b561", "#78424b", "#673472", "#058a88", "#0b6277", "#652e3f"]  # List of hex colors to remove (e.g., red, green, blue)

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def process_image(image, colors_to_remove_rgb):
    """Process a PIL Image to remove specified colors."""
    # Convert to RGBA if not already
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    # Convert image to numpy array
    data = np.array(image)
    
    # Process pixels
    for color in colors_to_remove_rgb:
        # Create mask for pixels matching the color (ignoring alpha)
        mask = np.all(data[:, :, :3] == color, axis=2)
        # Set alpha to 0 for matching pixels to make them transparent
        data[mask, 3] = 0
    
    # Convert back to PIL Image
    return Image.fromarray(data, mode='RGBA')

def main():
    # Validate folder path
    if not os.path.isdir(FOLDER_PATH):
        print(f"Error: Folder not found at {FOLDER_PATH}")
        return

    # Convert hex colors to RGB
    colors_to_remove_rgb = [hex_to_rgb(color) for color in COLORS_TO_REMOVE]

    # Get list of PNG files
    png_files = [f for f in os.listdir(FOLDER_PATH) if f.lower().endswith('.png')]
    if not png_files:
        print(f"No PNG files found in {FOLDER_PATH}")
        return

    # Create output folder
    output_folder = os.path.join(FOLDER_PATH, "processed")
    os.makedirs(output_folder, exist_ok=True)

    # Process each PNG file
    for file_name in png_files:
        input_path = os.path.join(FOLDER_PATH, file_name)
        output_path = os.path.join(output_folder, file_name)
        
        try:
            # Open PNG file
            image = Image.open(input_path)
            
            # Process image
            processed_image = process_image(image, colors_to_remove_rgb)
            
            # Save processed image
            processed_image.save(output_path, 'PNG')
            print(f"Processed: {file_name} -> {output_path}")
            
        except Exception as e:
            print(f"Error processing {file_name}: {e}")

    print(f"Processing complete. Modified PNGs saved in {output_folder}")

if __name__ == "__main__":
    main()