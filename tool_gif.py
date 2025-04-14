from PIL import Image
import os

# This script operates on a folder of PNG files and transforms them into a GIF.

# This was created to revert the effects of Texture Packer. We would take a gif and
# break it into a folder of PNGs for TexturePacker to compile into one big spritesheet.
# Overtime, there was a need to go in the reverse direction, hence this tool.

# Replace INPUT_FOLDER with the address of the PNGs folder
INPUT_FOLDER = r"C:\Users\qtran\Desktop\PROJECT Whale Nebula\TexturePacking\SyncedFolder(Chars)\blythe\idle"
FRAME_DURATION = 80 # Duration per frame in milliseconds (lower = faster)

# Automatically generate OUTPUT_GIF (desktop path with folder name)
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
folder_name = os.path.basename(INPUT_FOLDER)
OUTPUT_GIF = os.path.join(desktop, f"{folder_name}.gif")

def create_gif(input_folder, output_gif, duration):
    """
    Create an animated GIF from PNG files in a folder, preserving transparency.
    
    Args:
        input_folder (str): Path to folder containing PNG files
        output_gif (str): Path for output GIF file
        duration (int): Duration per frame in milliseconds
    """
    # Get list of PNG files
    files = [f for f in os.listdir(input_folder) if f.endswith('.png')]
    
    # Sort files numerically based on the number in parentheses
    files.sort(key=lambda x: int(x.strip('().png')))
    
    # Open images
    images = []
    for file in files:
        file_path = os.path.join(input_folder, file)
        img = Image.open(file_path)
        # Ensure image is in RGBA mode to preserve transparency
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        images.append(img)
    
    if not images:
        print("No PNG files found in the folder!")
        return
    
    # Save GIF with transparency
    images[0].save(
        output_gif,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,  # 0 means loop forever
        transparency=0,
        disposal=2  # Maintain transparency between frames
    )
    print(f"GIF created successfully: {output_gif}")

# Run the script
if __name__ == "__main__":
    create_gif(INPUT_FOLDER, OUTPUT_GIF, FRAME_DURATION)