import os
import re
from PIL import Image

# Take FOLDER and make it a GIF

# User-configurable fields
INPUT_FOLDER = r"C:\Users\qtran\Desktop\XX"  # Replace with your folder path
FRAME_DURATION = 70  # Duration of each frame in milliseconds

def extract_number(filename):
    """Extract the number from filenames like (1).png, (2).png, etc."""
    match = re.search(r'\((\d+)\)\.png$', filename, re.IGNORECASE)
    return int(match.group(1)) if match else float('inf')

def create_animated_gif(input_folder, frame_duration):
    # Get list of PNG files
    png_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.png')]
    
    # Sort files numerically based on the number in parentheses
    png_files.sort(key=extract_number)
    
    if not png_files:
        print("No PNG files found in the specified folder.")
        return
    
    # Load and process images
    images = []
    for png_file in png_files:
        file_path = os.path.join(input_folder, png_file)
        try:
            img = Image.open(file_path).convert('RGBA')
            # Create a new transparent background for each frame
            new_img = Image.new('RGBA', img.size, (0, 0, 0, 0))
            new_img.paste(img, (0, 0), img)
            images.append(new_img)
        except Exception as e:
            print(f"Error loading {png_file}: {e}")
            continue
    
    if not images:
        print("No valid images could be loaded.")
        return
    
    # Set output to Desktop
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    output_file = os.path.join(desktop_path, "animated.gif")
    
    # Ensure Desktop directory exists
    if not os.path.exists(desktop_path):
        print(f"Desktop directory not found: {desktop_path}")
        return
    
    # Save animated GIF with proper transparency handling
    try:
        images[0].save(
            output_file,
            save_all=True,
            append_images=images[1:],
            duration=frame_duration,
            loop=0,  # 0 means loop forever
            optimize=True,
            transparency=0,
            disposal=2  # Dispose of previous frame before displaying next
        )
        print(f"Animated GIF created successfully: {output_file}")
    except Exception as e:
        print(f"Error creating GIF: {e}")

if __name__ == "__main__":
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Invalid folder path: {INPUT_FOLDER}")
    else:
        create_animated_gif(INPUT_FOLDER, FRAME_DURATION)