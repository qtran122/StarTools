import os
from PIL import Image
from PIL import ImageOps
import argparse

# Specify the target folder here
TARGET_FOLDER = r"C:\Users\qtran\Desktop\PROJECT Whale Nebula\TexturePacking\SyncedFolder(Enemy1)\en\leech_morph"  # Replace with your folder path

def invert_png_colors(folder_path):
    """
    Recursively find and invert colors of all PNG files in the specified folder.
    Overwrites original files with inverted versions, preserving transparency.
    """
    # Walk through the folder recursively
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith('.png'):
                try:
                    # Construct full file path
                    file_path = os.path.join(root, filename)
                    
                    # Open the image
                    with Image.open(file_path) as img:
                        # Convert to RGBA to preserve transparency
                        if img.mode != 'RGBA':
                            img = img.convert('RGBA')
                        
                        # Split the image into RGB and alpha channels
                        r, g, b, alpha = img.split()
                        
                        # Invert only the RGB channels
                        rgb_img = Image.merge('RGB', (r, g, b))
                        inverted_rgb = ImageOps.invert(rgb_img)
                        
                        # Merge back with the original alpha channel
                        inverted_r, inverted_g, inverted_b = inverted_rgb.split()
                        inverted_img = Image.merge('RGBA', (inverted_r, inverted_g, inverted_b, alpha))
                        
                        # Overwrite the original file
                        inverted_img.save(file_path, 'PNG')
                        print(f"Processed and overwritten: {file_path}")
                
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Invert colors of PNG files in a folder recursively, overwriting originals")
    parser.add_argument(
        '--folder',
        type=str,
        default=TARGET_FOLDER,
        help="Path to the folder containing PNG files"
    )
    
    args = parser.parse_args()
    
    # Verify folder exists
    if not os.path.isdir(args.folder):
        print(f"Error: Directory '{args.folder}' does not exist")
        return
    
    print(f"Processing PNG files in: {args.folder}")
    invert_png_colors(args.folder)
    print("Color inversion complete!")

if __name__ == "__main__":
    main()